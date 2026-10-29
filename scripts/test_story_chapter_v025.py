# -*- coding: utf-8 -*-
import copy, csv, json, pathlib, re, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import apply_ru_story as ap
ALL=json.loads((ROOT/'story/story_main_selection_ru_v025.json').read_text('utf8'))
CH=json.loads((ROOT/'story/story_chapter_2_complete_ru_v025.json').read_text('utf8'))
PREV=json.loads((ROOT/'story/story_main_selection_ru_v024.json').read_text('utf8'))
class Chapter2FullFirstDraft(unittest.TestCase):
 def test_totals(self):
  self.assertEqual((len(CH['files']),sum(f['dialogue_count'] for f in CH['files'].values())),(20,1022))
  self.assertEqual((len(ALL['files']),sum(f['dialogue_count'] for f in ALL['files'].values())),(44,2377))
 def test_previous_work_preserved(self):
  for k,v in PREV['files'].items():self.assertEqual(v,ALL['files'][k])
 def test_all20_chapter_keys(self):
  expect={f'obt/main/level_main_02-{i:02}_{part}.txt' for i in range(1,11) for part in ('beg','end')}
  self.assertEqual(set(CH['files']),expect)
 def test_ordinals_and_blobs(self):
  for rel,info in ALL['files'].items():
   n=info['dialogue_count'];self.assertEqual(set(info['dialogues']),{str(i) for i in range(1,n+1)})
   for key in ('cn_git_blob_sha1','en_git_blob_sha1'):self.assertRegex(info[key],r'^[0-9a-f]{40}$')
 def test_new_markup(self):
  for rel,info in CH['files'].items():
   if rel in PREV['files']:continue
   x={int(i):ap.quoted_tokens(t) for i,t in info['dialogues'].items() if ap.quoted_tokens(t)}
   self.assertEqual(x,({58:['{@nickname}']} if '02-07_beg' in rel else {}))
 def test_all_dialogues_no_breaks(self):
  for info in CH['files'].values():
   for t in info['dialogues'].values():self.assertTrue(t.strip());self.assertNotRegex(t,r'[\r\n\t]')
 def test_new_speaker(self):self.assertEqual(ap.SPEAKER_RU['Operators'],'Оперативники')
 def test_allowlisted_paths(self):
  for k in ALL['files']:self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,k))
 def test_index(self):
  with (ROOT/'story/CHAPTER_2_INDEX_v025.tsv').open(encoding='utf8') as f:rows=list(csv.DictReader(f,delimiter='\t'))
  self.assertEqual(len(rows),20)
  self.assertEqual(sum(x['ru_status']=='first_draft_complete' for x in rows),20)
  self.assertEqual(sum(int(x['dialogues_ru_count']) for x in rows),1022)
 def test_review_tsv(self):
  with (ROOT/'story/STORY_CHAPTER_2_FINAL_10_RU_REVIEW_v025.tsv').open(encoding='utf8') as f:rows=list(csv.DictReader(f,delimiter='\t'))
  self.assertEqual(len(rows),426)
  self.assertTrue(all(x['review_status']=='needs_literary_review' for x in rows))
 def test_build44_synthetic_scenes_no_command_changes(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);cfg=copy.deepcopy(ALL)
   for rel,info in cfg['files'].items():
    en=['[PlayMusic(key="unchanged-source-track")]', '[Background(image="keep-bg")]']
    cn=['[PlayMusic(key="unchanged-source-track")]', '[Background(image="keep-bg")]']
    for i in range(1,info['dialogue_count']+1):
     marks=ap.quoted_tokens(info['dialogues'][str(i)])
     en.extend(['[name="Amiya"]  '+(' '.join(marks) if marks else 'Text'), '[Blocker(a=1, fadetime=0.5)]'])
     cn.extend(['[name="阿米娅"]  文字', '[Blocker(a=1, fadetime=0.5)]'])
    for lang,lines in (('en',en),('cn',cn)):
     data=('\n'.join(lines)+'\n').encode('utf8');p=root/'in'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
     info[lang+'_git_blob_sha1']=ap.git_blob_sha1(data)
   path=root/'config.json';path.write_text(json.dumps(cfg,ensure_ascii=False),encoding='utf8')
   report=ap.build(root/'in',root/'out',path)
   self.assertEqual((len(report['files']),report['lines_total']),(44,2377))
   for rel in cfg['files']:
    original=(root/'in/en'/rel).read_text('utf8').splitlines()
    result=(root/'out/ru'/rel).read_text('utf8').splitlines()
    self.assertEqual(len(original),len(result))
    self.assertEqual([s for s in original if s.startswith('[Blocker')],[s for s in result if s.startswith('[Blocker')])
    self.assertEqual([s for s in original if s.startswith('[Background')],[s for s in result if s.startswith('[Background')])
    self.assertEqual([s for s in original if s.startswith('[PlayMusic')],[s for s in result if s.startswith('[PlayMusic')])
 def test_reject_unexpected_source_version(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);rel='obt/main/level_main_02-10_end.txt';cfg={'files':{rel:ALL['files'][rel]}}
   for lang in ('en','cn'):
    p=root/'in'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('[name="Amiya"]  bad revision\n',encoding='utf8')
   path=root/'c.json';path.write_text(json.dumps(cfg,ensure_ascii=False),encoding='utf8')
   with self.assertRaisesRegex(ValueError,'Source revision mismatch'):ap.build(root/'in',root/'out',path)
   self.assertFalse((root/'out').exists())
 def test_reject_markup_change(self):
  with self.assertRaisesRegex(ValueError,'Markup/variable mismatch'):
   ap.patch_bytes(b'[name="Amiya"] hello {@nickname}\n',{'1':'Привет, Доктор!'},True)
 def test_keep_source_commands(self):
  src=b'[PlayMusic(key="track")]\n[name="Amiya"]   Hello\n[Background(image="bg") ]\n'
  patched,n=ap.patch_bytes(src,{'1':'Привет'},True)
  self.assertEqual(n,1)
  self.assertIn(b'[PlayMusic(key="track")]',patched)
  self.assertIn(b'[Background(image="bg") ]',patched)
if __name__=='__main__':unittest.main()
