# coding: utf-8
"""v0.52 XUnity unified UI overlay: regression, dedup, categorized archive tests."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import build_bepinex_unified_v052 as pack

class BepInExUnifiedV052(unittest.TestCase):
    def test_mapping_complete_and_conflict_free(self):
        orig=pack.load_original()
        curated=pack.load_curated()
        self.assertEqual(len(orig),1312)
        self.assertGreaterEqual(len(curated),145)
        protected=pack.old_key_hashes()
        self.assertEqual(len(protected),489)
        folders,coverage,report=pack.assemble()
        self.assertEqual(len(folders),8)
        self.assertGreater(report["additional_translation_keys"],950)
        self.assertEqual(sum(len(x) for x in folders),report["additional_translation_keys"])
        keys=[k for group in folders for k,v in group]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertFalse(any(pack.digest(k) in protected for k in keys))
        self.assertTrue(all(k not in keys for k in ("ON","OFF","Full","Free")))
        self.assertGreaterEqual(report["screen_terms_mapped_or_existing"],40)
        self.assertIn(coverage["Terminal"],("included_in_v052","present_in_original_user_TXT"))
        self.assertIn(coverage["Rarity"],("included_in_v052","present_in_original_user_TXT"))
        self.assertIn(coverage["Leave the Base?"],("included_in_v052","present_in_original_user_TXT"))

    def test_zip_contains_only_eight_translations_and_safe_backup(self):
        with tempfile.TemporaryDirectory() as t:
            report=pack.build(t)
            path=Path(t)/pack.NAME
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),report["sha256"])
            self.assertTrue((Path(t)/(pack.NAME+".sha256")).is_file())
            with zipfile.ZipFile(path) as z:
                names=set(z.namelist())
                expected={pack.PREFIX+x for x in pack.DESTS}
                self.assertTrue(expected.issubset(names))
                self.assertEqual(len(names),11)
                self.assertIn("README_UNIFIED_RU.md",names)
                self.assertIn("BACKUP_OLD_OVERLAYS_v052.cmd",names)
                self.assertIn("AUDIT_SCREEN_LABELS_v052.json",names)
                all_keys=[]
                for name in expected:
                    lines=z.read(name).decode("utf-8").splitlines()
                    lines=[ln for ln in lines if ln and not ln.startswith("#")]
                    for line in lines:
                        self.assertIn("=",line)
                        key,val=line.split("=",1)
                        self.assertTrue(key and val.strip())
                        all_keys.append(key)
                self.assertEqual(len(all_keys),len(set(all_keys)))
                self.assertEqual(len(all_keys),report["additional_translation_keys"])
                self.assertFalse(any(x.startswith("/") or ".." in x.split("/") for x in names))
                self.assertFalse(any(x.lower().endswith((".dll",".exe",".apk")) for x in names))
                for original in ("ArknightsRU_UI.txt","ArknightsRU_Additional.txt",
                                 "ArknightsRU_OperatorLines.txt","ArknightsRU_ItemsAndCombat.txt",
                                 "_Substitutions.txt","_Preprocessors.txt","_Postprocessors.txt"):
                    self.assertFalse(any(x.endswith("/"+original) for x in names))
                script=z.read("BACKUP_OLD_OVERLAYS_v052.cmd").decode("utf-8")
                self.assertNotIn(" del ",script.lower())
                self.assertNotIn("rmdir",script.lower())
                for legacy in pack.LEGACY:self.assertIn(legacy,script)
                audit=json.loads(z.read("AUDIT_SCREEN_LABELS_v052.json"))
                self.assertEqual(len(audit),len(pack.SCREEN_CHECKS))

    def test_does_not_modify_sources(self):
        a=ROOT/"translations/xunity_LITERAL_SAFE_PREVIEW.txt"
        b=ROOT/"translations/xunity_screen_labels_curated_v052.json"
        before=(hashlib.sha256(a.read_bytes()).hexdigest(),hashlib.sha256(b.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as t:pack.build(t)
        self.assertEqual(before,(hashlib.sha256(a.read_bytes()).hexdigest(),hashlib.sha256(b.read_bytes()).hexdigest()))
if __name__=="__main__":
    unittest.main()
