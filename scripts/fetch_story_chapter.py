#!/usr/bin/env python3
# coding: utf-8
"""Fetch all source pairs of a translation selection in one command.
Does not modify game files. Verifies the exact reviewed CN/EN Git blob versions.
"""
import argparse, hashlib, json, pathlib, sys
from fetch_story_pair import BASE, get_source, clean_relative
from apply_ru_story import git_blob_sha1


def fetch_all(translation_json, out_dir):
    data=json.loads(pathlib.Path(translation_json).read_text('utf8'))
    root=pathlib.Path(out_dir)
    pending=[]
    for relative, meta in data['files'].items():
        clean_relative(relative)
        # Do not follow symlinks in a pre-existing source folder
        for lang in ('cn','en'):
            dest=root/lang/relative
            if dest.is_symlink(): raise ValueError('Refusing symlink destination: '+str(dest))
            expected=meta[lang+'_git_blob_sha1']
            if dest.exists():
                payload=dest.read_bytes()
                if git_blob_sha1(payload).lower()!=expected.lower():
                    raise ValueError('Existing source file has wrong revision: '+str(dest))
            else:
                url=BASE[lang]+relative
                payload=get_source(url)
                if git_blob_sha1(payload).lower()!=expected.lower():
                    raise ValueError('Source revision mismatch: '+url+'; review required. Nothing written.')
            pending.append((dest,payload))
    # Every source pair is fetched + verified BEFORE writing any file.
    for dest,payload in pending:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(payload)
    return {'scenes':len(data['files']),'sources_checked':len(pending),'output':str(root),'safety':'game files untouched'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--translations',default='story/story_main_selection_ru_v020.json')
    p.add_argument('--output',default='source/story')
    a=p.parse_args()
    print(json.dumps(fetch_all(a.translations,a.output),ensure_ascii=False,indent=2))
