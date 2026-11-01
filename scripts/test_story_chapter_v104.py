# coding: utf-8
"""Regression tests for partial chapter 5 stage 5-9 after battle v1.04."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-09_end.txt"
NEW = "story/story_chapter_5_stage_5-9_after_partial_ru_v104.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter59AfterPartialV104(unittest.TestCase):
    def test_contiguous_nonempty_and_incomplete(self):
        p = load(NEW)
        d = p["dialogues"]
        self.assertEqual(set(d), {str(i) for i in range(1, 21)})
        self.assertEqual(p["source_file"], REL)
        self.assertFalse(p["progress"]["complete"])
        self.assertEqual((p["progress"]["total_ru_text_entries"], p["progress"]["remaining_text_entries"]), (20, 116))
        self.assertEqual((p["progress"]["source_lines_translated_through"], p["progress"]["first_untranslated_named_source_line"], p["progress"]["next_named_ordinal"]), (55, 57, 21))
        self.assertTrue(all(isinstance(v, str) and v.strip() and not any(c in v for c in "\r\n\t") for v in d.values()))
        self.assertEqual(d["20"], "В этих словах скрыт какой-то глубокий смысл?")

    def test_cn_en_hashes_and_structure(self):
        p = load(NEW)["source"]
        a = load("reports/CHAPTER_5_STAGE_5-9_AFTER_SOURCE_AUDIT_v104.json")["alignment"]
        self.assertEqual((p["cn_git_blob_sha1"], p["en_git_blob_sha1"]), ("ced45a6cd4fe5679c87cdd7ddae10fe051ef9465", "e02b0f41bbaf69d866c1ba86b73d5f361227b6fb"))
        self.assertEqual((a["cn_named"], a["en_named"], a["cn_bare"], a["en_bare"]), (136, 136, 0, 0))
        self.assertEqual((a["cn_non_dialogue_commands"], a["en_non_dialogue_commands"]), (169, 169))
        self.assertTrue(a["cn_en_text_source_line_positions_equal"])
        self.assertTrue(a["cn_en_non_dialogue_commands_equal"])
        self.assertTrue(a["en_terminal_newline_extra"])
        self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", p["cn_git_blob_sha1"]))

    def test_complete_selection_untouched(self):
        selection = load("story/story_main_selection_ru_v103.json")
        self.assertEqual(len(selection["files"]), 93)
        self.assertNotIn(REL, selection["files"])
        self.assertEqual(sum(f["dialogue_count"] for f in selection["files"].values()), 5604)

    def test_manifest_index_and_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v104.json")
        q = load("reports/QA_MAIN_STORY_v104.json")
        t = m["translation_integrity"]
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 21))
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (93, 5569))
        self.assertEqual((t["main_story_chapter_5_partial_named_ru_lines"], t["main_story_named_ru_lines_including_partial"]), (20, 5589))
        self.assertEqual(t["main_story_text_entries_including_partial"], 5624)
        self.assertEqual((q["new_text_entries"], q["source_text_entries_remaining"], q["partial_scene_files"]), (20, 116, 1))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v104.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-09_end.txt\tpartial_first_draft_20_of_136\t20\t0\t20", idx)

if __name__ == "__main__":
    unittest.main()
