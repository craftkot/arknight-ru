# coding: utf-8
import copy,hashlib,json,pathlib,re,sys,tempfile,unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).parent
sys.path.insert(0,str(HERE))
import apply_ru_story as engine
import fetch_story_chapter as fetch
ROOT=HERE.parent
CH=json.loads((ROOT/'story/story_chapter_2_part_1_ru_v022.json').read_text('utf8'))
ALL=json.loads((ROOT/'story/story_main_selection_ru_v022.json').read_text('utf8'))
OLD=json.loads((ROOT/'story/story_main_selection_ru_v021.json').read_text('utf8'))
TOKENS={'02-01_beg':{4:['{@nickname}'],9:['{@nickname}']},'02-01_end':{21:['{@nickname}'],38:['{@nickname}'],65:['{@nickname}']},'02-02_beg':{4:['{@nickname}']}}
class ChapterTwoPartOne(unittest.TestCase):
 def test_counts(self):
  self.assertEqual(len(CH['files']),3)
  self.assertEqual(sum(m['dialogue_count'] for m in CH['files'].values()),153)
  self.assertEqual(len(ALL['files']),27)
  self.assertEqual(sum(m['dialogue_count'] for m in ALL['files'].values()),1508)
 def test_earlier_chapters_identical(self):
  for path,data in OLD['files'].items():self.assertEqual(data,ALL['files'][path])
 def test_positions_and_tokens(self):
  for rel,m in CH['files'].items():
   self.assertRegex(rel,engine.ALLOWED_PATH)
   self.assertEqual(set(m['dialogues']),{str(x) for x in range(1,m['dialogue_count']+1)})
   s=pathlib.Path(rel).stem.replace('level_main_','')
   for n,v in m['dialogues'].items():
    self.assertTrue(v.strip())
    self.assertFalse(any(c in v for c in '\n\r\t'))
    self.assertEqual(engine.quoted_tokens(v),TOKENS.get(s,{}).get(int(n),[]),(s,n))
 def test_new_speakers(self):
  for name in ('PRTS','Broadcast','L.G.D. Agent',"Ch'en", "Kal'tsit",'Wei Yenwu','Infected'):
   self.assertIn(name,engine.SPEAKER_RU)
 def test_whitelist_rejects_unrelated_stages(self):
  for suffix in ('02-01_beg','02-02_beg','02-10_end'):
   self.assertRegex('obt/main/level_main_'+suffix+'.txt',engine.ALLOWED_PATH)
  for path in ('obt/main/../secret.txt','obt/main/level_main_02-11_beg.txt','obt/main/level_main_99-99_end.txt'):
   self.assertNotRegex(path,engine.ALLOWED_PATH)
 def test_synthetic_27_scene_build_preserves_controls(self):
  with tempfile.TemporaryDirectory() as td:
   d=pathlib.Path(td);config=copy.deepcopy(ALL)
   for rel,m in config['files'].items():
    cn=['[HEADER(dummy=1)]','[PlayMusic(key="unchanged")]']
    en=['[HEADER(dummy=1)]','[PlayMusic(key="unchanged")]']
    for i in range(1,m['dialogue_count']+1):
     tok=engine.quoted_tokens(m['dialogues'][str(i)])
     en.append('[name="Amiya"]  '+(' '.join(tok) if tok else 'English'))
     cn.append('[name="阿米娅"]  中文')
     en.append('[Background(image="original")]')
     cn.append('[Background(image="original")]')
    for lang,lines in (('cn',cn),('en',en)):
     raw=('\r\n'.join(lines)+'\r\n').encode()
     p=d/'src'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
     m[lang+'_git_blob_sha1']=engine.git_blob_sha1(raw)
   cfg=d/'input.json';cfg.write_text(json.dumps(config,ensure_ascii=False),'utf8')
   rep=engine.build(d/'src',d/'out',cfg)
   self.assertEqual(rep['lines_total'],1508)
   self.assertEqual(len(rep['files']),27)
   for rel,m in config['files'].items():
    data=(d/'out'/'ru'/rel).read_text('utf8')
    self.assertIn('[PlayMusic(key="unchanged")]',data)
    self.assertEqual(data.count('[Background(image="original")]'),m['dialogue_count'])
 def test_version_mismatch_rejected_without_output(self):
  with tempfile.TemporaryDirectory() as td:
   d=pathlib.Path(td);rel=next(iter(CH['files']))
   m=CH['files'][rel]
   for lang in ('cn','en'):
    p=d/'src'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('[name="Amiya"]  changed\n','utf8')
   cfg=d/'input.json';cfg.write_text(json.dumps({'files':{rel:m}}),'utf8')
   with self.assertRaisesRegex(ValueError,'Source revision mismatch'):
    engine.build(d/'src',d/'out',cfg)
   self.assertFalse((d/'out').exists())
 def test_chapter_two_index(self):
  lines=(ROOT/'story/CHAPTER_2_INDEX_v022.tsv').read_text('utf8').splitlines()
  self.assertEqual(len(lines),21)
  self.assertEqual(sum('first_draft_complete' in line for line in lines),3)
if __name__=='__main__':unittest.main()
