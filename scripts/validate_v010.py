# -*- coding: utf-8 -*-
import pathlib,json,csv,collections,re
p=pathlib.Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((p/'data/ui_all_keys_status.tsv').open(encoding='utf8',newline=''),delimiter='\t'))
bykey={x['game_key']:x for x in rows}
ru=json.loads((p/'translations/ui_keyed_all_ru.json').read_text('utf8'))
ph=re.compile(r'\{\d+(?::[^{}]*)?\}')
tag=re.compile(r'</?[^<>]+?>')
def sig(s):return collections.Counter(ph.findall(s)),collections.Counter(tag.findall(s)),s.count('\\n')
assert len(rows)==len(bykey)==2711
for k,val in ru.items():
 assert k in bykey and bykey[k]['russian']==val and sig(bykey[k]['english'])==sig(val),k
print('OK',len(ru),'translated UI keys, tags and placeholders intact')
