# coding: utf-8
"""Ensure v0.48 BepInEx overlay is safe to extract and respects 489 existing keys."""
import hashlib
import pathlib
import sys
import tempfile
import unittest
import zipfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import build_bepinex_dropin_v048 as overlay

class BepInExOverlayV048(unittest.TestCase):
    def test_existing_fingerprint_count(self):
        self.assertEqual(len(overlay.get_existing_hashes()),489)

    def test_zip_safe_and_does_not_overwrite_current_7_txt(self):
        with tempfile.TemporaryDirectory() as directory:
            result=overlay.build(directory)
            target=pathlib.Path(directory)/result["artifact"]
            self.assertTrue(target.exists())
            self.assertEqual(result["existing_uploaded_txt_count"],7)
            self.assertEqual(result["available_repository_literal_keys"],1312)
            self.assertGreaterEqual(result["additional_xunity_literal_mappings"],500)
            self.assertEqual(
                result["additional_xunity_literal_mappings"]+result["skipped_existing_keys"],
                1312)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),result["sha256"])
            with zipfile.ZipFile(target) as z:
                self.assertEqual(set(z.namelist()),{
                    "BepInEx/Translation/ru/Text/ArknightsRU_ExpandedUI_v048.txt",
                    "README_BEPINEX_RU_v048.md"})
                for file in z.namelist():
                    self.assertFalse(file.startswith("/") or ".." in file.split("/"))
                    self.assertFalse(file.lower().endswith((".exe",".dll",".apk")))
                contents=z.read(overlay.DEST).decode("utf-8")
                entries=[line for line in contents.splitlines() if line and not line.startswith("#")]
                self.assertEqual(len(entries),result["additional_xunity_literal_mappings"])
                keys=[x.split("=",1)[0] for x in entries]
                self.assertEqual(len(set(keys)),len(keys))
                self.assertTrue(all("=" in x for x in entries))
                old=overlay.get_existing_hashes()
                self.assertFalse(any(
                    hashlib.sha256(key.encode("utf-8")).digest()[:6] in old for key in keys))
                self.assertIn("BepInEx",z.read("README_BEPINEX_RU_v048.md").decode("utf-8"))

    def test_original_repo_source_unchanged(self):
        original=(ROOT/"translations/xunity_LITERAL_SAFE_PREVIEW.txt").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            overlay.build(tmp)
        self.assertEqual((ROOT/"translations/xunity_LITERAL_SAFE_PREVIEW.txt").read_bytes(),original)
if __name__=="__main__":
    unittest.main()
