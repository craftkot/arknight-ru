# coding: utf-8
"""Regression checks for completed 6-4 after battle draft v1.34."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Chapter604AfterV134(unittest.TestCase):
    def test_complete_and_preserves_previous(self):
        d=load("story/story_chapter_6_stage_6-4_after_ru_v134.json")
        old=load("story/story_chapter_6_stage_6-4_after_partial_ru_v133.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1,62)])
        self.assertEqual({k:d["dialogues"][k] for k in old["dialogues"]},old["dialogues"])
        self.assertEqual((d["progress"]["total_ru_text_entries"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(61,0,True))
        self.assertEqual((d["source_dialogue_line_numbers"]["35"],d["source_dialogue_line_numbers"]["61"]),(56,100))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
    def test_source_pins_and_alignment(self):
        d=load("story/story_chapter_6_stage_6-4_after_ru_v134.json")
        a=load("reports/CHAPTER_6_STAGE_6-4_AFTER_SOURCE_AUDIT_v134.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("b99c61e654c013f0c7533a6028c755db823d7847","afb27390867f90608de65f8966fd1c8b6abd5f60"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(61,61,43))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual((a["alignment"]["ru_tagged_entries"],a["alignment"]["ru_remaining_entries"]),(61,0))
        self.assertEqual(d["decisions"],{})
    def test_selection_and_historical_delta(self):
        s=load("story/story_main_selection_ru_v134.json")
        self.assertEqual(len(s["files"]),105)
        self.assertEqual(sum(len(f["dialogues"]) for f in s["files"].values()),6984)
        p=s["files"]["obt/main/level_main_06-04_end.txt"]
        self.assertEqual(p["dialogue_count"],61)
        self.assertEqual(len(p["dialogues"]),61)
        self.assertEqual(p["dialogues"],load("story/story_chapter_6_stage_6-4_after_ru_v134.json")["dialogues"])
    def test_manifest_qa_and_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v134.json")
        q=load("reports/QA_MAIN_STORY_v134.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(105,0))
        self.assertEqual((m["translation_integrity"]["main_story_text_entries_including_unnamed"],q["completed_story_text_entries"]),(6985,6985))
        self.assertEqual((q["selection_dialogue_entries_counted"],q["selection_vs_historical_manifest_delta"]),(6984,1))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-05_beg.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v134.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-04_end.txt\tfirst_draft_complete\t61\t0\t61",idx)
if __name__=="__main__": unittest.main()
