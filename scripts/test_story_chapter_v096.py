# coding: utf-8
"""Regression tests for the incomplete 5-4 before-battle draft v0.96."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-04_beg.txt"
NEW = "story/story_chapter_5_stage_5-4_before_partial_ru_v096.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter54BeforePartialV096(unittest.TestCase):
    def test_contiguous_nonempty_and_incomplete(self):
        p = load(NEW)
        d = p["dialogues"]
        self.assertEqual(set(d), {str(i) for i in range(1, 21)})
        self.assertEqual(p["source_file"], REL)
        self.assertFalse(p["progress"]["complete"])
        self.assertEqual((p["progress"]["total_ru_text_entries"], p["progress"]["remaining_text_entries"]), (20, 21))
        self.assertEqual((p["progress"]["source_lines_translated_through"], p["progress"]["first_untranslated_named_source_line"], p["progress"]["next_named_ordinal"]), (49, 50, 21))
        self.assertTrue(all(isinstance(v, str) and v.strip() and not any(c in v for c in "\r\n\t") for v in d.values()))
        self.assertEqual(d["20"], "Именно.")

    def test_cn_en_hashes_and_structure(self):
        p = load(NEW)["source"]
        a = load("reports/CHAPTER_5_STAGE_5-4_BEFORE_SOURCE_AUDIT_v096.json")["alignment"]
        self.assertEqual((p["cn_git_blob_sha1"], p["en_git_blob_sha1"]), ("54a9f0ea3102c4a0918bee64fed05f5131f97cfd", "8a998d4848d426c07ad88b17a1fb84379257f4f8"))
        self.assertEqual((a["cn_named"], a["en_named"], a["cn_bare"], a["en_bare"]), (41, 41, 0, 0))
        self.assertEqual((a["cn_non_dialogue_commands"], a["en_non_dialogue_commands"]), (65, 65))
        self.assertTrue(a["cn_en_text_source_line_positions_equal"])
        self.assertTrue(a["cn_en_non_dialogue_commands_equal"])
        self.assertTrue(a["en_terminal_newline_extra"])
        self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", p["cn_git_blob_sha1"]))

    def test_complete_selection_untouched(self):
        selection = load("story/story_main_selection_ru_v095.json")
        self.assertEqual(len(selection["files"]), 86)
        self.assertNotIn(REL, selection["files"])
        self.assertEqual(sum(f["dialogue_count"] for f in selection["files"].values()), 5228)

    def test_manifest_index_and_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v096.json")
        q = load("reports/QA_MAIN_STORY_v096.json")
        t = m["translation_integrity"]
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 21))
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (86, 5205))
        self.assertEqual((t["main_story_chapter_5_partial_named_ru_lines"], t["main_story_named_ru_lines_including_partial"]), (20, 5225))
        self.assertEqual(t["main_story_text_entries_including_partial"], 5248)
        self.assertEqual((q["new_text_entries"], q["source_text_entries_remaining"], q["partial_scene_files"]), (20, 21, 1))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v096.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-04_beg.txt\tpartial_first_draft_20_of_41\t20\t0\t20", idx)

if __name__ == "__main__":
    unittest.main()
