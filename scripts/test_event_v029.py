# coding: utf-8
import copy,json,pathlib,sys,tempfile,unittest,hashlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import apply_ru_event as e
from apply_ru_story import git_blob_sha1
NEW=json.loads((ROOT/'events/darknights_memoir_dm2_before_ru_v029.json').read_text('utf8'))
BOTH=json.loads((ROOT/'events/darknights_memoir_dm1_dm2_ru_v029.json').read_text('utf8'))
OLD=json.loads((ROOT/'events/darknights_memoir_dm1_both_ru_v028.json').read_text('utf8'))
KEY='activities/act9d0/level_act9d0_02_beg.txt'
class DarknightsV029(unittest.TestCase):
 def test_137_ru_lines_and_contiguous_keys(self):
  s=NEW['files'][KEY]
  self.assertEqual((s['dialogue_count'],s['plain_dialogue_count']),(132,5))
  self.assertEqual(set(s['dialogues']),set(map(str,range(1,133))))
  self.assertEqual(set(s['plain_dialogues']),set(map(str,range(1,6))))
 def test_exact_source_pins(self):
  s=NEW['files'][KEY]
  self.assertEqual(s['cn_git_blob_sha1'],'4442821acf5114c05819dbd18f14136cf0f440f5')
  self.assertEqual(s['en_git_blob_sha1'],'778a32130fd80ee1aaf4d78adcb4fa07f3771bb0')
 def test_previous_drafts_preserved_and_total(self):
  self.assertEqual(len(BOTH['files']),3)
  for file,spec in OLD['files'].items():self.assertEqual(BOTH['files'][file],spec)
  self.assertEqual(BOTH['files'][KEY],NEW['files'][KEY])
  self.assertEqual(sum(x['dialogue_count'] for x in BOTH['files'].values()),378)
  self.assertEqual(sum(x['plain_dialogue_count'] for x in BOTH['files'].values()),36)
 def test_content_quality_and_markup(self):
  s=NEW['files'][KEY]
  for value in list(s['dialogues'].values())+list(s['plain_dialogues'].values()):
   self.assertTrue(value.strip());self.assertNotIn('\t',value);self.assertNotIn('\n',value)
   self.assertEqual(e.quoted_tokens(value),[])
  self.assertIn('Бабель',s['dialogues']['108'])
  self.assertIn('Остов',s['dialogues']['132'])
 def test_new_speaker_supported_and_old_preserved(self):
  self.assertEqual(e.SPEAKER_EVENT_RU['Sarkaz Warrior'],'Воин-сарказ')
  self.assertEqual(e.SPEAKER_EVENT_RU['Hoederer'],'Хёдерер')
 def synth(self,rel):
  s=BOTH['files'][rel];v=rel.endswith('02_beg.txt')
  speakers=['Sarkaz Warrior','W','Hoederer','Ines'] if v else (['Ines','Hoederer','Disheveled Sarkaz Woman'] if '01_beg' in rel else ['Hoederer','W','Ines'])
  lines=['[HEADER(key="test", fit_mode="BLACK_MASK")]','[stopmusic]','[Character(name="avg_npc_333")]','[PlaySound(key="sound")]','[Blocker(a=1, r=0, g=0, b=0)]']
  lines+=['EN narrative line '+str(i) for i in range(1,s['plain_dialogue_count']+1)]
  lines+=['[Character(name="avg_npc_333")]' if i%23==0 else '' for i in range(1,s['dialogue_count']+1) if i%23==0]
  lines+=[f'[name="{speakers[(i-1)%len(speakers)]}"]   EN dialogue {i}' for i in range(1,s['dialogue_count']+1)]
  lines+=['[playMusic(intro="$darkness02_intro", key="$darkness02_loop")]','[Dialog]']
  return ('\r\n'.join(lines)+'\r\n').encode('utf8')
 def prepare(self,root):
  spec=copy.deepcopy(BOTH)
  for rel in spec['files']:
   en=self.synth(rel);cn=en.replace(b'EN dialogue',b'CN dialogue').replace(b'EN narrative',b'CN narrative')
   for lang,blob in [('en',en),('cn',cn)]:
    p=root/'sources'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
    spec['files'][rel][lang+'_git_blob_sha1']=git_blob_sha1(blob)
  cfg=root/'translation.json';cfg.write_text(json.dumps(spec,ensure_ascii=False),'utf8')
  return spec,cfg
 def test_synthetic_all_three_scenes_and_commands_preserved(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);spec,cfg=self.prepare(root)
   out=e.build(root/'sources',root/'output',cfg)
   self.assertEqual((out['files'],out['named_ru_lines'],out['plain_ru_lines']),(3,378,36))
   for rel in spec['files']:
    orig=(root/'sources/en'/rel).read_bytes();ru=(root/'output/ru'/rel).read_bytes()
    self.assertEqual(len(ru.splitlines()),len(orig.splitlines()))
    for a,b in zip(orig.decode().splitlines(),ru.decode().splitlines()):
     if a.startswith('[') and not a.startswith('[name='):self.assertEqual(a,b)
    self.assertEqual(orig,(root/'sources/en'/rel).read_bytes())
   self.assertIn('Остов?'.encode('utf8'),(root/'output/ru'/KEY).read_bytes())
   self.assertIn('Воин-сарказ'.encode('utf8'),(root/'output/ru'/KEY).read_bytes())
 def test_reject_mismatched_source_atomically(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);spec,cfg=self.prepare(root)
   (root/'sources/en'/KEY).write_bytes(b'corrupted')
   with self.assertRaisesRegex(ValueError,'revision mismatch'):e.build(root/'sources',root/'out',cfg)
   self.assertFalse((root/'out').exists())
 def test_reject_arbitrary_paths(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);spec,cfg=self.prepare(root)
   bad=copy.deepcopy(spec); bad['files']['../../arbitrary.txt']=bad['files'].pop(KEY)
   cfg.write_text(json.dumps(bad,ensure_ascii=False),'utf8')
   with self.assertRaisesRegex(ValueError,'Disallowed event file path'):e.build(root/'sources',root/'out',cfg)
 def test_preserved_story_ui_and_manifest(self):
  main=json.loads((ROOT/'story/story_main_selection_ru_v025.json').read_text('utf8'))
  ui=json.loads((ROOT/'translations/ui_keyed_all_ru.json').read_text('utf8'))
  self.assertEqual(sum(len(x['dialogues']) for x in main['files'].values()),2377)
  self.assertEqual(len(ui),2544)
  manifest=json.loads((ROOT/'chronology/CHRONOLOGY_MANIFEST_v029.json').read_text('utf8'))
  self.assertEqual(manifest['next_file'],'activities/act9d0/level_act9d0_02_end.txt')
 def test_bat_has_windows_paths(self):
  t=(ROOT/'BUILD_DARKNIGHTS_DM1_DM2_PREVIEW_v029.bat').read_text('utf8')
  self.assertIn(r'scripts\fetch_story_chapter.py',t)
  self.assertIn(r'events\darknights_memoir_dm1_dm2_ru_v029.json',t)
  self.assertNotIn('\\n',t)
if __name__=='__main__':unittest.main()
