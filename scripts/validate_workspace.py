# -*- coding: utf-8 -*-
import pathlib,csv,json,re,collections,sys
root=pathlib.Path(__file__).resolve().parents[1]
with (root/'data/ui_all_keys_status.tsv').open(encoding='utf-8',newline='') as f: a=list(csv.DictReader(f,delimiter='\t'))
trans=json.loads((root/'translations/ui_keyed_all_ru.json').read_text(encoding='utf-8'))
rows={x['game_key']:x for x in a}
assert len(rows)==len(a)==2711
ph=re.compile(r'\{\d+(?::[^{}]*)?\}');tag=re.compile(r'</?[^<>]+?>')
def sig(s):return sorted(ph.findall(s)),sorted(tag.findall(s)),s.count('\\n')
issues=[]
for k,ru in trans.items():
 if k not in rows:issues.append((k,'missing key'));continue
 if sig(ru)!=sig(rows[k]['english']):issues.append((k,'syntax'))
 if rows[k]['russian']!=ru:issues.append((k,'mismatch'))
assert not issues,issues[:15]
print('OK:',len(trans),'localized game keys, out of',len(rows),'source keys; no syntax errors.')
