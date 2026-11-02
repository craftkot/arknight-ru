# coding: utf-8
"""Regression checks for 6-2 before battle v1.21."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class Chapter602BeforeV121(unittest.TestCase):
    def test_complete_contiguous(self):
        d = load("story/story_chapter_6_stage_6-2_before_ru_v121.json")
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1,99)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        self.assertEqual(list(d["source_dialogue_line_numbers"].values()), sorted(d["source_dialogue_line_numbers"].values()))
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["unnamed_ru_lines"],d["progress"]["total_ru_text_entries"]), (72,26,98))
        self.assertTrue(all(x.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",x) for x in d["dialogues"].values()))
        self.assertTrue(d["progress"]["complete"])
        self.assertIn("NOT_GAME_TESTED",d["status"])
    def test_source_alignment_and_choices(self):
        d = load("story/story_chapter_6_stage_6-2_before_ru_v121.json")
        a = load("reports/CHAPTER_6_STAGE_6-2_BEFORE_SOURCE_AUDIT_v121.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("6c530f2a1bd469c55c251ffaea62b853d890750e","16e60bbfbfe612487c1bf6d2386cfdb21ad3dc9a"))
        self.assertEqual([x["line"] for x in d["decisions"].values()],[155,198])
        self.assertEqual([len(x["options"]) for x in d["decisions"].values()],[3,1])
        self.assertEqual([len(x["values"]) for x in d["decisions"].values()],[3,3])
        self.assertEqual(a["alignment"]["cn_non_decision_commands"],107)
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
    def test_selection_integrity(self):
        d=load("story/story_chapter_6_stage_6-2_before_ru_v121.json")
        s=load("story/story_main_selection_ru_v121.json")
        self.assertEqual(len(s["files"]),100)
        f=s["files"]["obt/main/level_main_06-02_beg.txt"]
        self.assertEqual(f["dialogues"],d["dialogues"])
        self.assertEqual(f["decisions"],d["decisions"])
        self.assertEqual(f["source_dialogue_line_numbers"],d["source_dialogue_line_numbers"])
    def test_manifest_index_and_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v121.json")
        q=load("reports/QA_MAIN_STORY_v121.json")
        self.assertEqual(m["translation_integrity"]["main_story_files"],100)
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_unnamed"],6568)
        self.assertEqual((q["scene_ru_named"],q["scene_ru_unnamed"],q["scene_remaining_named"]),(72,26,0))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-02_end.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v121.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-02_beg.txt\tfirst_draft_complete\t72\t26\t98",idx)
if __name__ == "__main__":
    unittest.main()
