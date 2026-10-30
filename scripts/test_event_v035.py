# coding: utf-8
"""Offline cumulative integrity checks for DM-3 v0.35 partial draft."""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from apply_ru_story import quoted_tokens

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class DarknightsV035(unittest.TestCase):
    def test_prior_lines_unchanged_and_new_prefix(self):
        old = load("events/darknights_memoir_dm3_before_partial_ru_v034.json")
        new = load("events/darknights_memoir_dm3_before_partial_ru_v035.json")
        self.assertEqual(new["version"], "v0.35-partial")
        self.assertEqual(new["source"], old["source"])
        self.assertEqual(new["source_file"], old["source_file"])
        for kind in ("dialogues", "plain_dialogues"):
            for key, text in old[kind].items():
                self.assertEqual(new[kind][key], text)
        self.assertEqual(set(new["dialogues"]), {str(i) for i in range(1, 101)})
        self.assertEqual(set(new["plain_dialogues"]), {str(i) for i in range(1, 22)})
        self.assertEqual((new["progress"]["named_ru_lines"], new["progress"]["plain_ru_lines"], new["progress"]["total_ru_lines"]), (100, 21, 121))
        self.assertEqual((new["progress"]["next_named_ordinal"], new["progress"]["next_plain_ordinal"]), (101, 22))
        self.assertFalse(new["progress"]["complete"])
        self.assertEqual(new["format"], "partial_translation_work_in_progress")
        for value in list(new["dialogues"].values()) + list(new["plain_dialogues"].values()):
            self.assertIsInstance(value, str)
            self.assertTrue(value.strip())
            self.assertFalse(any(c in value for c in "\r\n\t"))
            self.assertEqual(quoted_tokens(value), [])

    def test_cross_file_counts_and_source_hashes(self):
        doc = load("events/darknights_memoir_dm3_before_partial_ru_v035.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v035.json")
        q = load("reports/QA_v035.json")
        a = load("reports/DM3_SOURCE_AUDIT_v035.json")
        self.assertEqual(m["next_file"], doc["source_file"])
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"], 4)
        self.assertEqual(m["translation_integrity"]["darknights_ru_lines_including_partial"], 773)
        self.assertEqual(m["translation_integrity"]["darknights_partial_named_ru_lines"], 100)
        self.assertEqual(m["translation_integrity"]["darknights_partial_plain_ru_lines"], 21)
        self.assertEqual((q["new_named_ru_lines"], q["new_unnamed_ru_lines"], q["new_total"]), (48, 0, 48))
        self.assertEqual((q["event_partial_ru_lines"], q["event_ru_lines_including_partial"]), (121, 773))
        self.assertFalse(q["scene_complete"])
        self.assertEqual((a["partial_translation"]["named_lines_translated"], a["partial_translation"]["plain_lines_translated"]), (100, 21))
        self.assertEqual((a["partial_translation"]["remaining_named_lines"], a["partial_translation"]["remaining_plain_lines"]), (52, 14))
        self.assertEqual(a["sources"]["cn"]["git_blob_sha1"], doc["source"]["cn_git_blob_sha1"])
        self.assertEqual(a["sources"]["en"]["git_blob_sha1"], doc["source"]["en_git_blob_sha1"])
        self.assertEqual((doc["source"]["named_dialogue_count"], doc["source"]["plain_dialogue_count"]), (152, 35))
        idx = (ROOT / "events/DARKNIGHTS_MEMOIR_INDEX_v035.tsv").read_text(encoding="utf-8")
        self.assertIn("level_act9d0_03_beg.txt\tpartial_first_draft\t100\t21", idx)
        self.assertIn("level_act9d0_03_end.txt\tnot_translated\t0\t0", idx)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v035.json", readme)
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v034.json", readme)

    def test_new_dialogue_boundaries(self):
        doc = load("events/darknights_memoir_dm3_before_partial_ru_v035.json")
        self.assertEqual(doc["dialogues"]["53"], "М?")
        self.assertIn("Клоужер", doc["dialogues"]["54"])
        self.assertIn("Терезией", doc["dialogues"]["79"])
        self.assertIn("Родос Айленд", doc["dialogues"]["98"])
        self.assertTrue(doc["dialogues"]["63"].endswith("—"))
        self.assertTrue(doc["dialogues"]["64"].startswith("—"))
        self.assertEqual(doc["plain_dialogues"]["21"], "Да почему опять заклинило?!")

if __name__ == "__main__":
    unittest.main()
