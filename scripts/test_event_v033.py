# coding: utf-8
"""Offline integrity tests for cumulative DM-3 v0.33 partial draft."""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from apply_ru_story import quoted_tokens

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf8"))

class DarknightsV033(unittest.TestCase):
    def test_increment_preserves_previous_version(self):
        old = load("events/darknights_memoir_dm3_before_partial_ru_v032.json")
        new = load("events/darknights_memoir_dm3_before_partial_ru_v033.json")
        self.assertEqual(new["version"], "v0.33-partial")
        self.assertEqual(new["source"], old["source"])
        self.assertEqual(new["source_file"], old["source_file"])
        self.assertEqual({k: new["plain_dialogues"][k] for k in old["plain_dialogues"]}, old["plain_dialogues"])
        self.assertEqual(set(new["plain_dialogues"]), {str(i) for i in range(1, 21)})
        self.assertEqual(set(new["dialogues"]), {str(i) for i in range(1, 41)})
        self.assertEqual((new["progress"]["named_ru_lines"], new["progress"]["plain_ru_lines"], new["progress"]["total_ru_lines"]), (40, 20, 60))
        self.assertEqual((new["progress"]["next_named_ordinal"], new["progress"]["next_plain_ordinal"]), (41, 21))
        self.assertFalse(new["progress"]["complete"])
        self.assertEqual(new["format"], "partial_translation_work_in_progress")
        self.assertEqual((new["source"]["named_dialogue_count"], new["source"]["plain_dialogue_count"]), (152, 35))
        self.assertTrue(new["source"]["dialogue_kind_sequence_matches"])
        for v in list(new["plain_dialogues"].values()) + list(new["dialogues"].values()):
            self.assertIsInstance(v, str)
            self.assertTrue(v.strip())
            self.assertFalse(any(c in v for c in "\r\n\t"))
            self.assertEqual(quoted_tokens(v), [])

    def test_metadata_consistency(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v033.json")
        q = load("reports/QA_v033.json")
        a = load("reports/DM3_SOURCE_AUDIT_v033.json")
        integ = m["translation_integrity"]
        self.assertEqual(m["next_file"], "activities/act9d0/level_act9d0_03_beg.txt")
        self.assertEqual(integ["darknights_completed_files"], 4)
        self.assertEqual(integ["darknights_partial_named_ru_lines"], 40)
        self.assertEqual(integ["darknights_partial_plain_ru_lines"], 20)
        self.assertEqual(integ["darknights_ru_lines_including_partial"], 712)
        self.assertEqual((q["new_named_ru_lines"], q["new_unnamed_ru_lines"], q["new_total"]), (40, 3, 43))
        self.assertEqual((q["event_completed_scripts_ru_lines"], q["event_partial_ru_lines"], q["event_ru_lines_including_partial"]), (652, 60, 712))
        self.assertFalse(q["scene_complete"])
        self.assertEqual((a["partial_translation"]["named_lines_translated"], a["partial_translation"]["plain_lines_translated"]), (40, 20))
        self.assertEqual((a["partial_translation"]["remaining_named_lines"], a["partial_translation"]["remaining_plain_lines"]), (112, 15))
        self.assertEqual(a["sources"]["cn"]["git_blob_sha1"], "538c852f8a64981df34f7699be9f73dfe00873ea")
        self.assertEqual(a["sources"]["en"]["git_blob_sha1"], "37dcf8c721efd0fa5068d18146caae45ba200b70")
        idx = (ROOT / "events/DARKNIGHTS_MEMOIR_INDEX_v033.tsv").read_text(encoding="utf8")
        self.assertIn("level_act9d0_03_beg.txt\tpartial_first_draft\t40\t20", idx)
        self.assertIn("level_act9d0_03_end.txt\tnot_translated\t0\t0", idx)
        readme = (ROOT / "README.md").read_text(encoding="utf8")
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v033.json", readme)

    def test_representative_translations(self):
        d = load("events/darknights_memoir_dm3_before_partial_ru_v033.json")
        self.assertIn("Кальцит", d["plain_dialogues"]["19"])
        self.assertIn("корабле", d["dialogues"]["3"])
        self.assertIn("Искусства", d["dialogues"]["18"])
        self.assertIn("Терезию", d["dialogues"]["31"])
        self.assertIn("Доктор", d["dialogues"]["39"])

if __name__ == "__main__":
    unittest.main()
