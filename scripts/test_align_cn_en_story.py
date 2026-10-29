#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import importlib.util
import pathlib
import tempfile

ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('align', ROOT/'align_cn_en_story.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def run_tests():
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d)
        cn, en=p/'cn',p/'en'
        (cn/'obt/main').mkdir(parents=True)
        (en/'obt/main').mkdir(parents=True)
        (cn/'obt/main/scene.txt').write_text('[PlayMusic]\n[name="甲"]你好。\n[name="乙"]再见。\n', encoding='utf8')
        (en/'obt/main/scene.txt').write_text('[PlayMusic]\n[name="A"]Hello.\n[name="B"]Bye.\n', encoding='utf8')
        out=p/'review.tsv'
        report=mod.export(cn,en,out)
        assert report['candidate_pairs']==2 and report['files_with_count_mismatch']==0
        rows=list(csv.DictReader(out.open(encoding='utf-8-sig'),delimiter='\t'))
        assert len(rows)==2 and rows[0]['cn_original']=='你好。' and rows[0]['ru_draft']==''
        (en/'obt/main/scene.txt').write_text('[name="A"]Hello.\n',encoding='utf8')
        out2=p/'review_mismatch.tsv'
        report=mod.export(cn,en,out2)
        assert report['candidate_pairs']==0 and report['files_with_count_mismatch']==1
        assert 'MISMATCH_NO_ALIGNMENT' in out2.read_text(encoding='utf-8-sig')
        # Even equal counts cannot establish definitive alignment: review flag is mandatory.
        assert all(r['alignment_status']=='PAIR_BY_ORDER_NEEDS_REVIEW' for r in rows)
    print('PASS: CN/EN conservative alignment; mismatch rejection; no automatic RU injection')

if __name__=='__main__':
    run_tests()
