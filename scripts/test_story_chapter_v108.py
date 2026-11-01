# coding: utf-8
"""Regression tests for partial chapter 5 stage 5-10 before battle v1.08."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-10_beg.txt"
NEW = "story/story_chapter_5_stage_5-10_before_partial_ru_v108.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter510BeforePartialV108(unittest.TestCase):
    def test_contiguous_and_not_complete(self):
        p = load(NEW)
        self.assertEqual(p["source_file"], REL)
        self.assertEqual(set(p["dialogues"]), {str(i) for i in range(1, 52)})
        self.assertFalse(p["progress"]["complete"])
        self.assertEqual((p["progress"]["named_ru_lines"], p["progress"]["next_named_ordinal"]), (51, 52))
        self.assertEqual((p["progress"]["source_lines_translated_through"], p["progress"]["first_untranslated_named_source_line"]), (113, 139))
        self.assertTrue(all(v.strip() and not any(c in v for c in "\r\n\t") for v in p["dialogues"].values()))
        self.assertEqual(p["dialogues"]["51"], "Тогда продолжим!")

    def test_source_hashes_and_branching(self):
        p = load(NEW)
        a = load("reports/CHAPTER_5_STAGE_5-10_BEFORE_SOURCE_AUDIT_v108.json")["alignment"]
        self.assertEqual((p["source"]["cn_git_blob_sha1"], p["source"]["en_git_blob_sha1"]), ("922973f06fdda4acb1ad0207ef2ae6f07e3472f1", "dbf64cfdcc8e97b720398c386000477d0da81ea8"))
        self.assertEqual((a["cn_named"], a["en_named"], a["cn_bare"], a["en_bare"]), (247, 247, 1, 1))
        self.assertEqual((a["cn_bracket_commands"], a["en_bracket_commands"]), (425, 425))
        self.assertEqual((a["decision_commands_differing_only_in_localized_option_text"], a["source_choice_options"]), (6, 10))
        self.assertTrue(a["cn_en_dialogue_source_line_positions_equal"])
        self.assertFalse(a["cn_en_bracket_command_text_equal"])
        self.assertTrue(a["cn_en_non_decision_command_text_equal"])
        self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", p["source"]["cn_git_blob_sha1"]))

    def test_selection_unchanged(self):
        sel = load("story/story_main_selection_ru_v107.json")
        self.assertEqual(len(sel["files"]), 94)
        self.assertNotIn(REL, sel["files"])
        self.assertEqual(sum(f["dialogue_count"] for f in sel["files"].values()), 5740)

    def test_manifest_qa_index(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v108.json")
        q = load("reports/QA_MAIN_STORY_v108.json")
        t = m["translation_integrity"]
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 52))
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (94, 5705))
        self.assertEqual((t["main_story_partial_named_ru_lines"], t["main_story_named_ru_lines_including_partial"]), (51, 5756))
        self.assertEqual(t["main_story_text_entries_including_partial"], 5791)
        self.assertEqual((q["new_text_entries"], q["source_text_entries_remaining_excluding_choices"], q["partial_scene_files"]), (51, 197, 1))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v108.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-10_beg.txt\tpartial_first_draft_51_of_247\t51\t0\t51", idx)

if __name__ == "__main__":
    unittest.main()
