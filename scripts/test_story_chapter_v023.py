# coding: utf-8
import copy,hashlib,json,pathlib,sys,tempfile,unittest
HERE=pathlib.Path(__file__).parent
sys.path.insert(0,str(HERE))
import apply_ru_story as ap
ROOT=HERE.parent
OLD=json.loads((ROOT/'story/story_main_selection_ru_v022.json').read_text('utf8'))
ALL=json.loads((ROOT/'story/story_main_selection_ru_v023.json').read_text('utf8'))
CH=json.loads((ROOT/'story/story_chapter_2_part_2_ru_v023.json').read_text('utf8'))
MARKS={'02-02_end':{76:['{@nickname}'],81:['{@nickname}']},'02-03_beg':{89:['{@nickname}']},'02-03_end':{}}
class V023(unittest.TestCase):
 def test_counts(self):
  self.assertEqual(len(CH['files']),6)
  self.assertEqual(sum(x['dialogue_count'] for x in CH['files'].values()),386)
  self.assertEqual(len(ALL['files']),30)
  self.assertEqual(sum(x['dialogue_count'] for x in ALL['files'].values()),1741)
 def test_old_translations_unmodified(self):
  for k,v in OLD['files'].items():self.assertEqual(ALL['files'][k],v)
 def test_new_tokens_and_ordinals(self):
  for short in ('02-02_end','02-03_beg','02-03_end'):
   key='obt/main/level_main_'+short+'.txt';m=ALL['files'][key]
   self.assertEqual(set(m['dialogues']),{str(i) for i in range(1,m['dialogue_count']+1)})
   self.assertEqual(int(m['dialogue_count']),{'02-02_end':82,'02-03_beg':91,'02-03_end':60}[short])
   for i,t in m['dialogues'].items():
    self.assertTrue(t.strip());self.assertEqual(ap.quoted_tokens(t),MARKS[short].get(int(i),[]))
    self.assertFalse(any(c in t for c in '\r\n\t'))
 def test_new_speakers_mapped(self):
  for s in ('Misha','Rioter','Children','Franka','Liskarm','Ch\'en'):
   self.assertIn(s,ap.SPEAKER_RU)
 def test_new_scripts_within_allowlist(self):
  import re
  for short in ('02-02_end','02-03_beg','02-03_end'):
   self.assertTrue(re.fullmatch(ap.ALLOWED_PATH,'obt/main/level_main_'+short+'.txt'))
 def test_synthetic_all_scripts_preserves_scene_commands(self):
  with tempfile.TemporaryDirectory() as td:
   d=pathlib.Path(td);doc=copy.deepcopy(ALL)
   for rel,conf in doc['files'].items():
    a=['[PlayMusic(key="original")]'];b=['[PlayMusic(key="original")]']
    for i in range(1,conf['dialogue_count']+1):
     tok=ap.quoted_tokens(conf['dialogues'][str(i)])
     a.extend(['[name="阿米娅"]  中文','[Background(image="unchanged")]'])
     b.extend(['[name="Amiya"]  '+(' '.join(tok) if tok else 'English'),'[Background(image="unchanged")]'])
    for lang,arr in (('cn',a),('en',b)):
     data=('\n'.join(arr)+'\n').encode('utf8');f=d/'src'/lang/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
     conf[lang+'_git_blob_sha1']=ap.git_blob_sha1(data)
   config=d/'config.json';config.write_text(json.dumps(doc,ensure_ascii=False),'utf8')
   report=ap.build(d/'src',d/'output',config)
   self.assertEqual(report['lines_total'],1741)
   self.assertEqual(len(report['files']),30)
   for rel,cfg in doc['files'].items():
    blob=(d/'output'/'ru'/rel).read_text('utf8')
    self.assertIn('[PlayMusic(key="original")]',blob)
    self.assertEqual(blob.count('[Background(image="unchanged")]'),cfg['dialogue_count'])
 def test_bad_sha_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   d=pathlib.Path(td);key='obt/main/level_main_02-02_end.txt';v=ALL['files'][key]
   for lang in ('en','cn'):
    f=d/'src'/lang/key;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('[name="Amiya"]  changed\n','utf8')
   c=d/'c.json';c.write_text(json.dumps({'files':{key:v}}),'utf8')
   with self.assertRaisesRegex(ValueError,'Source revision mismatch'):
    ap.build(d/'src',d/'out',c)
   self.assertFalse((d/'out').exists())
if __name__=='__main__':unittest.main()
