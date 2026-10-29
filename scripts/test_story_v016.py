import copy
import json
import pathlib
import re
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import apply_ru_story as m
ROOT=pathlib.Path(__file__).resolve().parent

class Story016(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new=json.loads((ROOT/'story_0-4_0-6_ru_v016.json').read_text('utf-8'))
        cls.full=json.loads((ROOT/'story_main_selection_ru_v016.json').read_text('utf-8'))
        cls.old=json.loads((ROOT/'story_main_0-1_0-2_ru_v015.json').read_text('utf-8'))

    def test_counts_all(self):
        self.assertEqual([cfg['dialogue_count'] for cfg in self.new['files'].values()],[48,30])
        self.assertEqual(sum(cfg['dialogue_count'] for cfg in self.full['files'].values()),315)
        self.assertEqual(len(self.full['files']),6)
        for cfg in self.full['files'].values():
            self.assertEqual(set(cfg['dialogues']),{str(i) for i in range(1,cfg['dialogue_count']+1)})
            for txt in cfg['dialogues'].values():
                self.assertIsInstance(txt,str)
                self.assertTrue(txt.strip())
                self.assertNotIn('\n',txt)
                self.assertNotIn('\t',txt)

    def test_old_translations_preserved(self):
        for k,cfg in self.old['files'].items():
            self.assertEqual(cfg,self.full['files'][k])

    def test_chinese_context_beasts(self):
        texts=self.new['files']['obt/main/level_main_00-04_beg.txt']['dialogues']
        self.assertIn('зверей', texts['31'])
        self.assertIn('места встречи',texts['38'])
        self.assertIn('Эйс',m.SPEAKER_RU['Ace'])

    def test_pseudo_full_script_preserves_controls(self):
        for rel,cfg in self.new['files'].items():
            names=['Ace','Dobermann','Amiya','Reunion Member','Guard']
            en='[HEADER(key="intro")]\r\n[PlayMusic(key="test")]\r\n'
            for n in range(1,cfg['dialogue_count']+1):
                name=names[n%len(names)]
                token='Dr.{@nickname}' if rel.endswith('04_beg.txt') and n in {8,14,30,48} else 'plain'
                en+=f'[name="{name}"]  {token}\r\n'
                en+='[Background(image="unchanged")]\r\n'
            ru=copy.deepcopy(cfg['dialogues'])
            b,count=m.patch_bytes(en.encode('utf-8'),ru)
            self.assertEqual(count,cfg['dialogue_count'])
            txt=b.decode('utf8')
            self.assertEqual(txt.count('[PlayMusic('),1)
            self.assertEqual(txt.count('[Background('),cfg['dialogue_count'])
            self.assertEqual(txt.count('\r\n'),en.count('\r\n'))
            self.assertNotIn('[name="Ace"]',txt)

    def test_revisions_are_pinned(self):
        for cfg in self.new['files'].values():
            self.assertRegex(cfg['cn_git_blob_sha1'],r'^[0-9a-f]{40}$')
            self.assertRegex(cfg['en_git_blob_sha1'],r'^[0-9a-f]{40}$')

    def test_unauthorized_script_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            cfg=list(self.new['files'].values())[0]
            payload={'files':{'obt/main/../../x.txt':cfg}}
            p=root/'tr.json';p.write_text(json.dumps(payload),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Unexpected or unsafe'):
                m.build(root/'src',root/'out',p)
            self.assertFalse((root/'out').exists())

    def test_synthetic_full_build_rev_pins(self):
        # Two actual new stages, simulated upstream files with independent hashes.
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            config={}
            for rel,cfg in self.new['files'].items():
                names=['Ace','Dobermann','Amiya','Guard','Reunion Member']
                en=('[HEADER(key="x")]\n[PlayMusic(key="bgm")]\n'+''.join(
                    f'[name="{names[i%len(names)]}"]  '+('Dr.{@nickname}' if rel.endswith('04_beg.txt') and i+1 in (8,14,30,48) else 'test')+'\n[Background(image="bg")]\n'
                    for i in range(cfg['dialogue_count']))).encode('utf8')
                cn=('[HEADER(key="x")]\n[PlayMusic(key="bgm")]\n'+''.join(
                    '[name="杜宾"]  测试\n[Background(image="bg")]\n' for i in range(cfg['dialogue_count']))).encode('utf8')
                for lang,raw in [('en',en),('cn',cn)]:
                    p=root/'source'/lang/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
                cur=copy.deepcopy(cfg)
                cur['en_git_blob_sha1']=m.git_blob_sha1(en)
                cur['cn_git_blob_sha1']=m.git_blob_sha1(cn)
                config[rel]=cur
            tr=root/'new.json';tr.write_text(json.dumps({'files':config},ensure_ascii=False),encoding='utf8')
            report=m.build(root/'source',root/'result',tr)
            self.assertEqual(report['lines_total'],78)
            self.assertEqual(len(report['files']),2)
            for rel in config:
                output=(root/'result'/'ru'/rel).read_text('utf8')
                self.assertIn('[PlayMusic(key="bgm")]',output)
                self.assertIn('[Background(image="bg")]',output)
                self.assertIn('Эйс',output)

if __name__=='__main__':unittest.main(verbosity=2)
