# coding: utf-8
"""Chapter 6-4 before battle v1.28 partial draft invariants."""
import json
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Chapter604BeforeV128(unittest.TestCase):
    def test_partial_contiguous(self):
        d=load("story/story_chapter_6_stage_6-4_before_partial_ru_v128.json")
        self.assertEqual(list(d["dialogues"]),[str(i) for i in range(1,8)])
        self.assertEqual(list(d["source_dialogue_line_numbers"].values()),[6,7,8,9,11,15,16])
        self.assertEqual((d["progress"]["total_ru_text_entries"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(7,140,False))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
    def test_source_audit(self):
        d=load("story/story_chapter_6_stage_6-4_before_partial_ru_v128.json")
        a=load("reports/CHAPTER_6_STAGE_6-4_BEFORE_SOURCE_AUDIT_v128.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("fe138c6fa548b611ab94ebe47ffcd187a7e78395","c601ac112ced250feebd529a2bb07dd02021b4ae"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(147,147,207))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(d["decisions"],{})
    def test_selection_unmodified(self):
        selection=load("story/story_main_selection_ru_v127.json")
        self.assertEqual(len(selection["files"]),103)
        self.assertNotIn("obt/main/level_main_06-04_beg.txt",selection["files"])
    def test_manifest_qa_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v128.json")
        q=load("reports/QA_MAIN_STORY_v128.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(103,1))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"],6784)
        self.assertEqual((q["scene_ru_named"],q["scene_remaining_named"],q["included_in_complete_story_selection"]),(7,140,False))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-04_beg.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v128.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-04_beg.txt\tpartial_first_draft_7_of_147\t7\t0\t7",idx)
if __name__=="__main__": unittest.main()
