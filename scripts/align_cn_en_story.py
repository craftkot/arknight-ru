#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Align privately supplied Arknights CN + EN story scripts, conservatively.
Only [name="..."] visible dialogue lines are parsed. This does not download data.
Match by relative file path, then dialogue ordinal ONLY if line counts agree.
Never claim verified alignment: CN and EN builds can differ in line/speaker order.
"""
import argparse
import csv
import json
import pathlib
import re
import sys

SPEAKER = re.compile(r'\[\s*name\s*=\s*(["\'])(.*?)\1\s*\]', flags=re.I)
MAX_FILE = 16 * 1024 * 1024


def dialogues(path):
    if path.stat().st_size > MAX_FILE:
        raise ValueError(f'File too large for conservative parser: {path}')
    out = []
    text = path.read_text(encoding='utf-8-sig')
    for lineno, line in enumerate(text.splitlines(), 1):
        m = SPEAKER.search(line)
        if not m:
            continue
        spoken = line[m.end():].strip()
        if not spoken or spoken.startswith('//'):
            continue
        out.append(dict(line=lineno, speaker=m.group(2), text=spoken))
    return out


def files(path):
    if path.is_file():
        return {path.name: path}
    if not path.is_dir():
        raise FileNotFoundError(path)
    return {str(p.relative_to(path)).replace('\\', '/'): p for p in sorted(path.rglob('*.txt'))}


def export(cn_root, en_root, output):
    cnfiles, enfiles = files(cn_root), files(en_root)
    common = sorted(cnfiles.keys() & enfiles.keys())
    summary = dict(files_cn=len(cnfiles), files_en=len(enfiles), matched_filenames=len(common), files_with_equal_dialogue_counts=0, files_with_count_mismatch=0, candidate_pairs=0, warning='Pairs by dialogue order are NOT verified or translated; validate scene boundaries and speaker identity manually')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['story_file','dialogue_number','cn_line_number','cn_speaker','cn_original','en_line_number','en_speaker','en_official','ru_draft','alignment_status','review_note'])
        for rel in common:
            cn, en = dialogues(cnfiles[rel]), dialogues(enfiles[rel])
            if len(cn) != len(en):
                summary['files_with_count_mismatch'] += 1
                writer.writerow([rel,'',len(cn),'CN_DIALOGUE_COUNT', '',len(en),'EN_DIALOGUE_COUNT','','','MISMATCH_NO_ALIGNMENT','The number of dialogue lines differs. Manual story segmentation required.'])
                continue
            summary['files_with_equal_dialogue_counts'] += 1
            for idx, (c, e) in enumerate(zip(cn, en),1):
                writer.writerow([rel, idx,c['line'],c['speaker'],c['text'],e['line'],e['speaker'],e['text'],'','PAIR_BY_ORDER_NEEDS_REVIEW','Check speaker, scene/branch and game version; no automatic patching.'])
                summary['candidate_pairs'] += 1
    summary['missing_cn_files'] = sorted(enfiles.keys() - cnfiles.keys())[:100]
    summary['missing_en_files'] = sorted(cnfiles.keys() - enfiles.keys())[:100]
    report = output.with_suffix('.report.json')
    report.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser(description='Create a non-authoritative CN/EN story alignment TSV for human translation.')
    parser.add_argument('--cn', type=pathlib.Path, required=True, help='CN story file or root directory')
    parser.add_argument('--en', type=pathlib.Path, required=True, help='EN story file or root directory')
    parser.add_argument('--out', type=pathlib.Path, required=True, help='Output TSV path')
    args = parser.parse_args()
    result = export(args.cn, args.en, args.out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['matched_filenames']:
        print('WARNING: no matching filenames; check relative directory layout.',file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
