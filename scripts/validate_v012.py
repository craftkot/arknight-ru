#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections,csv,json,pathlib,re
root=pathlib.Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'data/ui_all_keys_status.tsv').open(encoding='utf8',newline=''),delimiter='\t'))
ru=json.loads((root/'translations/ui_keyed_all_ru.json').read_text(encoding='utf8'))
assert len(rows)==2711 and len({r['game_key'] for r in rows})==2711
assert len(ru)==2433
ph=re.compile(r'\{\d+(?::[^{}]*)?\}');tag=re.compile(r'</?[^<>]+?>')
def sig(s):return collections.Counter(ph.findall(s)),collections.Counter(tag.findall(s)),s.count('\\n'),s.count('\n')
for row in rows:
 k=row['game_key']
 assert bool(row['russian'])==(row['status']=='translated'),k
 if row['russian']:
  assert ru[k]==row['russian'],k
  assert sig(row['english'])==sig(row['russian']),k
 else:
  assert k not in ru,k
print('PASS:',len(ru),'translations; all placeholders, markup, linebreaks and statuses consistent')
