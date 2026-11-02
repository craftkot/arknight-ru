# coding: utf-8
"""Regression checks for 6-1 after battle complete v1.20."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class Chapter601AfterV120(unittest.TestCase):
    def test_complete_contiguous_and_preserved(self):
        d = load("story/story_chapter_6_stage_6-1_after_ru_v120.json")
        old = load("story/story_chapter_6_stage_6-1_after_partial_ru_v119.json")
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1, 139)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        self.assertEqual(list(d["source_dialogue_line_numbers"].values()), sorted(d["source_dialogue_line_numbers"].values()))
        self.assertEqual((d["source_dialogue_line_numbers"]["58"], d["source_dialogue_line_numbers"]["138"]), (141, 310))
        self.assertTrue(all(d["dialogues"][str(i)] == old["dialogues"][str(i)] for i in range(1, 58)))
        self.assertTrue(all(x.strip() and not re.search(r"[\u4e00-\u9fff\r\n]", x) for x in d["dialogues"].values()))
    def test_all_decisions_and_source_alignment(self):
        d = load("story/story_chapter_6_stage_6-1_after_ru_v120.json")
        a = load("reports/CHAPTER_6_STAGE_6-1_AFTER_SOURCE_AUDIT_v120.json")
        self.assertEqual(set(d["decisions"]), {str(i) for i in range(1, 10)})
        self.assertEqual([x["line"] for x in d["decisions"].values()], [50,130,138,148,155,160,180,197,207])
        self.assertEqual([len(x["options"]) for x in d["decisions"].values()], [3,3,1,3,1,1,3,3,3])
        self.assertEqual(sum(len(x["options"]) for x in d["decisions"].values()), 21)
        self.assertTrue(all(len(x["options"]) == len(x["values"]) for x in d["decisions"].values()))
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["cn_non_decision_commands"]), (138,166))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(d["source"]["cn_git_blob_sha1"], "59437f1fe11a9e0712229888e232fa5f86f7caf9")
        self.assertEqual(d["source"]["en_git_blob_sha1"], "db3d5de405ada39426d8a936ea0308dd9e140576")
    def test_selection_integrity(self):
        d = load("story/story_chapter_6_stage_6-1_after_ru_v120.json")
        s = load("story/story_main_selection_ru_v120.json")
        self.assertEqual(len(s["files"]), 99)
        f = s["files"]["obt/main/level_main_06-01_end.txt"]
        self.assertEqual(f["dialogues"], d["dialogues"])
        self.assertEqual(f["decisions"], d["decisions"])
        self.assertEqual(f["source_dialogue_line_numbers"], d["source_dialogue_line_numbers"])
        self.assertEqual((d["progress"]["total_ru_text_entries"], d["progress"]["remaining_text_entries"], d["progress"]["decision_ru_options"]), (138,0,21))
        self.assertTrue(d["progress"]["complete"])
        self.assertIn("NOT_GAME_TESTED", d["status"])
    def test_manifest_index_and_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v120.json")
        q = load("reports/QA_MAIN_STORY_v120.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_files"]), (99,0))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_unnamed"], 6470)
        self.assertEqual((q["scene_ru_named"], q["scene_remaining_named"], q["included_in_complete_story_selection"]), (138,0,True))
        self.assertEqual(m["next_file"], "obt/main/level_main_06-02_beg.txt")
        idx = (ROOT / "story/CHAPTER_6_INDEX_v120.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-01_end.txt\tfirst_draft_complete\t138\t0\t138", idx)
if __name__ == "__main__":
    unittest.main()
