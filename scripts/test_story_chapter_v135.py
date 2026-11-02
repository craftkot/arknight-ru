# coding: utf-8
"""Regression checks for CN-primary 6-5 before battle partial draft v1.35."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Chapter605BeforeV135(unittest.TestCase):
    def test_contiguous_partial_and_progress(self):
        d=load("story/story_chapter_6_stage_6-5_before_partial_ru_v135.json")
        self.assertEqual(list(d["dialogues"]),[str(i) for i in range(1,49)])
        self.assertEqual((d["progress"]["total_ru_text_entries"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(48,62,False))
        self.assertEqual((d["progress"]["next_text_ordinal"],d["progress"]["next_source_line"]),(49,99))
        self.assertEqual((d["source_dialogue_line_numbers"]["1"],d["source_dialogue_line_numbers"]["48"]),(9,97))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
    def test_source_pins_and_alignment(self):
        d=load("story/story_chapter_6_stage_6-5_before_partial_ru_v135.json")
        a=load("reports/CHAPTER_6_STAGE_6-5_BEFORE_SOURCE_AUDIT_v135.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("21dbb955fd9e12151a8754930dae6c6e348b1fc2","aedc8fd8cfa764ecccdcadfd81260cdd27c4fa0e"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(110,110,109))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual((a["alignment"]["ru_tagged_entries"],a["alignment"]["ru_remaining_entries"]),(48,62))
        self.assertEqual(d["decisions"],{})
    def test_complete_selection_unchanged(self):
        s=load("story/story_main_selection_ru_v134.json")
        self.assertEqual(len(s["files"]),105)
        self.assertNotIn("obt/main/level_main_06-05_beg.txt",s["files"])
    def test_manifest_qa_and_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v135.json")
        q=load("reports/QA_MAIN_STORY_v135.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(105,1))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"],7033)
        self.assertEqual((q["scene_ru_named"],q["scene_remaining_named"],q["included_in_complete_story_selection"]),(48,62,False))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-05_beg.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v135.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-05_beg.txt\tpartial_first_draft_48_of_110\t48\t0\t48",idx)
if __name__=="__main__": unittest.main()
