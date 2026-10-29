# -*- coding: utf-8 -*-
import pathlib,json,csv,re,collections
p=pathlib.Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((p/'data/ui_all_keys_status.tsv').open(encoding='utf8',newline=''),delimiter='\t'))
bykey={r['game_key']:r for r in rows}
ru=json.loads((p/'translations/ui_keyed_all_ru.json').read_text('utf8'))
ph=re.compile(r'\{\d+(?::[^{}]*)?\}'); tag=re.compile(r'</?[^<>]+?>')
def sig(s):return collections.Counter(ph.findall(s)),collections.Counter(tag.findall(s)),s.count('\\n')
assert len(rows)==len(bykey)==2711
assert len(ru)==1994
for key,val in ru.items():
 assert key in bykey and bykey[key]['russian']==val,(key,'mismatch')
 assert sig(bykey[key]['english'])==sig(val),(key,'format mismatch')
for row in rows:
 assert bool(row['russian'])==(row['status']=='translated')
print('PASS:',len(ru),'UI keys; placeholders, tags, line-breaks and status consistent')
