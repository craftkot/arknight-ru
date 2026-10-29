#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections,csv,json,pathlib,re
root=pathlib.Path(__file__).resolve().parents[1]
a=list(csv.DictReader((root/'data/ui_all_keys_status.tsv').open(encoding='utf8',newline=''),delimiter='\t'))
d=json.loads((root/'translations/ui_keyed_all_ru.json').read_text(encoding='utf8'))
meta=json.loads((root/'reports/QA_v013.json').read_text(encoding='utf8'))
assert len(a)==2711 and len({x['game_key'] for x in a})==len(a)
assert len(d)==meta['ui_total_keyed_drafts']==2544
assert sum(r['status']=='format_unchanged' for r in a)==meta['ui_format_unchanged']==167
ph=re.compile(r'\{\d+(?::[^{}]*)?\}'); tags=re.compile(r'</?[^<>]+?>')
def sig(s):return collections.Counter(ph.findall(s)),collections.Counter(tags.findall(s)),s.count('\\n'),s.count('\n')
for r in a:
 k=r['game_key'];en=r['english'];ru=r['russian']
 if ru:
  assert r['status']=='translated' and k in d and d[k]==ru and sig(en)==sig(ru),k
 else:
  assert r['status']=='format_unchanged' and k not in d,k
print(f'PASS: {len(d)} keyed translations + {len(a)-len(d)} unchanged UI formatting keys; no structural changes')
