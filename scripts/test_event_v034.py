# coding: utf-8
"""Offline consistency checks for DM-3 v0.34 partial draft."""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from apply_ru_story import quoted_tokens


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class DarknightsV034(unittest.TestCase):
    def test_increment_preserves_all_prior_lines(self):
        previous = load("events/darknights_memoir_dm3_before_partial_ru_v033.json")
        current = load("events/darknights_memoir_dm3_before_partial_ru_v034.json")
        self.assertEqual(current["version"], "v0.34-partial")
        self.assertEqual(current["source"], previous["source"])
        self.assertEqual(current["source_file"], previous["source_file"])
        for kind in ("dialogues", "plain_dialogues"):
            for ordinal, translation in previous[kind].items():
                self.assertEqual(current[kind][ordinal], translation)
        self.assertEqual(set(current["dialogues"]), {str(i) for i in range(1, 53)})
        self.assertEqual(set(current["plain_dialogues"]), {str(i) for i in range(1, 22)})
        progress = current["progress"]
        self.assertEqual((progress["named_ru_lines"], progress["plain_ru_lines"], progress["total_ru_lines"]), (52, 21, 73))
        self.assertEqual((progress["next_named_ordinal"], progress["next_plain_ordinal"]), (53, 22))
        self.assertEqual((progress["completed_named_ordinals"], progress["completed_plain_ordinals"]), ("1-52", "1-21"))
        self.assertFalse(progress["complete"])
        self.assertEqual(current["format"], "partial_translation_work_in_progress")
        for translation in list(current["dialogues"].values()) + list(current["plain_dialogues"].values()):
            self.assertIsInstance(translation, str)
            self.assertTrue(translation.strip())
            self.assertFalse(any(c in translation for c in "\r\n\t"))
            self.assertEqual(quoted_tokens(translation), [])

    def test_cross_file_metadata(self):
        doc = load("events/darknights_memoir_dm3_before_partial_ru_v034.json")
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v034.json")
        qa = load("reports/QA_v034.json")
        audit = load("reports/DM3_SOURCE_AUDIT_v034.json")
        totals = manifest["translation_integrity"]
        self.assertEqual(manifest["next_file"], doc["source_file"])
        self.assertEqual(totals["darknights_completed_files"], 4)
        self.assertEqual(totals["darknights_partial_named_ru_lines"], len(doc["dialogues"]))
        self.assertEqual(totals["darknights_partial_plain_ru_lines"], len(doc["plain_dialogues"]))
        self.assertEqual(totals["darknights_ru_lines_including_partial"], 652 + len(doc["dialogues"]) + len(doc["plain_dialogues"]))
        self.assertEqual((qa["new_named_ru_lines"], qa["new_unnamed_ru_lines"], qa["new_total"]), (12, 1, 13))
        self.assertEqual((qa["event_partial_ru_lines"], qa["event_ru_lines_including_partial"]), (73, 725))
        self.assertFalse(qa["scene_complete"])
        self.assertEqual((audit["partial_translation"]["named_lines_translated"], audit["partial_translation"]["plain_lines_translated"]), (52, 21))
        self.assertEqual((audit["partial_translation"]["remaining_named_lines"], audit["partial_translation"]["remaining_plain_lines"]), (100, 14))
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"], doc["source"]["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"], doc["source"]["en_git_blob_sha1"])
        self.assertEqual((doc["source"]["named_dialogue_count"], doc["source"]["plain_dialogue_count"]), (152, 35))
        idx = (ROOT / "events/DARKNIGHTS_MEMOIR_INDEX_v034.tsv").read_text(encoding="utf-8")
        self.assertIn("level_act9d0_03_beg.txt\tpartial_first_draft\t52\t21", idx)
        self.assertIn("level_act9d0_03_end.txt\tnot_translated\t0\t0", idx)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v034.json", readme)

    def test_contiguous_scene_prefix(self):
        # Pinned CN/EN source order: first 20 plain, then 52 named, then plain #21.
        # Kind order is necessary but does not prove semantic alignment.
        doc = load("events/darknights_memoir_dm3_before_partial_ru_v034.json")
        self.assertEqual(len(doc["plain_dialogues"]), 21)
        self.assertEqual(len(doc["dialogues"]), 52)
        self.assertTrue(doc["dialogues"]["52"].endswith("—"))
        self.assertEqual(doc["plain_dialogues"]["21"], "Да почему опять заклинило?!")

if __name__ == "__main__":
    unittest.main()
