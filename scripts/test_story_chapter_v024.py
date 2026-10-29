# -*- coding: utf-8 -*-
import copy,json,pathlib,sys,tempfile,unittest,re,hashlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import apply_ru_story as ap
PREV=json.loads((ROOT/'story/story_main_selection_ru_v023.json').read_text('utf8'))
ALL=json.loads((ROOT/'story/story_main_selection_ru_v024.json').read_text('utf8'))
CH=json.loads((ROOT/'story/story_chapter_2_part_3_ru_v024.json').read_text('utf8'))
SHAS={
'02-04_beg':('e21d3ff27b6a6c4f4e8c62bb8e7a5bce265eea63','1ac89425fabf20a1c093b94470731ca2ce779bca',62),
'02-04_end':('d70bfa56a7b2a0ac022832562a6162ab4a870805','1839989a30dc73c20ae55bf1f2ca9ea9958a2daf',43),
'02-05_beg':('f102c4671a0398fee5b8f223f8c83089b86642b4','4f1db44081816fba4f051d52ad5e143b91568417',51),
'02-05_end':('519fdfd2f05c20ad04ef3abb188025bf7844a11f','456fdebaa5ca11e76a0f6b8d924715b7e58a2e20',54),
}
class Chapter2V024(unittest.TestCase):
 def test_exact_counts(self):
  self.assertEqual((len(CH['files']),sum(t['dialogue_count'] for t in CH['files'].values())),(10,596))
  self.assertEqual((len(ALL['files']),sum(t['dialogue_count'] for t in ALL['files'].values())),(34,1951))
 def test_old_translations_identical(self):
  for k,v in PREV['files'].items():self.assertEqual(ALL['files'][k],v)
 def test_versions_and_order(self):
  for short,(cn,en,n) in SHAS.items():
   rel=f'obt/main/level_main_{short}.txt';t=ALL['files'][rel]
   self.assertEqual((t['cn_git_blob_sha1'],t['en_git_blob_sha1'],t['dialogue_count']),(cn,en,n))
   self.assertEqual(set(t['dialogues']),{str(i) for i in range(1,n+1)})
 def test_untouched_markup(self):
  for short in SHAS:
   rel=f'obt/main/level_main_{short}.txt'; t=ALL['files'][rel]
   marks={int(i):ap.quoted_tokens(text) for i,text in t['dialogues'].items() if ap.quoted_tokens(text)}
   self.assertEqual(marks,({53:['{@nickname}']} if short=='02-05_end' else {}))
 def test_no_newlines_in_dialogues(self):
  for short in SHAS:
   rel=f'obt/main/level_main_{short}.txt'
   for text in ALL['files'][rel]['dialogues'].values():
    self.assertTrue(text.strip());self.assertNotRegex(text,r'[\r\n\t]')
 def test_new_speaker_tags(self):
  for name in ('Exusiai','Texas','Skullshatterer','Misha','Franka','Liskarm'):
   self.assertIn(name,ap.SPEAKER_RU)
 def test_allowlist(self):
  for short in SHAS:self.assertRegex('obt/main/level_main_'+short+'.txt','^'+ap.ALLOWED_PATH+'$')
 def test_index_counts(self):
  import csv
  with (ROOT/'story/CHAPTER_2_INDEX_v024.tsv').open(encoding='utf8') as f:
   rows=list(csv.DictReader(f,delimiter='\t'))
  self.assertEqual(len(rows),20)
  self.assertEqual(sum(x['ru_status']=='first_draft_complete' for x in rows),10)
  self.assertEqual(sum(int(x['dialogues_ru_count']) for x in rows),596)
 def test_synthetic_full_34_scene_build(self):
  with tempfile.TemporaryDirectory() as td:
   tmp=pathlib.Path(td);config=copy.deepcopy(ALL)
   for rel,info in config['files'].items():
    en=['[PlayMusic(key="keep-original")]'];cn=['[PlayMusic(key="keep-original")]']
    for i in range(1,info['dialogue_count']+1):
     toks=ap.quoted_tokens(info['dialogues'][str(i)])
     en.extend(['[name="Amiya"]  '+(' '.join(toks) if toks else 'English'), '[Background(image="keep-original")]'])
     cn.extend(['[name="阿米娅"]  中文','[Background(image="keep-original")]'])
    for lang,lines in (('en',en),('cn',cn)):
     data=('\n'.join(lines)+'\n').encode('utf8');p=tmp/'source'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
     info[lang+'_git_blob_sha1']=ap.git_blob_sha1(data)
   cf=tmp/'conf.json';cf.write_text(json.dumps(config,ensure_ascii=False),encoding='utf8')
   summary=ap.build(tmp/'source',tmp/'out',cf)
   self.assertEqual((len(summary['files']),summary['lines_total']),(34,1951))
   for rel,info in config['files'].items():
    orig=(tmp/'source/en'/rel).read_text('utf8').splitlines();patched=(tmp/'out/ru'/rel).read_text('utf8').splitlines()
    self.assertEqual(len(orig),len(patched))
    self.assertEqual([v for v in orig if v.startswith('[Background')],[v for v in patched if v.startswith('[Background')])
 def test_reject_wrong_revision_without_output(self):
  with tempfile.TemporaryDirectory() as td:
   d=pathlib.Path(td);rel='obt/main/level_main_02-05_end.txt'
   for lang in ('en','cn'):
    p=d/'src'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('[name="Amiya"]  tampered\n',encoding='utf8')
   c=d/'config.json';c.write_text(json.dumps({'files':{rel:ALL['files'][rel]}},ensure_ascii=False),encoding='utf8')
   with self.assertRaisesRegex(ValueError,'Source revision mismatch'):ap.build(d/'src',d/'out',c)
   self.assertFalse((d/'out').exists())
if __name__=='__main__':unittest.main()
