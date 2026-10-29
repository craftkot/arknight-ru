# -*- coding: utf-8 -*-
"""Compare new English string_map TSV with this workspace; Python 3 standard library."""
import csv,sys,json,pathlib
if len(sys.argv)!=2:
 print("Usage: python compare_game_resource.py newly_extracted_string_map.tsv");sys.exit(2)
root=pathlib.Path(__file__).resolve().parents[1]
with (root/'data/ui_all_keys_status.tsv').open(encoding='utf-8',newline='') as f: old={r['game_key']:r for r in csv.DictReader(f,delimiter='\t')}
with open(sys.argv[1],encoding='utf-8',newline='') as f: new={r['game_key']:r['english'] for r in csv.DictReader(f,delimiter='\t')}
report={
 'new_keys':sorted(set(new)-set(old)),
 'removed_keys':sorted(set(old)-set(new)),
 'changed_english':[{'key':k,'old':old[k]['english'],'new':new[k]} for k in new.keys() & old.keys() if new[k]!=old[k]['english']],
 'still_untranslated':[k for k in new if k in old and old[k]['status']!='translated']
}
out=root/'reports/resource_diff_current.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('New:',len(report['new_keys']),'Removed:',len(report['removed_keys']),'Changed:',len(report['changed_english']),'Untranslated:',len(report['still_untranslated']));print(out)
