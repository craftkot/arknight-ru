# coding: utf-8
"""Regression checks for the completed 6-4 before battle draft v1.32."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter604V132(unittest.TestCase):
    def test_contiguous_and_preserved(self):
        old = load("story/story_chapter_6_stage_6-4_before_partial_ru_v131.json")
        d = load("story/story_chapter_6_stage_6-4_before_ru_v132.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1, 148)])
        self.assertEqual({k:d["dialogues"][k] for k in old["dialogues"]}, old["dialogues"])
        self.assertEqual({k:d["source_dialogue_line_numbers"][k] for k in old["source_dialogue_line_numbers"]}, old["source_dialogue_line_numbers"])
        self.assertEqual((d["source_dialogue_line_numbers"]["107"],d["source_dialogue_line_numbers"]["147"]),(280,351))
        self.assertEqual((d["progress"]["total_ru_text_entries"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(147,0,True))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]", s) for s in d["dialogues"].values()))
    def test_source_alignment_and_choices(self):
        d=load("story/story_chapter_6_stage_6-4_before_ru_v132.json")
        a=load("reports/CHAPTER_6_STAGE_6-4_BEFORE_SOURCE_AUDIT_v132.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("fe138c6fa548b611ab94ebe47ffcd187a7e78395","c601ac112ced250feebd529a2bb07dd02021b4ae"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(147,147,207))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual((a["alignment"]["ru_tagged_entries"],a["alignment"]["ru_remaining_entries"]),(147,0))
        self.assertEqual(d["decisions"],{})
    def test_complete_selection_includes_scene(self):
        s=load("story/story_main_selection_ru_v132.json")
        d=load("story/story_chapter_6_stage_6-4_before_ru_v132.json")
        self.assertEqual(len(s["files"]),104)
        self.assertEqual(s["files"][d["source_file"]]["dialogues"],d["dialogues"])
        self.assertEqual(sum(len(v["dialogues"]) for v in s["files"].values()),6923)
    def test_manifest_qa_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v132.json")
        q=load("reports/QA_MAIN_STORY_v132.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(104,0))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"],6924)
        self.assertEqual((q["scene_ru_named"],q["scene_remaining_named"],q["included_in_complete_story_selection"]),(147,0,True))
        self.assertEqual((q["selection_dialogue_entries_counted"],q["selection_vs_historical_manifest_delta"]),(6923,1))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-04_end.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v132.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-04_beg.txt\tfirst_draft_complete\t147\t0\t147",idx)
if __name__=="__main__": unittest.main()
