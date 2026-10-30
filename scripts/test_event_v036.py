# coding: utf-8
"""Offline integrity checks for DM-3 v0.36 partial draft."""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from apply_ru_story import quoted_tokens

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class DarknightsV036(unittest.TestCase):
    def test_prior_draft_and_contiguous_prefix(self):
        old = load("events/darknights_memoir_dm3_before_partial_ru_v035.json")
        new = load("events/darknights_memoir_dm3_before_partial_ru_v036.json")
        self.assertEqual(new["version"], "v0.36-partial")
        self.assertEqual(new["source"], old["source"])
        self.assertEqual(new["source_file"], old["source_file"])
        for kind in ("dialogues", "plain_dialogues"):
            for key, value in old[kind].items():
                self.assertEqual(new[kind][key], value)
        self.assertEqual(set(new["dialogues"]), {str(i) for i in range(1, 121)})
        self.assertEqual(set(new["plain_dialogues"]), {str(i) for i in range(1, 22)})
        self.assertEqual((new["progress"]["named_ru_lines"], new["progress"]["plain_ru_lines"], new["progress"]["total_ru_lines"]), (120, 21, 141))
        self.assertEqual((new["progress"]["next_named_ordinal"], new["progress"]["next_plain_ordinal"]), (121, 22))
        self.assertFalse(new["progress"]["complete"])
        for value in list(new["dialogues"].values()) + list(new["plain_dialogues"].values()):
            self.assertTrue(isinstance(value, str) and value.strip())
            self.assertFalse(any(c in value for c in "\r\n\t"))
            self.assertEqual(quoted_tokens(value), [])

    def test_cross_file_consistency(self):
        new = load("events/darknights_memoir_dm3_before_partial_ru_v036.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v036.json")
        a = load("reports/DM3_SOURCE_AUDIT_v036.json")
        q = load("reports/QA_v036.json")
        self.assertEqual(m["next_file"], new["source_file"])
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"], 4)
        self.assertEqual(m["translation_integrity"]["darknights_ru_lines_including_partial"], 793)
        self.assertEqual(m["translation_integrity"]["darknights_partial_named_ru_lines"], 120)
        self.assertEqual((q["new_named_ru_lines"], q["new_unnamed_ru_lines"], q["new_total"]), (20, 0, 20))
        self.assertEqual((q["event_partial_ru_lines"], q["event_ru_lines_including_partial"]), (141, 793))
        self.assertFalse(q["scene_complete"])
        self.assertEqual((a["partial_translation"]["named_lines_translated"], a["partial_translation"]["plain_lines_translated"]), (120, 21))
        self.assertEqual((a["partial_translation"]["remaining_named_lines"], a["partial_translation"]["remaining_plain_lines"]), (32, 14))
        self.assertEqual(a["sources"]["cn"]["git_blob_sha1"], new["source"]["cn_git_blob_sha1"])
        self.assertEqual(a["sources"]["en"]["git_blob_sha1"], new["source"]["en_git_blob_sha1"])
        self.assertEqual((new["source"]["named_dialogue_count"], new["source"]["plain_dialogue_count"]), (152, 35))
        idx = (ROOT / "events/DARKNIGHTS_MEMOIR_INDEX_v036.tsv").read_text(encoding="utf-8")
        self.assertIn("level_act9d0_03_beg.txt\tpartial_first_draft\t120\t21", idx)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v036.json", readme)
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v035.json", readme)

    def test_new_dialogue_boundaries(self):
        new = load("events/darknights_memoir_dm3_before_partial_ru_v036.json")
        self.assertIn("регенту", new["dialogues"]["101"])
        self.assertIn("дверь", new["dialogues"]["102"])
        self.assertEqual(new["dialogues"]["111"], "…")
        self.assertIn("Терезия", new["dialogues"]["117"])
        self.assertIn("имя наёмницы", new["dialogues"]["119"])
        self.assertIn("войной", new["dialogues"]["120"])

if __name__ == "__main__":
    unittest.main()
