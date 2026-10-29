import json
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import apply_ru_story as m
ROOT=pathlib.Path(__file__).resolve().parent

class Stage0_2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/'story_0-2_ru_v015.json').read_text('utf-8'))
        cls.both=json.loads((ROOT/'story_main_0-1_0-2_ru_v015.json').read_text('utf-8'))
    def test_stage_02_count(self):
        self.assertEqual(sum(v['dialogue_count'] for v in self.doc['files'].values()),99)
        self.assertEqual([v['dialogue_count'] for v in self.doc['files'].values()],[48,51])
        for v in self.doc['files'].values():
            self.assertEqual(set(v['dialogues']),{str(i) for i in range(1,v['dialogue_count']+1)})
    def test_project_combined_count(self):
        self.assertEqual(sum(v['dialogue_count'] for v in self.both['files'].values()),237)
        self.assertEqual(len(self.both['files']),4)
    def test_source_hashes(self):
        for v in self.doc['files'].values():
            self.assertRegex(v['cn_git_blob_sha1'],r'^[a-f0-9]{40}$')
            self.assertRegex(v['en_git_blob_sha1'],r'^[a-f0-9]{40}$')
    def test_story_variables(self):
        for cfg in self.doc['files'].values():
            for line in cfg['dialogues'].values():
                self.assertNotIn('\n',line)
                self.assertNotIn('\t',line)
                self.assertNotIn('{@nickname}',line)
    def test_stage_01_unchanged(self):
        old=json.loads((ROOT/'story_0-1_ru_v014.json').read_text('utf-8'))
        for key,orig in old['files'].items():
            self.assertEqual(self.both['files'][key],orig)
    def test_new_speakers(self):
        self.assertEqual(m.SPEAKER_RU['TV Host'],'Телеведущий')
        self.assertIn('Урсуса',m.SPEAKER_RU['Ursus Captain'])
        sample='[PlayMusic(key="good")]\n[name="Ursus Captain"]  ENGLISH\n[Character(name="other")]\n[name="TV Host"] ENGLISH 2\n'
        x,n=m.patch_bytes(sample.encode('utf8'),{'1':'Русский!', '2':'Новости'},True)
        ss=x.decode()
        self.assertEqual(n,2)
        self.assertIn('[PlayMusic(key="good")]',ss)
        self.assertIn('[Character(name="other")]',ss)
        self.assertIn('[name="Телеведущий"]',ss)
        self.assertIn('[name="Капитан военной полиции Урсуса"]',ss)
        self.assertNotIn('ENGLISH',ss)
    def test_no_install_side_effect(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            rel='obt/main/level_main_00-02_beg.txt'
            en='[HEADER(key="x")]\n[name="TV Host"] News\n[PlayMusic(key="foo")]\n'.encode()
            cn='[HEADER(key="x")]\n[name="电视主持人"] 新闻\n[PlayMusic(key="foo")]\n'.encode()
            for lang,blob in [('en',en),('cn',cn)]:
                f=root/'source'/lang/rel;f.parent.mkdir(parents=True);f.write_bytes(blob)
            payload={'version':'test', 'files':{rel:{'cn_git_blob_sha1':m.git_blob_sha1(cn),'en_git_blob_sha1':m.git_blob_sha1(en),'dialogue_count':1,'dialogues':{'1':'Новости'}}}}
            f=root/'tiny.json';f.write_text(json.dumps(payload),encoding='utf8')
            report=m.build(root/'source',root/'result',f)
            self.assertEqual(report['lines_total'],1)
            self.assertEqual((root/'source/en'/rel).read_bytes(),en)
            result=(root/'result/ru'/rel).read_text('utf-8')
            self.assertIn('[HEADER(key="x")]',result)
            self.assertIn('[PlayMusic(key="foo")]',result)
            self.assertIn('[name="Телеведущий"] Новости',result)
    def test_reject_wrong_version_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            rel='obt/main/level_main_00-02_end.txt'
            p=root/'source/en'/rel;p.parent.mkdir(parents=True);p.write_text('[name="Amiya"] Hi')
            p=root/'source/cn'/rel;p.parent.mkdir(parents=True);p.write_text('[name="阿米娅"] 你好')
            doc={'files':{rel:{'en_git_blob_sha1':'0'*40,'cn_git_blob_sha1':'0'*40,'dialogue_count':1,'dialogues':{'1':'Привет'}}}}
            q=root/'x.json';q.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError,'revision mismatch'):
                m.build(root/'source',root/'result',q)
            self.assertFalse((root/'result').exists())
    def test_reject_unauthorized_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            doc={'files':{'obt/main/level_main_09-99_beg.txt':{'en_git_blob_sha1':'0'*40,'cn_git_blob_sha1':'0'*40,'dialogue_count':1,'dialogues':{'1':'Привет'}}}}
            p=root/'bad.json';p.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError,'Unexpected or unsafe'):
                m.build(root/'source',root/'result',p)
    def test_select_chinese_nuance(self):
        beg=self.doc['files']['obt/main/level_main_00-02_beg.txt']['dialogues']
        self.assertIn('родителей',beg['17'])
        self.assertIn('никаких доказательств',beg['40'].lower())
        end=self.doc['files']['obt/main/level_main_00-02_end.txt']['dialogues']
        self.assertIn('крольчиха',end['36'])

if __name__=='__main__': unittest.main(verbosity=2)
