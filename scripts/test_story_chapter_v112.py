# coding: utf-8
"""Regression tests for partial 5-10 after-battle translation v1.12."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-10_end.txt"
NEW = "story/story_chapter_5_stage_5-10_after_partial_ru_v112.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter510AfterPartialV112(unittest.TestCase):
    def test_contiguous_partial_and_source_hashes(self):
        c = load(NEW)
        self.assertEqual(c["source_file"], REL)
        self.assertEqual(set(c["dialogues"]), {str(i) for i in range(1, 46)})
        self.assertEqual(set(c["source_dialogue_line_numbers"]), set(c["dialogues"]))
        self.assertEqual((c["source_dialogue_line_numbers"]["1"], c["source_dialogue_line_numbers"]["45"]), (10, 113))
        self.assertEqual((c["progress"]["named_ru_lines"], c["progress"]["remaining_text_entries"], c["progress"]["next_named_ordinal"], c["progress"]["first_untranslated_named_source_line"]), (45, 105, 46, 115))
        self.assertFalse(c["progress"]["complete"])
        self.assertEqual((c["source"]["cn_git_blob_sha1"], c["source"]["en_git_blob_sha1"]), ("7f4138c8b615b4965c98c08f08bff695d37555c5", "a26bb1d24231785c98762193454268f5f8fbf081"))

    def test_markup_and_no_fake_complete_scene(self):
        c = load(NEW)
        self.assertIn("{@nickname}", c["dialogues"]["42"])
        self.assertTrue(all(v.strip() and "\r" not in v and "\n" not in v and "\t" not in v for v in c["dialogues"].values()))
        sel = load("story/story_main_selection_ru_v111.json")
        self.assertEqual(len(sel["files"]), 95)
        self.assertNotIn(REL, sel["files"])

    def test_audit_and_qa_alignment(self):
        a = load("reports/CHAPTER_5_STAGE_5-10_AFTER_SOURCE_AUDIT_v112.json")
        q = load("reports/QA_MAIN_STORY_v112.json")
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["en_tagged"], a["alignment"]["cn_bracket_commands"], a["alignment"]["en_bracket_commands"]), (150, 150, 265, 265))
        self.assertTrue(a["alignment"]["cn_en_command_text_equal"])
        self.assertEqual((q["scene_ru_named"], q["scene_remaining_named"], q["completed_story_files"]), (45, 105, 95))
        self.assertFalse(q["included_in_complete_story_selection"])

    def test_manifest_index(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v112.json")
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 46))
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_named_ru_lines"]), (95, 45))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"], 6033)
        idx = (ROOT / "story/CHAPTER_5_INDEX_v112.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-10_end.txt\tpartial_first_draft_45_of_150\t45\t0\t45", idx)

if __name__ == "__main__":
    unittest.main()
