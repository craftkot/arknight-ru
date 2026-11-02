# coding: utf-8
"""Regression invariants for chapter 6, 6-1 before battle partial draft v1.17."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_06-01_beg.txt"
NEW = "story/story_chapter_6_stage_6-1_before_partial_ru_v117.json"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Chapter601BeforePartialV117(unittest.TestCase):
    def test_contiguous_partial_and_source_line_map(self):
        d = load(NEW)
        self.assertEqual(d["source_file"], REL)
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1, 47)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        numbers = list(d["source_dialogue_line_numbers"].values())
        self.assertEqual((numbers[0], numbers[-1]), (6, 125))
        self.assertEqual(numbers, sorted(numbers))
        self.assertEqual(d["source_dialogue_line_numbers"]["20"], 74)
        self.assertEqual(d["source_dialogue_line_numbers"]["46"], 125)
        self.assertTrue(all(isinstance(s, str) and s.strip() and "\n" not in s and "\r" not in s for s in d["dialogues"].values()))
        self.assertTrue(all(not re.search(r"[\u4e00-\u9fff]", s) for s in d["dialogues"].values()))

    def test_progress_hashes_and_partial_status(self):
        d = load(NEW)
        p, s = d["progress"], d["source"]
        self.assertEqual((p["named_ru_lines"], p["unnamed_ru_lines"], p["total_ru_text_entries"]), (30, 16, 46))
        self.assertEqual((p["source_total_text_entries"], p["remaining_text_entries"]), (87, 41))
        self.assertEqual((p["next_text_ordinal"], p["next_named_ordinal"], p["first_untranslated_source_line"]), (47, 31, 133))
        self.assertFalse(p["complete"])
        self.assertIn("SCENE_NOT_COMPLETE", d["status"])
        self.assertIn("NOT_GAME_TESTED", d["status"])
        self.assertEqual(s["cn_git_blob_sha1"], "b6e2676b8f7caa0a932b762d1ab2ea888631fd48")
        self.assertEqual(s["en_git_blob_sha1"], "2e727fd428c47cce434faf62442c24aaa5a1c7d1")

    def test_choice_and_source_alignment_record(self):
        d = load(NEW)
        a = load("reports/CHAPTER_6_STAGE_6-1_BEFORE_SOURCE_AUDIT_v117.json")
        self.assertEqual(d["source_decision_line_numbers"], {"1": 19})
        self.assertEqual(d["decisions"]["1"]["values"], ["1"])
        self.assertEqual(d["decisions"]["1"]["options"], ["ФростНова!"])
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["cn_plain"]), (70, 17))
        self.assertEqual(a["alignment"]["cn_non_decision_commands"], 161)
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertTrue(a["alignment"]["cn_en_decision_value_alignment"])
        self.assertEqual(a["alignment"]["ru_remaining_entries"], 41)

    def test_manifest_index_qa_and_exclusion_from_complete_selection(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v117.json")
        q = load("reports/QA_MAIN_STORY_v117.json")
        selection = load("story/story_main_selection_ru_v116.json")
        self.assertEqual((m["next_file"], m["next_text_ordinal"], m["next_named_ordinal"]), (REL, 47, 31))
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_files"]), (97, 1))
        self.assertEqual((m["translation_integrity"]["main_story_partial_named_ru_lines"], m["translation_integrity"]["main_story_partial_unnamed_ru_lines"]), (30, 16))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"], 6291)
        self.assertEqual((q["scene_ru_named"], q["scene_ru_unnamed"], q["scene_remaining_named"], q["scene_remaining_unnamed"]), (30, 16, 40, 1))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertEqual(len(selection["files"]), 97)
        self.assertNotIn(REL, selection["files"])
        index = (ROOT / "story/CHAPTER_6_INDEX_v117.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-01_beg.txt\tpartial_first_draft_46_of_87\t30\t16\t46", index)


if __name__ == "__main__":
    unittest.main()
