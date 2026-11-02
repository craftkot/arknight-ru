# coding: utf-8
"""Regression checks for completed 6-5 after battle v1.39."""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SCENE = "obt/main/level_main_06-05_end.txt"
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class Chapter605AfterV139(unittest.TestCase):
    def test_complete_contiguous(self):
        d=load("story/story_chapter_6_stage_6-5_after_ru_v139.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1,114)])
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["unnamed_ru_lines"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(109,4,0,True))
        self.assertEqual(d["source_dialogue_line_numbers"]["113"],227)
        self.assertEqual(d["decisions"],{})
        self.assertTrue(all(x.strip() and "\n" not in x and not any(0x4e00<=ord(c)<=0x9fff for c in x) for x in d["dialogues"].values()))
    def test_previous_50_preserved(self):
        old=load("story/story_chapter_6_stage_6-5_after_partial_ru_v138.json")["dialogues"]
        new=load("story/story_chapter_6_stage_6-5_after_ru_v139.json")["dialogues"]
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        self.assertIn("100800-00200-rct211-93001",new["35"])
    def test_sources(self):
        d=load("story/story_chapter_6_stage_6-5_after_ru_v139.json")
        a=load("reports/CHAPTER_6_STAGE_6-5_AFTER_SOURCE_AUDIT_v139.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("61a567f9864898a98c913b4b1e169e0bcc7e93b7","4a4e8cc4004b1b268529eb33923a3e26d3014049"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["cn_plain"],a["alignment"]["cn_non_decision_commands"]),(109,4,118))
        self.assertTrue(a["alignment"]["cn_en_command_positions_equal"])
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
    def test_selection_manifest_index(self):
        s=load("story/story_main_selection_ru_v139.json")
        m=load("chronology/CHRONOLOGY_MANIFEST_v139.json")
        q=load("reports/QA_MAIN_STORY_v139.json")
        self.assertEqual(len(s["files"]),107)
        self.assertIn(SCENE,s["files"])
        self.assertEqual(len(s["files"][SCENE]["dialogues"]),113)
        self.assertEqual(sum(len(v.get("dialogues",{}))+len(v.get("plain_lines",{})) for v in s["files"].values()),7207)
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(107,0))
        self.assertEqual((q["completed_story_text_entries"],q["selection_vs_historical_manifest_delta"]),(7208,1))
        idx=(ROOT/"story/CHAPTER_6_INDEX_v139.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-05_end.txt\tfirst_draft_complete\t109\t4\t113",idx)
if __name__=="__main__":
    unittest.main()
