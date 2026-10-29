# coding: utf-8
import copy, json, pathlib, tempfile, unittest, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import apply_ru_story as m
ROOT=pathlib.Path(__file__).resolve().parent
class Stage07(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.new=json.loads((ROOT/'story_0-7_ru_v017.json').read_text('utf8'))
  cls.full=json.loads((ROOT/'story_main_selection_ru_v017.json').read_text('utf8'))
  cls.previous=json.loads((ROOT/'story_main_selection_ru_v016.json').read_text('utf8'))
 def test_counts_and_nonempty(self):
  self.assertEqual([v['dialogue_count'] for v in self.new['files'].values()],[56,42])
  self.assertEqual(sum(x['dialogue_count'] for x in self.full['files'].values()),413)
  self.assertEqual(len(self.full['files']),8)
  for cfg in self.full['files'].values():
   self.assertEqual(set(cfg['dialogues']),set(map(str,range(1,cfg['dialogue_count']+1))))
   for phrase in cfg['dialogues'].values():
    self.assertIsInstance(phrase,str);self.assertTrue(phrase.strip());self.assertNotIn('\n',phrase);self.assertNotIn('\t',phrase)
 def test_previous_315_unchanged(self):
  for rel,data in self.previous['files'].items():self.assertEqual(data,self.full['files'][rel])
 def test_cn_original_nuances(self):
  beg=self.new['files']['obt/main/level_main_00-07_beg.txt']['dialogues']
  self.assertIn('железной комнате',beg['38'])
  self.assertIn('пешка',beg['49'])
  self.assertIn('Dr.{@nickname}',beg['40'])
  self.assertIn('Dr.{@nickname}',beg['51'])
  end=self.new['files']['obt/main/level_main_00-07_end.txt']['dialogues']
  self.assertIn('Краунслеер',end['39'])
  self.assertIn('Ниарл',end['2'])
 def test_source_revisions(self):
  self.assertEqual(self.new['files']['obt/main/level_main_00-07_beg.txt']['cn_git_blob_sha1'],'41506122d7c8886b283027aacba1581d60ef660a')
  for cfg in self.new['files'].values():
   self.assertRegex(cfg['cn_git_blob_sha1'],r'^[0-9a-f]{40}$')
   self.assertRegex(cfg['en_git_blob_sha1'],r'^[0-9a-f]{40}$')
 def test_crownslayer_speaker(self):
  self.assertEqual(m.SPEAKER_RU['Crownslayer'],'Краунслеер')
  base='[HEADER(x=1)]\r\n[name="Crownslayer"] Разговор\r\n[PlayMusic(key="x")]\r\n'
  patched,n=m.patch_bytes(base.encode(),{'1':'Зачем ты пришёл?'})
  self.assertEqual(n,1);self.assertIn('[name="Краунслеер"]',patched.decode());self.assertIn('[PlayMusic(key="x")]',patched.decode());self.assertNotIn('Разговор',patched.decode())
 def test_synthetic_both_build_and_no_source_write(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d); payload={}
   for rel,cfg in self.new['files'].items():
    en_lines=['[HEADER(key="test", fit_mode="BLACK_MASK")]','[PlayMusic(key="original", volume=0.6)]']
    cn_lines=['[HEADER(key="test", fit_mode="BLACK_MASK")]','[PlayMusic(key="original", volume=0.6)]']
    for i in range(1,cfg['dialogue_count']+1):
     tag=('Dr.{@nickname}' if rel.endswith('beg.txt') and i in (40,51) else 'text')
     name='Crownslayer' if rel.endswith('end.txt') and i==41 else 'Dobermann'
     en_lines.extend([f'[name="{name}"]  {tag}', '[Background(image="bg_safe")]'])
     cn_lines.extend(['[name="杜宾"]  测试','[Background(image="bg_safe")]'])
    en=('\r\n'.join(en_lines)+'\r\n').encode('utf8');cn=('\r\n'.join(cn_lines)+'\r\n').encode('utf8')
    for lang,b in [('en',en),('cn',cn)]:
     p=root/'src'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    c=copy.deepcopy(cfg);c['en_git_blob_sha1']=m.git_blob_sha1(en);c['cn_git_blob_sha1']=m.git_blob_sha1(cn);payload[rel]=c
   tr=root/'translate.json';tr.write_text(json.dumps({'version':'synthetic','files':payload},ensure_ascii=False),encoding='utf8')
   report=m.build(root/'src',root/'generated',tr)
   self.assertEqual(report['lines_total'],98)
   self.assertEqual(len(report['files']),2)
   for rel,cfg in payload.items():
    got=(root/'generated/ru'/rel).read_text('utf8')
    self.assertEqual(got.count('[PlayMusic('),1)
    self.assertEqual(got.count('[Background('),cfg['dialogue_count'])
    self.assertIn('Краунслеер',got) if rel.endswith('end.txt') else None
    self.assertIn('[HEADER(key="test", fit_mode="BLACK_MASK")]',got)
    self.assertIn(b'\r\n',(root/'generated/ru'/rel).read_bytes())
    self.assertIn('测试',(root/'src/cn'/rel).read_text('utf8'))
 def test_version_mismatch_stops_before_output(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   rel='obt/main/level_main_00-07_beg.txt';cfg=copy.deepcopy(self.new['files'][rel]);cfg['dialogue_count']=1;cfg['dialogues']={'1':'Привет'}
   for lang in ['cn','en']:
    p=root/'src'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('[name="Dobermann"] Test',encoding='utf8')
   tr=root/'translate.json';tr.write_text(json.dumps({'files':{rel:cfg}}),encoding='utf8')
   with self.assertRaisesRegex(ValueError,'revision mismatch'):m.build(root/'src',root/'out',tr)
   self.assertFalse((root/'out').exists())
 def test_path_allowlist_no_traversal(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);cfg=copy.deepcopy(next(iter(self.new['files'].values())))
   tr=root/'t.json';tr.write_text(json.dumps({'files':{'obt/main/../../escape.txt':cfg}}),encoding='utf8')
   with self.assertRaisesRegex(ValueError,'Unexpected or unsafe'):m.build(root/'src',root/'out',tr)
if __name__=='__main__': unittest.main(verbosity=2)
