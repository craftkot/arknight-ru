# coding: utf-8
"""Offline integrity checks for the incremental DM-3 partial draft v0.32."""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from apply_ru_story import quoted_tokens

def read_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf8"))

class DarknightsV032(unittest.TestCase):
    def test_increment_is_exact_and_preserves_prior_translation(self):
        old = read_json("events/darknights_memoir_dm3_before_partial_ru_v031.json")
        new = read_json("events/darknights_memoir_dm3_before_partial_ru_v032.json")
        self.assertEqual(new["version"], "v0.32-partial")
        self.assertEqual(new["source"], old["source"])
        self.assertEqual(new["source_file"], old["source_file"])
        self.assertEqual(new["dialogues"], old["dialogues"])
        self.assertEqual(new["source"]["named_dialogue_count"], 152)
        self.assertEqual(new["source"]["plain_dialogue_count"], 35)
        self.assertEqual({k: new["plain_dialogues"][k] for k in old["plain_dialogues"]}, old["plain_dialogues"])
        self.assertEqual(set(new["plain_dialogues"]), {str(i) for i in range(1, 18)})
        self.assertEqual(new["progress"]["named_ru_lines"], 0)
        self.assertEqual(new["progress"]["plain_ru_lines"], 17)
        self.assertEqual(new["progress"]["total_ru_lines"], 17)
        self.assertEqual(new["progress"]["next_plain_ordinal"], 18)
        self.assertEqual(new["progress"]["completed_plain_ordinals"], "1-17")
        self.assertFalse(new["progress"]["complete"])
        self.assertEqual(new["format"], "partial_translation_work_in_progress")
        for v in new["plain_dialogues"].values():
            self.assertIsInstance(v, str)
            self.assertTrue(v.strip())
            self.assertFalse(any(c in v for c in "\r\n\t"))
            self.assertEqual(quoted_tokens(v), [])

    def test_progress_is_consistent_across_metadata(self):
        manifest = read_json("chronology/CHRONOLOGY_MANIFEST_v032.json")
        qa = read_json("reports/QA_v032.json")
        audit = read_json("reports/DM3_SOURCE_AUDIT_v032.json")
        integ = manifest["translation_integrity"]
        self.assertEqual(manifest["next_file"], "activities/act9d0/level_act9d0_03_beg.txt")
        self.assertEqual(integ["darknights_completed_files"], 4)
        self.assertEqual(integ["darknights_partial_plain_ru_lines"], 17)
        self.assertEqual(integ["darknights_ru_lines_including_partial"], 669)
        self.assertEqual((qa["event_completed_scripts_ru_lines"], qa["event_partial_ru_lines"]), (652, 17))
        self.assertEqual(qa["event_ru_lines_including_partial"], 669)
        self.assertFalse(qa["scene_complete"])
        self.assertEqual(audit["partial_translation"]["plain_lines_translated"], 17)
        self.assertEqual(audit["partial_translation"]["remaining_plain_lines"], 18)
        self.assertEqual(audit["partial_translation"]["file"], "events/darknights_memoir_dm3_before_partial_ru_v032.json")
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"], "538c852f8a64981df34f7699be9f73dfe00873ea")
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"], "37dcf8c721efd0fa5068d18146caae45ba200b70")
        index = (ROOT / "events/DARKNIGHTS_MEMOIR_INDEX_v032.tsv").read_text(encoding="utf8")
        self.assertIn("level_act9d0_03_beg.txt\tpartial_first_draft\t0\t17", index)
        self.assertIn("level_act9d0_03_end.txt\tnot_translated\t0\t0", index)
        readme = (ROOT / "README.md").read_text(encoding="utf8")
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v032.json", readme)

if __name__ == "__main__":
    unittest.main()
