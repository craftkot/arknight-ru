# coding: utf-8
"""Regression checks for 6-2 after battle v1.22."""
import json
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
class Chapter602AfterV122(unittest.TestCase):
    def test_complete_contiguous(self):
        d=load("story/story_chapter_6_stage_6-2_after_ru_v122.json")
        self.assertEqual(set(d["dialogues"]),{str(i) for i in range(1,47)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]),set(d["dialogues"]))
        self.assertEqual(list(d["source_dialogue_line_numbers"].values()),sorted(d["source_dialogue_line_numbers"].values()))
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["unnamed_ru_lines"],d["progress"]["total_ru_text_entries"]),(46,0,46))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
        self.assertTrue(d["progress"]["complete"])
        self.assertIn("NOT_GAME_TESTED",d["status"])
    def test_source_alignment_and_choices(self):
        d=load("story/story_chapter_6_stage_6-2_after_ru_v122.json")
        a=load("reports/CHAPTER_6_STAGE_6-2_AFTER_SOURCE_AUDIT_v122.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("2d7aed80762850fa8ba84a4e711294ad28244b4b","edcabd5e8e38861a9888cc9580c3aa6cf00424a6"))
        self.assertEqual([x["line"] for x in d["decisions"].values()],[29,34])
        self.assertEqual([len(x["options"]) for x in d["decisions"].values()],[1,1])
        self.assertEqual([x["values"] for x in d["decisions"].values()],[["1"],["1"]])
        self.assertEqual(a["alignment"]["cn_non_decision_commands"],53)
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
    def test_selection_integrity(self):
        d=load("story/story_chapter_6_stage_6-2_after_ru_v122.json")
        s=load("story/story_main_selection_ru_v122.json")
        self.assertEqual(len(s["files"]),101)
        f=s["files"]["obt/main/level_main_06-02_end.txt"]
        self.assertEqual(f["dialogues"],d["dialogues"])
        self.assertEqual(f["decisions"],d["decisions"])
        self.assertEqual(f["source_dialogue_line_numbers"],d["source_dialogue_line_numbers"])
    def test_manifest_index_and_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v122.json")
        q=load("reports/QA_MAIN_STORY_v122.json")
        self.assertEqual(m["translation_integrity"]["main_story_files"],101)
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_unnamed"],6614)
        self.assertEqual((q["scene_ru_named"],q["scene_ru_unnamed"],q["scene_remaining_named"]),(46,0,0))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-03_beg.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v122.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-02_end.txt\tfirst_draft_complete\t46\t0\t46",idx)
if __name__=="__main__": unittest.main()
