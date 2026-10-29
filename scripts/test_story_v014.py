import json
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import apply_ru_story as m

HERE=pathlib.Path(__file__).parent

class StoryRU014Tests(unittest.TestCase):
    def setUp(self):
        self.doc=json.loads((HERE/'story_0-1_ru_v014.json').read_text('utf-8'))

    def test_counts_and_sequential_ids(self):
        self.assertEqual(sum(v['dialogue_count'] for v in self.doc['files'].values()),138)
        for v in self.doc['files'].values():
            self.assertEqual(set(v['dialogues']),set(str(i) for i in range(1,v['dialogue_count']+1)))

    def test_source_refs_complete(self):
        for _,v in self.doc['files'].items():
            self.assertRegex(v['cn_git_blob_sha1'],r'^[a-f0-9]{40}$')
            self.assertRegex(v['en_git_blob_sha1'],r'^[a-f0-9]{40}$')

    def test_variables_in_expected_dialogues(self):
        def get(suffix):return next(v['dialogues'] for path,v in self.doc['files'].items() if path.endswith(suffix))
        beg=get('beg.txt')
        end=get('end.txt')
        self.assertEqual(m.quoted_tokens(beg['54']),['{@nickname}'])
        for i in [5,20,36,62]:self.assertEqual(m.quoted_tokens(end[str(i)]),['{@nickname}'])

    def test_literals_and_empty(self):
        for cfg in self.doc['files'].values():
            for s in cfg['dialogues'].values():
                self.assertTrue(s.strip())
                self.assertNotIn('\t',s)
                self.assertNotIn('\r',s)
                self.assertNotIn('\n',s)

    def test_git_hash(self):
        self.assertEqual(m.git_blob_sha1(b'abc'), 'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f')

    def test_preserve_control_lines_and_bom(self):
        src='[HEADER(key="hello")]\r\n[name="Amiya"]  Hello {@nickname}\r\n[PlayMusic(key="bg")]\r\n'.encode('utf8')
        raw,n=m.patch_bytes(b'\xef\xbb\xbf'+src, {'1':'Привет, {@nickname}!'},True)
        self.assertEqual(n,1)
        expected=b'\xef\xbb\xbf'+'[HEADER(key="hello")]\r\n[name="Амия"]  Привет, {@nickname}!\r\n[PlayMusic(key="bg")]\r\n'.encode('utf8')
        self.assertEqual(raw,expected)

    def test_keep_english_speaker(self):
        raw,_=m.patch_bytes('[name="Dobermann"] hi\n'.encode(),{'1':'Привет'},False)
        self.assertEqual(raw.decode(),'[name="Dobermann"] Привет\n')

    def test_reject_variable_loss(self):
        with self.assertRaisesRegex(ValueError,'Markup/variable'):
            m.patch_bytes('[name="Dobermann"] hi {@nickname}\n'.encode(),{'1':'Привет'})

    def test_reject_count_mismatch(self):
        with self.assertRaisesRegex(ValueError,'Missing RU'):
            m.patch_bytes('[name="Amiya"] Hello\n'.encode(),{})

    def test_integration_two_sources_and_report(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            src=root/'sources';dest=root/'output';data={'files':{},'version':'v0.14 synthetic'}
            for stem in ['beg','end']:
                rel=f'obt/main/level_main_00-01_{stem}.txt'
                enc='[HEADER(key="x")]\n[name="Amiya"] Hi {@nickname}\n[Music(key="foo")]\n'.encode()
                cnc='[HEADER(key="x")]\n[name="阿米娅"] 你好{@nickname}\n[Music(key="foo")]\n'.encode()
                for lang,blob in [('en',enc),('cn',cnc)]:
                    file=src/lang/rel;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(blob)
                data['files'][rel]={'en_git_blob_sha1':m.git_blob_sha1(enc),'cn_git_blob_sha1':m.git_blob_sha1(cnc),'dialogue_count':1,'dialogues':{'1':'Здравствуй, {@nickname}'}}
            jsonpath=root/'translations.json';jsonpath.write_text(json.dumps(data),encoding='utf8')
            result=m.build(src,dest,jsonpath)
            self.assertEqual(result['lines_total'],2)
            self.assertEqual(len(result['files']),2)
            self.assertIn('Здравствуй', (dest/'ru/obt/main/level_main_00-01_end.txt').read_text())
            self.assertTrue((dest/'ru_preview_report.json').exists())

    def test_integration_revision_drift_refuses_writing(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            src=root/'sources';dest=root/'output';rel='obt/main/level_main_00-01_beg.txt'
            enfile=src/'en'/rel;enfile.parent.mkdir(parents=True);enfile.write_bytes(b'[name="Amiya"] wrong revision\n')
            cnfile=src/'cn'/rel;cnfile.parent.mkdir(parents=True);cnfile.write_bytes(b'[name="Amiya"] CN\n')
            fake={'version':'test','files':{rel:{'en_git_blob_sha1':'0'*40,'cn_git_blob_sha1':'0'*40,'dialogue_count':1,'dialogues':{'1':'OK'}}}}
            j=root/'translations.json';j.write_text(json.dumps(fake))
            with self.assertRaisesRegex(ValueError,'Source revision mismatch'):m.build(src,dest,j)
            self.assertFalse(dest.exists())

if __name__=='__main__':unittest.main(verbosity=2)
