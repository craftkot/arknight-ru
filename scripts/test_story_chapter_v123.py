# coding: utf-8
"""Regression invariants for chapter 6-3 before battle partial draft v1.23."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class Chapter603BeforeV123(unittest.TestCase):
    def test_contiguous_partial_fragment(self):
        d = load("story/story_chapter_6_stage_6-3_before_partial_ru_v123.json")
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1, 37)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        lines = list(d["source_dialogue_line_numbers"].values())
        self.assertEqual(lines, sorted(lines))
        self.assertEqual((lines[0], lines[-1]), (8, 72))
        self.assertTrue(all(s.strip() and not re.search(r"[\\u4e00-\\u9fff\\r\\n]", s) for s in d["dialogues"].values()))
    def test_source_alignment(self):
        d = load("story/story_chapter_6_stage_6-3_before_partial_ru_v123.json")
        a = load("reports/CHAPTER_6_STAGE_6-3_BEFORE_SOURCE_AUDIT_v123.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"], d["source"]["en_git_blob_sha1"]), ("761a61b650186ed88476602440936d8d1e7116d3", "328738b032366a56e2b270e8b8e77ac8fbc92ea3"))
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["en_tagged"], a["alignment"]["cn_non_decision_commands"]), (92, 92, 128))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(a["alignment"]["source_choice_commands"], 1)
        self.assertEqual(d["decisions"], {})
    def test_partial_not_merged_to_selection(self):
        d = load("story/story_chapter_6_stage_6-3_before_partial_ru_v123.json")
        s = load("story/story_main_selection_ru_v122.json")
        self.assertEqual((d["progress"]["total_ru_text_entries"], d["progress"]["remaining_text_entries"]), (36, 56))
        self.assertFalse(d["progress"]["complete"])
        self.assertEqual(d["progress"]["first_untranslated_source_line"], 99)
        self.assertIn("SCENE_NOT_COMPLETE", d["status"])
        self.assertNotIn(d["source_file"], s["files"])
        self.assertEqual(len(s["files"]), 101)
    def test_manifest_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v123.json")
        q = load("reports/QA_MAIN_STORY_v123.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_files"]), (101, 1))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"], 6650)
        self.assertEqual((q["scene_ru_named"], q["scene_remaining_named"], q["included_in_complete_story_selection"]), (36, 56, False))
        self.assertEqual(m["next_file"], "obt/main/level_main_06-03_beg.txt")
        idx = (ROOT / "story/CHAPTER_6_INDEX_v123.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-03_beg.txt\\tpartial_first_draft\\t36\\t0\\t36", idx)
if __name__ == "__main__":
    unittest.main()
