#!/usr/bin/env python3
# coding: utf-8
"""Generate LOCAL review preview of Arknights supported main story stages RU from source scripts.
Never edits game files, verifies source Git blobs and preserves all other lines.
Requires CN/EN same explicit revision as editor-checked translation.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

SPEAKER = re.compile(r'(\[\s*name\s*=\s*)(["\'])(.*?)(\2)(\s*\])', re.I)
INLINE = re.compile(r'\{@[\w]+\}|\{\d+(?:[^{}]*)\}|<[^>]+>')
ALLOWED_PATH = r'obt/main/level_main_(?:00-(?:01_(?:beg|end)|02_(?:beg|end)|04_beg|06_end|07_(?:beg|end)|08_beg|09_end|10_beg|11_end)|01-(?:01_(?:beg|end)|03_(?:beg|end)|04_beg|06_beg|07_(?:beg|end)|08_beg|10_end|12_(?:beg|end))|02-(?:0[1-9]|10)_(?:beg|end))\.txt'
SPEAKER_RU = {
    'Dobermann':'Доберманн', 'Amiya':'Амия', 'Ace':'Эйс', 'Reunion Member':'Боец Воссоединения',
    'Reunion Member A':'Боец Воссоединения А', 'Reunion Member B':'Боец Воссоединения Б',
    'Ursus Guard':'Военный полицейский Урсуса', 'Medic':'Медик',
    'Guard':'Боец', 'Female':'Женщина', 'Male':'Мужчина', 'Child':'Ребёнок',
    'TV Host':'Телеведущий', 'Ursus Captain':'Капитан военной полиции Урсуса',
    '???':'???', '':'', 'Civilian':'Мирный житель', 'Talulah':'Талула', 'W':'W', 'Nearl':'Нирл', 'Faust':'Фауст', 'Ch\'en':'Чэнь', 'Kal\'tsit':'Кальцит', 'Wei Yenwu':'Вэй Яньу', 'PRTS':'PRTS', 'Broadcast':'Оповещение', 'L.G.D. Agent':'Сотрудник городской стражи', 'Infected':'Заражённый', 'Children':'Дети', 'Child':'Ребёнок', 'Misha':'Миша', 'Rioter':'Погромщик', 'Franka':'Франка', 'Liskarm':'Лискарм', 'Exusiai':'Экзия', 'Texas':'Техас', 'Skullshatterer':'Крушитель Черепов', 'Operators':'Оперативники', 'Crownslayer':'Краунслеер', 'Mephisto':'Мефисто',
}

def git_blob_sha1(raw):
    header = f'blob {len(raw)}\0'.encode('ascii')
    return hashlib.sha1(header + raw).hexdigest()


def split_newline(raw):
    if b'\r\n' in raw:
        return b'\r\n'
    return b'\n'


def quoted_tokens(s):
    return sorted(INLINE.findall(s))


def read_validated(path, expected_git_sha1):
    raw=pathlib.Path(path).read_bytes()
    if len(raw)>2*1024*1024:
        raise ValueError(f'Source too large: {path}')
    actual=git_blob_sha1(raw)
    if actual.lower()!=expected_git_sha1.lower():
        raise ValueError(f'Source revision mismatch: {path}\nexpected Git blob {expected_git_sha1}, actual {actual}; DO NOT apply this draft to a different game script.')
    return raw


def dialogues_in_text(raw):
    text=raw.decode('utf-8-sig')
    out=[]
    for n,line in enumerate(text.splitlines(),1):
        m=SPEAKER.search(line)
        if not m:
            continue
        spoken=line[m.end():].strip()
        if spoken and not spoken.startswith('//'):
            out.append((n,m.group(3),spoken))
    return out


def patch_bytes(en_bytes, ru_map, localize_names=True):
    # Return a complete script with ONLY dialogue text and optionally display-speaker labels replaced.
    # Does not alter any other storyboard commands, comments, timings, asset references.
    text=en_bytes.decode('utf-8-sig')
    has_bom=en_bytes.startswith(b'\xef\xbb\xbf')
    eol='\r\n' if b'\r\n' in en_bytes else '\n'
    lines=text.splitlines(keepends=True)
    dialog_count=0
    for index,rawline in enumerate(lines):
        body=rawline.rstrip('\r\n')
        tail=rawline[len(body):]
        m=SPEAKER.search(body)
        if not m:
            continue
        spoken=body[m.end():].strip()
        if not spoken or spoken.startswith('//'):
            continue
        dialog_count+=1
        key=str(dialog_count)
        if key not in ru_map:
            raise ValueError(f'Missing RU dialogue {dialog_count}')
        ru=ru_map[key]
        if not isinstance(ru,str) or not ru.strip() or ('\n' in ru) or ('\t' in ru):
            raise ValueError(f'Invalid RU dialogue {dialog_count}')
        if quoted_tokens(spoken)!=quoted_tokens(ru):
            raise ValueError(f'Markup/variable mismatch at {dialog_count}: {quoted_tokens(spoken)} vs {quoted_tokens(ru)}')
        # retain all leading whitespace that followed original speaker tag; do not parse or modify it.
        after=body[m.end():]
        leading=after[:len(after)-len(after.lstrip())]
        prefix=body[:m.end()]
        if localize_names:
            old=m.group(3)
            if old not in SPEAKER_RU:
                raise ValueError(f'Unmapped speaker name: {old}')
            # Only localize name value inside the [name=""] display instruction.
            prefix=prefix[:m.start(3)]+SPEAKER_RU[old]+prefix[m.end(3):]
        lines[index]=prefix+leading+ru+tail
    if dialog_count!=len(ru_map):
        raise ValueError(f'Dialogue count mismatch EN={dialog_count}, RU={len(ru_map)}')
    new=''.join(lines)
    if '\r\n' in text and new.count('\r\n')!=text.count('\r\n'):
        raise ValueError('CRLF line endings lost')
    return (b'\xef\xbb\xbf' if has_bom else b'')+new.encode('utf-8'),dialog_count


def build(source_root, out_root, translations, localize_names=True):
    source_root=pathlib.Path(source_root)
    out_root=pathlib.Path(out_root)
    if (out_root.resolve()==source_root.resolve() or source_root.resolve() in out_root.resolve().parents):
        raise ValueError('Output must be outside source tree; no modification of source files permitted')
    doc=json.loads(pathlib.Path(translations).read_text('utf-8'))
    report={'version':doc.get('version'), 'files':[], 'lines_total':0, 'warnings':[]}
    # validate ALL sources + patch in memory before creating output files
    files=[]
    for rel,config in doc['files'].items():
        if not re.fullmatch(ALLOWED_PATH,rel):
            raise ValueError('Unexpected or unsafe story file path')
        en=read_validated(source_root/'en'/rel,config['en_git_blob_sha1'])
        cn=read_validated(source_root/'cn'/rel,config['cn_git_blob_sha1'])
        if len(dialogues_in_text(cn))!=len(dialogues_in_text(en)):
            raise ValueError(f'Source alignment count mismatch {rel}')
        if len(dialogues_in_text(cn))!=config['dialogue_count']:
            raise ValueError(f'Source dialogue count mismatch {rel}')
        if len(config['dialogues'])!=config['dialogue_count']:
            raise ValueError(f'RU dictionary count mismatch {rel}')
        target,count=patch_bytes(en,config['dialogues'],localize_names)
        # reject accidental modification of control commands and non-dialogue lines
        orig=en.decode('utf-8-sig').splitlines()
        patched=target.decode('utf-8-sig').splitlines()
        if len(orig)!=len(patched):
            raise ValueError(f'Line count changed {rel}')
        for a,b in zip(orig,patched):
            if not SPEAKER.search(a) and a!=b:
                raise ValueError(f'Control line changed: {rel}')
        files.append((rel,target,count,config))
    for rel,data,n,cfg in files:
        dest=out_root/'ru'/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
        report['lines_total']+=n
        report['files'].append({'name':rel,'dialogues_translated':n,'sha256_ru_preview':hashlib.sha256(data).hexdigest(),
                                'source_cn_git_blob_sha1':cfg['cn_git_blob_sha1'],
                                'source_en_git_blob_sha1':cfg['en_git_blob_sha1']})
    report['warnings']=[f"{doc.get('stage', 'Selected story scripts')}: first drafts only; not installed in game.",
        'CN/EN sources are community archives; version and meaning require editorial review.',
        'This script modifies a private local preview, not game files or AssetBundles.']
    (out_root/'ru_preview_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description='Generate version-verified story previews for pinned stage selections; no game patch')
    p.add_argument('--source',default='source/story',help='Directory containing en/obt/... and cn/obt/... source files')
    p.add_argument('--output',default='output/story_ru_preview')
    p.add_argument('--translations',default='story/story_0-1_ru_v014.json')
    p.add_argument('--keep-en-speaker-tags',action='store_true',help='Preserve name tags; translate dialogue only')
    args=p.parse_args()
    print(json.dumps(build(args.source,args.output,args.translations,not args.keep_en_speaker_tags),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
