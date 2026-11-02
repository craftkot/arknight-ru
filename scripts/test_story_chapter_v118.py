# coding: utf-8
"""Regression invariants for completed 6-1 before battle v1.18."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_06-01_beg.txt"
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class Chapter601BeforeV118(unittest.TestCase):
    def test_contiguous_entries_and_line_map(self):
        d=load("story/story_chapter_6_stage_6-1_before_ru_v118.json")
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1,88)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        self.assertEqual(list(d["source_dialogue_line_numbers"].values()), sorted(d["source_dialogue_line_numbers"].values()))
        self.assertEqual((d["source_dialogue_line_numbers"]["47"],d["source_dialogue_line_numbers"]["87"]),(133,241))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
    def test_prior_text_and_choice_unchanged(self):
        d=load("story/story_chapter_6_stage_6-1_before_ru_v118.json")
        old=load("story/story_chapter_6_stage_6-1_before_partial_ru_v117.json")
        self.assertEqual({str(i):d["dialogues"][str(i)] for i in range(1,47)},old["dialogues"])
        self.assertEqual(d["decisions"],old["decisions"])
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["unnamed_ru_lines"],d["progress"]["remaining_text_entries"]),(70,17,0))
        self.assertTrue(d["progress"]["complete"])
    def test_source_hashes_and_commands(self):
        d=load("story/story_chapter_6_stage_6-1_before_ru_v118.json")
        a=load("reports/CHAPTER_6_STAGE_6-1_BEFORE_SOURCE_AUDIT_v118.json")
        self.assertEqual(d["source"]["cn_git_blob_sha1"],"b6e2676b8f7caa0a932b762d1ab2ea888631fd48")
        self.assertEqual(d["source"]["en_git_blob_sha1"],"2e727fd428c47cce434faf62442c24aaa5a1c7d1")
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["cn_plain"],a["alignment"]["cn_non_decision_commands"]),(70,17,161))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(d["decisions"]["1"]["values"],["1"])
        self.assertIn("NOT_GAME_TESTED",d["status"])
    def test_selection_manifest_index_and_qa(self):
        d=load("story/story_chapter_6_stage_6-1_before_ru_v118.json")
        s=load("story/story_main_selection_ru_v118.json")
        m=load("chronology/CHRONOLOGY_MANIFEST_v118.json")
        q=load("reports/QA_MAIN_STORY_v118.json")
        self.assertEqual(len(s["files"]),98)
        self.assertEqual(s["files"][REL]["dialogues"],d["dialogues"])
        self.assertEqual(s["files"][REL]["decisions"],d["decisions"])
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_text_entries_including_unnamed"]),(98,6332))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-01_end.txt")
        self.assertEqual((q["scene_ru_named"],q["scene_ru_unnamed"],q["scene_remaining_named"]),(70,17,0))
        self.assertTrue(q["included_in_complete_story_selection"])
        self.assertIn("level_main_06-01_beg.txt\tfirst_draft_complete\t70\t17\t87",(ROOT/"story/CHAPTER_6_INDEX_v118.tsv").read_text(encoding="utf-8"))
if __name__ == "__main__":
    unittest.main()
