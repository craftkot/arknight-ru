# coding: utf-8
"""Additive 0-9/0-10 tests, plus synthetic end-to-end preview validation."""
import copy
import json
import pathlib
import re
import tempfile
import unittest
import sys
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import apply_ru_story as engine
R09='obt/main/level_main_00-09_end.txt'
R10='obt/main/level_main_00-10_beg.txt'

class StoryV019(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.new=json.loads((HERE/'story_0-9_0-10_ru_v019.json').read_text('utf8'))
  cls.old=json.loads((HERE/'story_main_selection_ru_v018.json').read_text('utf8'))
  cls.both=json.loads((HERE/'story_main_selection_ru_v019.json').read_text('utf8'))

 def test_two_new_scenes_counts_and_complete_indices(self):
  for filename,n in [(R09,49),(R10,54)]:
   d=self.new['files'][filename]
   self.assertEqual(d['dialogue_count'],n)
   self.assertEqual(set(d['dialogues']),set(str(x) for x in range(1,n+1)))
   for phrase in d['dialogues'].values():
    self.assertIsInstance(phrase,str)
    self.assertTrue(phrase.strip())
    self.assertNotRegex(phrase,r'[\t\n\r]')

 def test_all_491_previous_dialogues_unchanged(self):
  self.assertEqual(self.old['files'],{k:v for k,v in self.both['files'].items() if k in self.old['files']})
  self.assertEqual(len(self.both['files']),11)
  self.assertEqual(sum(x['dialogue_count'] for x in self.both['files'].values()),594)

 def test_pinned_sources_and_CN_dialogue_criteria(self):
  f=self.new['files']
  self.assertEqual(f[R09]['cn_git_blob_sha1'],'dd65e36833754ce119ad7fab7c1abf0ae50a1122')
  self.assertEqual(f[R09]['en_git_blob_sha1'],'d9ef40b57477bfa5589ef1c6d66bd27bcd4c85dd')
  self.assertEqual(f[R10]['cn_git_blob_sha1'],'0e09c7eeb0d916f62184b90fb5cabd6c48aab83c')
  self.assertEqual(f[R10]['en_git_blob_sha1'],'5a484f9820a5937c1e2f4668ef41f30e78cd5e19')
  self.assertIn('c7',f[R09]['dialogues']['17'])
  self.assertIn('ладью',f[R09]['dialogues']['17'])
  self.assertIn('Нирл',f[R09]['dialogues']['49'])
  self.assertNotIn('колесница',f[R09]['dialogues']['49'])
  self.assertIn('Фауст',f[R10]['dialogues']['20'])
  self.assertIn('Казимеж',f[R10]['dialogues']['52'])
  self.assertIn('{@nickname}',f[R09]['dialogues']['48'])

 def test_speaker_localization_and_unmodified_controls(self):
  self.assertEqual(engine.SPEAKER_RU['Nearl'],'Нирл')
  self.assertEqual(engine.SPEAKER_RU['Faust'],'Фауст')
  txt='[HEADER(key="x")]\r\n[Fade(a=1)]\r\n[name="Nearl"]  Say something.\r\n[Background(image="bg")]\r\n[name="Faust"]  Hmph.\r\n'
  b,n=engine.patch_bytes(txt.encode('utf8'),{'1':'Отступайте!','2':'…'})
  target=b.decode('utf8')
  self.assertEqual(n,2)
  self.assertIn('[name="Нирл"]  Отступайте!',target)
  self.assertIn('[name="Фауст"]  …',target)
  self.assertIn('[Fade(a=1)]',target)
  self.assertIn('[Background(image="bg")]',target)
  self.assertEqual(target.count('\r\n'),txt.count('\r\n'))

 def test_full_eleven_scene_synthetic_preview(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp)
   modified={}
   for rel,cfg in self.both['files'].items():
    cn=['[HEADER(key="important")]','[PlayMusic(key="keep_this")]']
    en=['[HEADER(key="important")]','[PlayMusic(key="keep_this")]']
    for idx in range(1,cfg['dialogue_count']+1):
     tokens=engine.quoted_tokens(cfg['dialogues'][str(idx)])
     # synthetic alignment deliberately uses real RU markup tokens
     en.append('[name="Nearl"]  English '+ (' '.join(tokens) if tokens else 'line'))
     cn.append('[name="临光"]  中文')
     en.append('[Background(image="original_bg")]')
     cn.append('[Background(image="original_bg")]')
    e=('\r\n'.join(en)+'\r\n').encode('utf-8')
    c=('\r\n'.join(cn)+'\r\n').encode('utf-8')
    for language,data in [('cn',c),('en',e)]:
     target=root/'sources'/language/rel
     target.parent.mkdir(parents=True,exist_ok=True)
     target.write_bytes(data)
    conf=copy.deepcopy(cfg)
    conf['cn_git_blob_sha1']=engine.git_blob_sha1(c)
    conf['en_git_blob_sha1']=engine.git_blob_sha1(e)
    modified[rel]=conf
   tr=root/'input.json'
   tr.write_text(json.dumps({'version':'v0.19 synthetic','files':modified},ensure_ascii=False),'utf8')
   report=engine.build(root/'sources',root/'output',tr)
   self.assertEqual(report['lines_total'],594)
   self.assertEqual(len(report['files']),11)
   for rel,cfg in modified.items():
    out=(root/'output/ru'/rel).read_text('utf8')
    self.assertIn('[PlayMusic(key="keep_this")]',out)
    self.assertEqual(out.count('[Background(image="original_bg")]'),cfg['dialogue_count'])
    self.assertEqual(out.count('[name="Нирл"]'),cfg['dialogue_count'])
    self.assertEqual(out.count('[HEADER(key="important")]'),1)

 def test_bad_source_hash_prevents_output_creation(self):
  rel=R10
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp)
   cfg=copy.deepcopy(self.new['files'][rel])
   for lang,s in [('en','[name="Nearl"] Text\n'),('cn','[name="临光"] 内容\n')]:
    p=root/'sources'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,'utf8')
   tr=root/'translations.json';tr.write_text(json.dumps({'files':{rel:cfg}}),'utf8')
   with self.assertRaisesRegex(ValueError,'revision mismatch'):
    engine.build(root/'sources',root/'output',tr)
   self.assertFalse((root/'output').exists())

 def test_unauthorized_path_and_old_regex_safety(self):
  self.assertNotRegex('obt/main/../other.txt',r'^obt/main/level_main_00-(?:01_(?:beg|end)|02_(?:beg|end)|04_beg|06_end|07_(?:beg|end)|08_beg|09_end|10_beg)\.txt$')
  for rel in [R09,R10]:
   self.assertRegex(rel,r'^obt/main/level_main_00-(?:01_(?:beg|end)|02_(?:beg|end)|04_beg|06_end|07_(?:beg|end)|08_beg|09_end|10_beg)\.txt$')

if __name__=='__main__':
 unittest.main(verbosity=2)
