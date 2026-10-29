# -*- coding: utf-8 -*-
"""Regression tests for CN-primary 0-8 draft and 9-scene cumulative preview."""
import copy
import json
import pathlib
import re
import tempfile
import unittest
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import apply_ru_story as engine
D=pathlib.Path(__file__).resolve().parent
NEW='obt/main/level_main_00-08_beg.txt'

class Stage08(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.new=json.loads((D/'story_0-8_ru_v018.json').read_text('utf8'))
  cls.old=json.loads((D/'story_main_selection_ru_v017.json').read_text('utf8'))
  cls.combined=json.loads((D/'story_main_selection_ru_v018.json').read_text('utf8'))
 def test_78_lines_and_exact_key_coverage(self):
  cfg=self.new['files'][NEW]
  self.assertEqual(cfg['dialogue_count'],78)
  self.assertEqual(set(cfg['dialogues']),set(map(str,range(1,79))))
  for r in cfg['dialogues'].values():
   self.assertTrue(r.strip());self.assertNotRegex(r,r'[\t\r\n]')
 def test_previous_413_lines_unchanged(self):
  for k,v in self.old['files'].items():self.assertEqual(v,self.combined['files'][k])
  self.assertEqual(len(self.combined['files']),9)
  self.assertEqual(sum(v['dialogue_count'] for v in self.combined['files'].values()),491)
 def test_pinned_cn_en_blobs(self):
  self.assertEqual(self.new['files'][NEW]['cn_git_blob_sha1'],'4a3d59100acba8510292fa2879c0dbfe6b8da274')
  self.assertEqual(self.new['files'][NEW]['en_git_blob_sha1'],'a9c1c1258964a2622b6fbacf4c9b95c0e1d63dc6')
 def test_CN_semantic_priority(self):
  d=self.new['files'][NEW]['dialogues']
  self.assertIn('букашек',d['3']);self.assertNotIn('свет',d['3'])
  self.assertEqual(d['58'],'…Ты…')
  self.assertIn('устройство',d['72'])
  self.assertIn('Мефисто',d['18'])
 def test_mephisto_speaker_tag(self):
  self.assertEqual(engine.SPEAKER_RU['Mephisto'],'Мефисто')
  old='[PlayMusic(key="cue")]\r\n[name="Mephisto"]  Hello!\r\n[Background(image="test")]\r\n'
  out,n=engine.patch_bytes(old.encode(),{'1':'Здравствуйте!'});txt=out.decode()
  self.assertEqual(n,1);self.assertIn('[name="Мефисто"]  Здравствуйте!',txt)
  self.assertIn('[PlayMusic(key="cue")]',txt);self.assertIn('[Background(image="test")]',txt)
 def test_preview_all_nine_synthetic_pinned_and_unmodified(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);cfgs={}
   for rel,cfg in self.combined['files'].items():
    e=['[HEADER(key="test")]', '[PlayMusic(intro="x",key="original")]']
    c=['[HEADER(key="test")]', '[PlayMusic(intro="x",key="original")]']
    for idx in range(1,cfg['dialogue_count']+1):
     ru=cfg['dialogues'][str(idx)]
     # Simulate the expected original markup exactly, without assuming the original prose.
     tokens=engine.quoted_tokens(ru)
     speaker='Mephisto' if rel==NEW and idx>=18 else ('Crownslayer' if rel==NEW and idx<=12 else 'Dobermann')
     e.append(f'[name="{speaker}"]  Original '+(' '.join(tokens) if tokens else 'text'))
     c.append('[name="杜宾"]  原文')
     e.append('[Background(image="bg_unmodified")]')
     c.append('[Background(image="bg_unmodified")]')
    en=('\r\n'.join(e)+'\r\n').encode('utf8');cn=('\r\n'.join(c)+'\r\n').encode('utf8')
    for lang,content in [('en',en),('cn',cn)]:
     p=root/'source'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    copy_cfg=copy.deepcopy(cfg)
    copy_cfg['cn_git_blob_sha1']=engine.git_blob_sha1(cn)
    copy_cfg['en_git_blob_sha1']=engine.git_blob_sha1(en)
    cfgs[rel]=copy_cfg
   tr=root/'translation.json';tr.write_text(json.dumps({'version':'v0.18-synthetic','files':cfgs},ensure_ascii=False),'utf8')
   result=engine.build(root/'source',root/'preview',tr)
   self.assertEqual(result['lines_total'],491);self.assertEqual(len(result['files']),9)
   for rel,cfg in cfgs.items():
    generated=(root/'preview/ru'/rel).read_text('utf8')
    self.assertEqual(generated.count('[PlayMusic('),1)
    self.assertEqual(generated.count('[Background('),cfg['dialogue_count'])
    self.assertEqual(generated.count('[name='),cfg['dialogue_count'])
    self.assertIn('[HEADER(key="test")]',generated)
    self.assertEqual((root/'source/en'/rel).read_bytes().count(b'[Background('),cfg['dialogue_count'])
    if rel==NEW:self.assertIn('[name="Мефисто"]',generated)
 def test_revision_mismatch_refuses_partial_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);cfg=copy.deepcopy(self.new['files'][NEW]);cfg['dialogue_count']=1;cfg['dialogues']={'1':'Тест'}
   for lang in ['en','cn']:
    p=root/'source'/lang/NEW;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('[name="Mephisto"] Hello','utf8')
   manifest=root/'cfg.json';manifest.write_text(json.dumps({'version':'test','files':{NEW:cfg}}),'utf8')
   with self.assertRaisesRegex(ValueError,'revision mismatch'):engine.build(root/'source',root/'output',manifest)
   self.assertFalse((root/'output').exists())
 def test_no_unauthorized_filenames(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp)
   t=root/'translation.json';t.write_text(json.dumps({'files':{'obt/main/../other.txt':self.new['files'][NEW]}}),'utf8')
   with self.assertRaisesRegex(ValueError,'Unexpected or unsafe'):engine.build(root/'src',root/'out',t)

if __name__=='__main__':unittest.main(verbosity=2)
