# coding: utf-8
"""Chapter 1 reviewed keyed text and safe all-chapter preview regression checks."""
import copy
import hashlib
import json
import pathlib
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).parent
sys.path.insert(0,str(HERE))
import apply_ru_story as eng
import fetch_story_chapter as fetch
BASE=HERE.parent
OLD=json.loads((BASE/'story/story_main_selection_ru_v020.json').read_text('utf8'))
ONE=json.loads((BASE/'story/story_chapter_1_ru_v021.json').read_text('utf8'))
ALL=json.loads((BASE/'story/story_main_selection_ru_v021.json').read_text('utf8'))
PLACEHOLDERS={
 '01-01_end':{3:['{@nickname}']},
 '01-03_beg':{3:['{@nickname}'],11:['{@nickname}'],25:['{@nickname}'],28:['{@nickname}']},
 '01-07_beg':{27:['{@nickname}']},
 '01-08_beg':{11:['{@nickname}'],135:['{@nickname}']},
 '01-10_end':{24:['{@nickname}']},
 '01-12_beg':{3:['{@nickname}'],22:['{@Nickname}'],23:['{@Nickname}']},
 '01-12_end':{18:['{@Nickname}'],34:['{@nickname}'],54:['{@nickname}']}
}

class ChapterOne(unittest.TestCase):
 def test_all_twelve_scenes_seven_hundred_one_dialogues(self):
  self.assertEqual(len(ONE['files']),12)
  self.assertEqual(sum(x['dialogue_count'] for x in ONE['files'].values()),701)
  self.assertEqual(len(ALL['files']),24)
  self.assertEqual(sum(x['dialogue_count'] for x in ALL['files'].values()),1355)
 def test_all_old_chapter_zero_untouched(self):
  self.assertEqual(OLD['files'],{k:v for k,v in ALL['files'].items() if k in OLD['files']})
 def test_complete_ordinals_no_bad_whitespace(self):
  for name,meta in ONE['files'].items():
   self.assertEqual(set(meta['dialogues']),{str(i) for i in range(1,1+meta['dialogue_count'])},name)
   for n,s in meta['dialogues'].items():
    self.assertTrue(s.strip(),(name,n))
    self.assertFalse(any(x in s for x in '\r\n\t'),(name,n))
 def test_original_english_placeholders_unchanged(self):
  for name,meta in ONE['files'].items():
   suffix=pathlib.Path(name).stem[len('level_main_'):]
   expected=PLACEHOLDERS.get(suffix,{})
   for number,s in meta['dialogues'].items():
    self.assertEqual(eng.quoted_tokens(s),expected.get(int(number),[]),(suffix,number))
 def test_sources_are_pinned_and_paths_safe(self):
  for name,meta in ONE['files'].items():
   self.assertRegex(name,eng.ALLOWED_PATH)
   for lang in ('cn','en'):self.assertRegex(meta[lang+'_git_blob_sha1'],r'^[0-9a-f]{40}$')
  self.assertNotRegex('obt/main/../secret.txt',eng.ALLOWED_PATH)
  self.assertNotRegex('obt/main/level_main_99-02_beg.txt',eng.ALLOWED_PATH)
 def test_speaker_names_and_story_commands(self):
  for name in ('','Civilian','Talulah','W','Amiya','Dobermann'):
   self.assertIn(name,eng.SPEAKER_RU)
  src=b'[PlayMusic(key="x")]\r\n[name="Civilian"]  Hello\r\n[Background(image="bg")]\r\n'
  result,count=eng.patch_bytes(src,{'1':'Привет'})
  self.assertEqual(count,1)
  self.assertIn('[name="Мирный житель"]',result.decode('utf8'))
  self.assertEqual(result.decode('utf8').splitlines()[0],'[PlayMusic(key="x")]')
  self.assertEqual(result.decode('utf8').splitlines()[-1],'[Background(image="bg")]')
 def test_full_24_scenes_synthetic_preview_preserves_non_dialogue(self):
  with tempfile.TemporaryDirectory() as td:
   temp=pathlib.Path(td);cfg=copy.deepcopy(ALL)
   for rel,meta in cfg['files'].items():
    cn=['[HEADER(test=1)]','[PlayMusic(key="original")]']
    en=['[HEADER(test=1)]','[PlayMusic(key="original")]']
    for k in range(1,meta['dialogue_count']+1):
     tokens=eng.quoted_tokens(meta['dialogues'][str(k)])
     speaker='W' if rel.startswith('obt/main/level_main_01-') else 'Nearl'
     en.append('[name="'+speaker+'"]  English '+(' '.join(tokens) if tokens else 'placeholder'))
     cn.append('[name="临光"]  中文')
     en.append('[Background(image="untouched")]');cn.append('[Background(image="untouched")]')
    for lang,lines in [('cn',cn),('en',en)]:
     payload=('\r\n'.join(lines)+'\r\n').encode('utf8')
     target=temp/'src'/lang/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
     meta[lang+'_git_blob_sha1']=eng.git_blob_sha1(payload)
   config=temp/'config.json';config.write_text(json.dumps(cfg,ensure_ascii=False),'utf8')
   result=eng.build(temp/'src',temp/'out',config)
   self.assertEqual(result['lines_total'],1355)
   self.assertEqual(len(result['files']),24)
   for rel,meta in cfg['files'].items():
    a=(temp/'out'/'ru'/rel).read_text('utf8')
    self.assertEqual(a.count('[Background(image="untouched")]'),meta['dialogue_count'])
    self.assertIn('[PlayMusic(key="original")]',a)
 def test_source_revision_failure_writes_no_preview(self):
  with tempfile.TemporaryDirectory() as td:
   temp=pathlib.Path(td);rel=next(iter(ONE['files']))
   meta=copy.deepcopy(ONE['files'][rel])
   for lang in ('cn','en'):
    p=temp/'src'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'[name="Amiya"]  changed\n')
   inp=temp/'config.json';inp.write_text(json.dumps({'files':{rel:meta}},ensure_ascii=False),'utf8')
   with self.assertRaisesRegex(ValueError,'Source revision mismatch'):
    eng.build(temp/'src',temp/'out',inp)
   self.assertFalse((temp/'out').exists())
 def test_batch_fetch_preflight_no_partial_writes(self):
  with tempfile.TemporaryDirectory() as td:
   temp=pathlib.Path(td);data=b'[name="Nearl"]  Good\n';sha=eng.git_blob_sha1(data)
   rels=list(ONE['files'])[:2]
   inp={'files':{rels[0]:{'cn_git_blob_sha1':sha,'en_git_blob_sha1':sha},rels[1]:{'cn_git_blob_sha1':sha,'en_git_blob_sha1':'0'*40}}}
   p=temp/'in.json';p.write_text(json.dumps(inp),'utf8')
   with patch.object(fetch,'get_source',return_value=data):
    with self.assertRaisesRegex(ValueError,'revision mismatch'):
     fetch.fetch_all(p,temp/'source')
   self.assertFalse((temp/'source').exists())

if __name__=='__main__':unittest.main()
