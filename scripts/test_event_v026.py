# coding: utf-8
import copy,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import apply_ru_event as e
from apply_ru_story import git_blob_sha1
SRC=json.loads((ROOT/'events/darknights_memoir_dm1_before_ru_v026.json').read_text('utf8'))
OLD=json.loads((ROOT/'story/story_main_selection_ru_v025.json').read_text('utf8'))
K='activities/act9d0/level_act9d0_01_beg.txt'
class DM1(unittest.TestCase):
 def test_first_scene_110_lines(self):
  self.assertEqual((len(SRC['files'][K]['dialogues']),len(SRC['files'][K]['plain_dialogues'])),(94,16))
 def test_exact_revision_blobs(self):
  x=SRC['files'][K];self.assertEqual(x['cn_git_blob_sha1'],'e83034b8bfd59bb3f66632f2ccfa5423005440f7');self.assertEqual(x['en_git_blob_sha1'],'c1b956f58a66f2f9a8c06b1f4253c8044a6c4fe9')
 def test_all_ordinals_present(self):
  x=SRC['files'][K]
  for cat,n in [('dialogues',94),('plain_dialogues',16)]:self.assertEqual(set(x[cat]),{str(i) for i in range(1,n+1)})
 def test_no_markup_or_newlines_in_translation(self):
  x=SRC['files'][K]
  for t in list(x['dialogues'].values())+list(x['plain_dialogues'].values()):
   self.assertTrue(t.strip());self.assertNotIn('\n',t);self.assertNotIn('\r',t);self.assertNotIn('\t',t);self.assertEqual(e.quoted_tokens(t),[])
 def test_unmatched_tags_cannot_pass(self):
  x=copy.deepcopy(SRC['files'][K]);raw=self.make_en()
  x['dialogues']['2']='{@nickname} текст'
  with self.assertRaisesRegex(ValueError,'Markup mismatch'):e.patch(raw,x)
 def test_new_name_localized(self):
  self.assertEqual(e.SPEAKER_EVENT_RU['Hoederer'],'Хёдерер')
  self.assertEqual(e.SPEAKER_EVENT_RU['Ines'],'Инес')
 def make_en(self):
  p=['[PlayMusic(key="original-music")]', '[Background(image="original-background")]','[Dialog]', '[Blocker(x=1)]']
  p += ['EN plain text ' + str(i) for i in range(1,9)]
  p += ['[name="Ines"]  EN named dialogue '+str(i) for i in range(1,94)]
  p += ['[name="Hoederer"]  EN named dialogue 94']
  p += ['EN narrative text ' + str(i) for i in range(9,17)]
  return ('\r\n'.join(p)+'\r\n').encode('utf8')
 def test_preserves_controls_and_plain_dialogue(self):
  raw=self.make_en();patched=e.patch(raw,SRC['files'][K]);o=raw.decode().splitlines();t=patched.decode().splitlines()
  self.assertEqual(len(o),len(t));self.assertEqual(o[:4],t[:4]);self.assertIn('Это я.',t);self.assertIn('Она станет одним из лучших воинов-сарказов.',t)
  self.assertIn('[name="Хёдерер"]  …«W».',t)
  self.assertNotIn('EN plain text 1',t)
 def test_build_and_reject_tamper(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);cfg=copy.deepcopy(SRC);en=self.make_en();cn=en.replace(b'Ines',b'Baba')
   for lang,data in [('en',en),('cn',cn)]:
    p=root/'src'/lang/K;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    cfg['files'][K][lang+'_git_blob_sha1']=git_blob_sha1(data)
   config=root/'translation.json';config.write_text(json.dumps(cfg,ensure_ascii=False),'utf8')
   output=e.build(root/'src',root/'out',config)
   self.assertEqual((output['files'],output['named_ru_lines'],output['plain_ru_lines']),(1,94,16))
   self.assertEqual((root/'src/en'/K).read_bytes(),en)
   self.assertTrue((root/'out/ru'/K).is_file())
   (root/'src/en'/K).write_bytes(en+b'X')
   with self.assertRaisesRegex(ValueError,'Source revision mismatch'):e.build(root/'src',root/'out2',config)
 def test_directory_escape_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);cfg=copy.deepcopy(SRC);cfg['files']['../bad.txt']=cfg['files'].pop(K)
   p=root/'bad.json';p.write_text(json.dumps(cfg),'utf8')
   with self.assertRaisesRegex(ValueError,'Disallowed event'):e.build(root/'src',root/'out',p)
 def test_mainstory_untouched(self):
  old=json.loads((ROOT/'story/story_main_selection_ru_v025.json').read_text('utf8'))
  self.assertEqual(OLD,old);self.assertEqual(len(old['files']),44)
