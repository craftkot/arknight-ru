# coding: utf-8
import copy,hashlib,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).parent.resolve()
sys.path.insert(0,str(HERE))
import apply_ru_story as engine
import fetch_story_chapter as fetchall
OLD='story_main_selection_ru_v019.json'
NEW='story_main_selection_ru_v020.json'
REL='obt/main/level_main_00-11_end.txt'
class ChapterZeroV020(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=json.loads((HERE/OLD).read_text('utf8'))
  cls.new=json.loads((HERE/NEW).read_text('utf8'))
 def test_previous_sources_and_translations_unchanged(self):
  self.assertEqual(self.old['files'],{k:v for k,v in self.new['files'].items() if k in self.old['files']})
 def test_chapter_complete_twelve(self):
  self.assertEqual(len(self.new['files']),12)
  self.assertEqual(sum(v['dialogue_count'] for v in self.new['files'].values()),654)
  self.assertEqual(self.new['files'][REL]['dialogue_count'],60)
 def test_all_sixty_russian_lines_have_ordinal(self):
  entries=self.new['files'][REL]['dialogues']
  self.assertEqual(set(entries),set(map(str,range(1,61))))
  self.assertTrue(all(bool(x.strip()) for x in entries.values()))
  self.assertTrue(all(not any(c in x for c in '\n\r\t') for x in entries.values()))
 def test_critical_source_sha(self):
  self.assertEqual(self.new['files'][REL]['cn_git_blob_sha1'],'60f8817da1607b34e205386e8884198d2fea33d3')
  self.assertEqual(self.new['files'][REL]['en_git_blob_sha1'],'f7c700d91db1a52a0740fcc50a49e509461ebf5f')
 def test_nickname_token(self):
  self.assertEqual(engine.quoted_tokens(self.new['files'][REL]['dialogues']['44']),['{@nickname}'])
 def test_talulah_canon(self):
  self.assertIn('Талул',self.new['files'][REL]['dialogues']['52'])
 def test_accepted_story_file_path(self):
  self.assertRegex(REL,engine.ALLOWED_PATH)
  self.assertNotRegex('obt/main/../hack.txt',engine.ALLOWED_PATH)
 def test_full_chapter_mocked_preview(self):
  with tempfile.TemporaryDirectory() as temp:
   t=pathlib.Path(temp);entries={}
   for rel,cfg in self.new['files'].items():
    cn=['[HEADER(test=1)]','[PlayMusic(key="original")]']
    en=['[HEADER(test=1)]','[PlayMusic(key="original")]']
    for i in range(1,cfg['dialogue_count']+1):
     tokens=engine.quoted_tokens(cfg['dialogues'][str(i)])
     en.append('[name="Nearl"]  English '+(' '.join(tokens) if tokens else 'placeholder'))
     cn.append('[name="临光"]  中文')
     en.append('[Background(image="keep")]');cn.append('[Background(image="keep")]')
    en_b=('\r\n'.join(en)+'\r\n').encode('utf8');cn_b=('\r\n'.join(cn)+'\r\n').encode('utf8')
    for lang,buf in [('cn',cn_b),('en',en_b)]:
     p=t/'src'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(buf)
    upd=copy.deepcopy(cfg);upd['cn_git_blob_sha1']=engine.git_blob_sha1(cn_b);upd['en_git_blob_sha1']=engine.git_blob_sha1(en_b)
    entries[rel]=upd
   path=t/'cfg.json';path.write_text(json.dumps({'version':'synthetic','files':entries},ensure_ascii=False),'utf8')
   report=engine.build(t/'src',t/'out',path)
   self.assertEqual(report['lines_total'],654)
   self.assertEqual(len(report['files']),12)
   for rel in entries:
    s=(t/'out/ru'/rel).read_text('utf8')
    self.assertIn('[PlayMusic(key="original")]',s)
    self.assertEqual(s.count('[Background(image="keep")]'),entries[rel]['dialogue_count'])
 def test_batch_fetch_preflights_all_sources_before_write(self):
  with tempfile.TemporaryDirectory() as temp:
   t=pathlib.Path(temp);p=t/'translations.json'
   b='[name="Nearl"]  Hi\n'.encode('utf8')
   dat={'files':{'obt/main/level_main_00-11_end.txt':{'cn_git_blob_sha1':engine.git_blob_sha1(b),'en_git_blob_sha1':engine.git_blob_sha1(b)},'obt/main/level_main_00-09_end.txt':{'cn_git_blob_sha1':engine.git_blob_sha1(b),'en_git_blob_sha1':'0'*40}}}
   p.write_text(json.dumps(dat),'utf8')
   with patch.object(fetchall,'get_source',return_value=b):
    with self.assertRaisesRegex(ValueError,'revision mismatch'):
     fetchall.fetch_all(p,t/'out')
   self.assertFalse((t/'out/cn/obt/main/level_main_00-11_end.txt').exists())
 def test_batch_fetch_keeps_reused_valid_file(self):
  with tempfile.TemporaryDirectory() as temp:
   t=pathlib.Path(temp);p=t/'input.json';b=b'[name="Nearl"]  Hi\n';sha=engine.git_blob_sha1(b)
   p.write_text(json.dumps({'files':{REL:{'cn_git_blob_sha1':sha,'en_git_blob_sha1':sha}}}),'utf8')
   with patch.object(fetchall,'get_source',return_value=b):
    x=fetchall.fetch_all(p,t/'output')
   self.assertEqual(x['sources_checked'],2)
   for lang in ('cn','en'):self.assertEqual((t/'output'/lang/REL).read_bytes(),b)
if __name__=='__main__':unittest.main()
