#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch a single Arknights CN/EN story pair for PRIVATE translation review.

Uses community mirrors Kengxxiao/ArknightsGameData (CN) and
Kengxxiao/ArknightsGameData_YoStar (EN), no launcher / BepInEx / mod binaries.
Not intended for game patching or automatic story translation.
"""
import argparse
import hashlib
import json
import pathlib
import re
import urllib.request
from datetime import datetime, timezone

MAX_BYTES = 2 * 1024 * 1024
BASE = {
    'cn': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/story/',
    'en': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/main/en_US/gamedata/story/',
}
# Only known story directory paths; prevent arbitrary URL / filesystem traversal.
PATH_RE = re.compile(r'^(?:obt/(?:main|memory|guide)/[a-zA-Z0-9_./-]+|activities/[a-zA-Z0-9_./-]+)\.txt$')


def clean_relative(path):
    path = path.replace('\\', '/')
    pieces = pathlib.PurePosixPath(path).parts
    if not PATH_RE.fullmatch(path) or any(x in {'.', '..', ''} for x in pieces) or path.startswith('/'):
        raise ValueError('Expected a safe game story path, for example obt/main/level_main_00-01_beg.txt')
    return path


def get_source(url, opener=None):
    if opener is None:
        opener = urllib.request.urlopen
    with opener(urllib.request.Request(url, headers={'User-Agent': 'ArkRU-SourceCheck/0.15'}), timeout=25) as response:
        # Do not follow redirects to arbitrary websites.
        final_url = response.geturl()
        if not final_url.startswith('https://raw.githubusercontent.com/'):
            raise ValueError('Unapproved redirect destination')
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Story is bigger than the per-file size limit')
    text = raw.decode('utf-8-sig')
    if '[name=' not in text and '[Name=' not in text:
        raise ValueError('No story dialogue tags found; verify the source file')
    return raw


def download(relative, root, opener=None):
    relative = clean_relative(relative)
    root = pathlib.Path(root)
    results = {}
    # Fetch both successfully before writing either file.
    for lang, base in BASE.items():
        url = base + relative
        data = get_source(url, opener)
        results[lang] = {'url':url,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'data':data}
    written = {}
    for lang, record in results.items():
        path = root/lang/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(record.pop('data'))
        written[lang] = path.as_posix()
    manifest = {'relative_story_path':relative,'fetched_at_utc':datetime.now(timezone.utc).isoformat(),
                'source_type':'community mirrors, not official release',
                'warning':'CN and EN story revisions may not match; compare dialogue ordinals and scene structure before translation',
                'files':results,'local_files':written}
    meta = root/'source_manifest.json'
    if meta.exists():
        old = json.loads(meta.read_text(encoding='utf-8'))
        manifest_list = old.get('pairs', []) if isinstance(old, dict) else []
    else:
        manifest_list=[]
    manifest_list=[rec for rec in manifest_list if rec.get('relative_story_path')!=relative] + [manifest]
    meta.write_text(json.dumps({'pairs':manifest_list},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return manifest


def main():
    ap=argparse.ArgumentParser(description='Download one aligned-source candidate CN + EN (read-only game data)')
    ap.add_argument('relative',help='e.g. obt/main/level_main_00-01_beg.txt')
    ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path('source/story'))
    args=ap.parse_args()
    manifest=download(args.relative,args.out)
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('Next: python scripts/align_cn_en_story.py --cn source/story/cn --en source/story/en --out story_work/review.tsv')

if __name__=='__main__':
    main()
