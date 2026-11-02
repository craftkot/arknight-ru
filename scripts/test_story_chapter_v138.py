# coding: utf-8
"""Regression checks for 6-5 after battle partial draft v1.38."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENE = "obt/main/level_main_06-05_end.txt"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter605AfterV138(unittest.TestCase):
    def test_partial_contiguous_50_entries(self):
        d = load("story/story_chapter_6_stage_6-5_after_partial_ru_v138.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1, 51)])
        p = d["progress"]
        self.assertEqual((p["named_ru_lines"], p["unnamed_ru_lines"], p["remaining_text_entries"], p["complete"]), (46, 4, 63, False))
        self.assertEqual((p["next_text_ordinal"], p["next_source_line"], p["source_lines_translated_through"]), (51, 115, 113))
        self.assertEqual(d["source_dialogue_line_numbers"]["50"], 113)
        self.assertEqual(d["decisions"], {})
        self.assertTrue(all(s.strip() and "\\n" not in s and not any(0x4e00 <= ord(c) <= 0x9fff for c in s) for s in d["dialogues"].values()))
        self.assertIn("100800-00200-rct211-93001", d["dialogues"]["35"])

    def test_pins_and_source_alignment(self):
        d = load("story/story_chapter_6_stage_6-5_after_partial_ru_v138.json")
        a = load("reports/CHAPTER_6_STAGE_6-5_AFTER_SOURCE_AUDIT_v138.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"], d["source"]["en_git_blob_sha1"]), ("61a567f9864898a98c913b4b1e169e0bcc7e93b7", "4a4e8cc4004b1b268529eb33923a3e26d3014049"))
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["cn_plain"], a["alignment"]["cn_non_decision_commands"]), (109, 4, 118))
        self.assertTrue(a["alignment"]["cn_en_command_positions_equal"])
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(a["alignment"]["source_choice_commands"], 0)

    def test_manifest_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v138.json")
        q = load("reports/QA_MAIN_STORY_v138.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_files"]), (106, 1))
        self.assertEqual((m["translation_integrity"]["main_story_partial_named_ru_lines"], m["translation_integrity"]["main_story_partial_unnamed_ru_lines"]), (46, 4))
        self.assertEqual((q["scene_ru_named"], q["scene_ru_unnamed"], q["scene_remaining_named"], q["included_in_complete_story_selection"]), (46, 4, 63, False))
        self.assertEqual((m["next_file"], m["partial_scene_next_text_ordinal"], m["partial_scene_next_source_line"]), (SCENE, 51, 115))
        idx = (ROOT / "story/CHAPTER_6_INDEX_v138.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-05_end.txt\\tpartial_first_draft_50_of_113\\t46\\t4\\t50", idx)

    def test_prior_selection_unchanged(self):
        s = load("story/story_main_selection_ru_v137.json")
        self.assertEqual(len(s["files"]), 106)
        self.assertNotIn(SCENE, s["files"])
        self.assertEqual(sum(len(v.get("dialogues", {})) + len(v.get("plain_lines", {})) for v in s["files"].values()), 7094)
        self.assertEqual(load("reports/QA_MAIN_STORY_v138.json")["selection_vs_historical_manifest_delta"], 1)

if __name__ == "__main__":
    unittest.main()
