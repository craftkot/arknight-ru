# coding: utf-8
import copy,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import apply_ru_event as event
from apply_ru_story import git_blob_sha1
NEW=json.loads((ROOT/'events/darknights_memoir_dm1_after_ru_v028.json').read_text('utf8'))
BOTH=json.loads((ROOT/'events/darknights_memoir_dm1_both_ru_v028.json').read_text('utf8'))
OLD=json.loads((ROOT/'events/darknights_memoir_dm1_before_ru_v026.json').read_text('utf8'))
KEY='activities/act9d0/level_act9d0_01_end.txt'
FIRST='activities/act9d0/level_act9d0_01_beg.txt'
class DM1Post(unittest.TestCase):
 def test_all_167_strings(self):
  s=NEW['files'][KEY]
  self.assertEqual((s['dialogue_count'],s['plain_dialogue_count']),(152,15))
  self.assertEqual(set(s['dialogues']),set(map(str,range(1,153))))
  self.assertEqual(set(s['plain_dialogues']),set(map(str,range(1,16))))
 def test_revision_pins(self):
  s=NEW['files'][KEY]
  self.assertEqual(s['cn_git_blob_sha1'],'9086e7dfb554a06dba354a8313e6c49221eb1e8a')
  self.assertEqual(s['en_git_blob_sha1'],'f292786b0b7cbc11b69712b7ee5e65739e2c2c7f')
 def test_combined_old_unchanged(self):
  self.assertEqual(BOTH['files'][FIRST],OLD['files'][FIRST])
  self.assertEqual(BOTH['files'][KEY],NEW['files'][KEY])
 def test_no_bad_tokens(self):
  s=NEW['files'][KEY]
  for value in list(s['dialogues'].values())+list(s['plain_dialogues'].values()):
   self.assertTrue(value.strip())
   self.assertEqual(event.quoted_tokens(value),[])
   self.assertNotIn('\n',value);self.assertNotIn('\t',value)
 def make_synthetic(self,p):
  s=BOTH['files'][p];n=s['dialogue_count'];q=s['plain_dialogue_count']
  names=['Hoederer','W','Ines'] if p==KEY else ['Ines','Hoederer','Disheveled Sarkaz Woman']
  lines=['[Header(fake=true)]','[playMusic(intro="abc", key="xyz")]', '[Character(name="test")]', '[Blocker(fadetime=2)]']
  lines += ['EN plain '+str(i) for i in range(1,q+1)]
  lines += [f'[name="{names[(i-1)%len(names)]}"]  EN named {i}' for i in range(1,n+1)]
  lines += ['[PlaySound(key="fire")]','[Character]','[Dialog]']
  return ('\r\n'.join(lines)+'\r\n').encode('utf8')
 def test_full_combined_preview_and_safety(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td); spec=copy.deepcopy(BOTH)
   original={}
   for file in spec['files']:
    en=self.make_synthetic(file);cn=en.replace(b'EN named',b'CN named')
    original[file]=en
    for lang,raw in [('en',en),('cn',cn)]:
     p=root/'source'/lang/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
     spec['files'][file][lang+'_git_blob_sha1']=git_blob_sha1(raw)
   cfg=root/'translations.json';cfg.write_text(json.dumps(spec,ensure_ascii=False),'utf8')
   out=event.build(root/'source',root/'preview',cfg)
   self.assertEqual((out['files'],out['named_ru_lines'],out['plain_ru_lines']),(2,246,31))
   for file in spec['files']:
    en=original[file];ru=(root/'preview/ru'/file).read_bytes()
    self.assertEqual(len(en.splitlines()),len(ru.splitlines()))
    for orig,new in zip(en.decode().splitlines(),ru.decode().splitlines()):
     if orig.startswith('[') and not orig.startswith('[name='):
      self.assertEqual(orig,new)
    self.assertEqual((root/'source/en'/file).read_bytes(),en)
   self.assertIn('«Бабель»'.encode('utf8'),(root/'preview/ru'/KEY).read_bytes())
 def test_reject_mismatched_source_before_any_output(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);spec=copy.deepcopy(BOTH)
   for file in spec['files']:
    en=self.make_synthetic(file);cn=en.replace(b'EN named',b'CN named')
    for lang,raw in [('en',en),('cn',cn)]:
     p=root/'source'/lang/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
     spec['files'][file][lang+'_git_blob_sha1']=git_blob_sha1(raw)
   (root/'source/en'/KEY).write_bytes(b'tampered source')
   cfg=root/'t.json';cfg.write_text(json.dumps(spec,ensure_ascii=False),'utf8')
   with self.assertRaisesRegex(ValueError,'revision mismatch'):event.build(root/'source',root/'out',cfg)
   self.assertFalse((root/'out').exists())
 def test_previous_story_and_ui_counts(self):
  main=json.loads((ROOT/'story/story_main_selection_ru_v025.json').read_text('utf8'))
  ui=json.loads((ROOT/'translations/ui_keyed_all_ru.json').read_text('utf8'))
  self.assertEqual(sum(len(x['dialogues']) for x in main['files'].values()),2377)
  self.assertEqual(len(ui),2544)
