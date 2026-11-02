# coding: utf-8
"""Regression checks for 6-4 before battle v1.29 partial draft."""
import json
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
class Chapter604V129(unittest.TestCase):
    def test_contiguous_preserved(self):
        old=load("story/story_chapter_6_stage_6-4_before_partial_ru_v128.json")
        d=load("story/story_chapter_6_stage_6-4_before_partial_ru_v129.json")
        self.assertEqual(list(d["dialogues"]),[str(i) for i in range(1,43)])
        self.assertEqual({k:d["dialogues"][k] for k in old["dialogues"]},old["dialogues"])
        self.assertEqual((d["progress"]["total_ru_text_entries"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(42,105,False))
        self.assertEqual((d["progress"]["next_text_ordinal"],d["progress"]["next_source_line"]),(43,95))
        self.assertEqual((d["source_dialogue_line_numbers"]["8"],d["source_dialogue_line_numbers"]["42"]),(18,88))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
    def test_source_alignment(self):
        d=load("story/story_chapter_6_stage_6-4_before_partial_ru_v129.json")
        a=load("reports/CHAPTER_6_STAGE_6-4_BEFORE_SOURCE_AUDIT_v129.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("fe138c6fa548b611ab94ebe47ffcd187a7e78395","c601ac112ced250feebd529a2bb07dd02021b4ae"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(147,147,207))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual((a["alignment"]["ru_tagged_entries"],a["alignment"]["ru_remaining_entries"]),(42,105))
        self.assertEqual(d["decisions"],{})
    def test_complete_selection_unchanged(self):
        s=load("story/story_main_selection_ru_v127.json")
        self.assertEqual(len(s["files"]),103)
        self.assertNotIn("obt/main/level_main_06-04_beg.txt",s["files"])
    def test_manifest_qa_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v129.json")
        q=load("reports/QA_MAIN_STORY_v129.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(103,1))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"],6819)
        self.assertEqual((q["scene_ru_named"],q["scene_remaining_named"],q["included_in_complete_story_selection"]),(42,105,False))
        self.assertEqual((q["next_text_ordinal"],q["next_source_line"]),(43,95))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-04_beg.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v129.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-04_beg.txt\tpartial_first_draft_42_of_147\t42\t0\t42",idx)
if __name__=="__main__": unittest.main()
