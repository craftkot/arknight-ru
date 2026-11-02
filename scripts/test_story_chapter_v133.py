# coding: utf-8
"""Regression checks for 6-4 after battle partial draft v1.33."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Chapter604AfterV133(unittest.TestCase):
    def test_consecutive_partial_and_progress(self):
        d=load("story/story_chapter_6_stage_6-4_after_partial_ru_v133.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1,35)])
        self.assertEqual((d["progress"]["total_ru_text_entries"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(34,27,False))
        self.assertEqual((d["progress"]["next_text_ordinal"],d["progress"]["next_source_line"]),(35,56))
        self.assertEqual((d["source_dialogue_line_numbers"]["1"],d["source_dialogue_line_numbers"]["34"]),(6,54))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
    def test_pinned_sources_and_commands(self):
        d=load("story/story_chapter_6_stage_6-4_after_partial_ru_v133.json")
        a=load("reports/CHAPTER_6_STAGE_6-4_AFTER_SOURCE_AUDIT_v133.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("b99c61e654c013f0c7533a6028c755db823d7847","afb27390867f90608de65f8966fd1c8b6abd5f60"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(61,61,43))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual((a["alignment"]["ru_tagged_entries"],a["alignment"]["ru_remaining_entries"]),(34,27))
        self.assertEqual(d["decisions"],{})
    def test_complete_selection_not_modified(self):
        s=load("story/story_main_selection_ru_v132.json")
        self.assertEqual(len(s["files"]),104)
        self.assertNotIn("obt/main/level_main_06-04_end.txt",s["files"])
    def test_manifest_and_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v133.json")
        q=load("reports/QA_MAIN_STORY_v133.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(104,1))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"],6958)
        self.assertEqual((q["scene_ru_named"],q["scene_remaining_named"],q["included_in_complete_story_selection"]),(34,27,False))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-04_end.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v133.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-04_end.txt\tpartial_first_draft_34_of_61\t34\t0\t34",idx)
if __name__=="__main__": unittest.main()
