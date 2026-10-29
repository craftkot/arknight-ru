#!/usr/bin/env python3
import hashlib
import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import Mock
from io import BytesIO
P=pathlib.Path(__file__).resolve().parent/'fetch_story_pair.py'
spec=importlib.util.spec_from_file_location('story_fetch',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Resp:
 def __init__(self,link,b): self.link=link;self.buf=BytesIO(b)
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def geturl(self):return self.link
 def read(self,n):return self.buf.read(n)
class T(unittest.TestCase):
 def test_paths(self):
  self.assertEqual(m.clean_relative('obt/main/level_main_00-01_beg.txt'),'obt/main/level_main_00-01_beg.txt')
  for p in ['/etc/passwd','../../abc.txt','obt/main/../../../a.txt','https://exmpl.com/a.txt','a.txt','obt/main/file.json']:
   with self.assertRaises(ValueError):m.clean_relative(p)
 def test_download_two_languages_and_metadata(self):
  def opener(req,timeout):
   url=req.full_url
   return Resp(url, b'[name="Dobermann"] Hello\n' if 'en_US' in url else '[name="杜宾"] 你好\n'.encode('utf8'))
  with tempfile.TemporaryDirectory() as d:
   meta=m.download('obt/main/level_main_00-01_beg.txt',d,opener)
   self.assertEqual(len(meta['files']),2)
   self.assertEqual(hashlib.sha256((pathlib.Path(d)/'en/obt/main/level_main_00-01_beg.txt').read_bytes()).hexdigest(),meta['files']['en']['sha256'])
   self.assertTrue((pathlib.Path(d)/'source_manifest.json').exists())
   self.assertEqual(len(m.download('obt/main/level_main_00-01_beg.txt',d,opener)['files']),2)
   self.assertEqual(len(__import__('json').loads((pathlib.Path(d)/'source_manifest.json').read_text())['pairs']),1)
 def test_disallowed_redirect(self):
  with self.assertRaises(ValueError):m.get_source('https://raw.githubusercontent.com/something', lambda r,timeout: Resp('https://notgithub.org/a',b'[name="X"] Hi'))
 def test_size_limit(self):
  with self.assertRaises(ValueError):m.get_source('https://raw.githubusercontent.com/x',lambda r,timeout:Resp('https://raw.githubusercontent.com/x',b'[name="X"] Hi'+b'x'*(m.MAX_BYTES+10)))
if __name__=='__main__':unittest.main(verbosity=2)
