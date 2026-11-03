# coding: utf-8
"""Regression checks for partial chapter 6-6 before battle v1.40."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENE = "obt/main/level_main_06-06_beg.txt"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter606BeforeV140(unittest.TestCase):
    def test_partial_contiguous(self):
        d = load("story/story_chapter_6_stage_6-6_before_partial_ru_v140.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1, 54)])
        self.assertEqual((d["progress"]["named_ru_lines"], d["progress"]["unnamed_ru_lines"], d["progress"]["remaining_text_entries"], d["progress"]["complete"]), (53, 0, 99, False))
        self.assertEqual((d["source_dialogue_line_numbers"]["1"], d["source_dialogue_line_numbers"]["53"], d["progress"]["next_source_line"]), (10, 111, 118))
        self.assertTrue(all(v.strip() and "\n" not in v and not any(0x4e00 <= ord(c) <= 0x9fff for c in v) for v in d["dialogues"].values()))
    def test_decisions(self):
        d = load("story/story_chapter_6_stage_6-6_before_partial_ru_v140.json")
        self.assertEqual([v["line"] for v in d["decisions"].values()], [32, 46, 78, 93, 98])
        self.assertEqual([len(v["options"]) for v in d["decisions"].values()], [1, 3, 3, 1, 1])
        self.assertEqual(sum(len(v["options"]) for v in d["decisions"].values()), 9)
        self.assertTrue(all(len(v["options"]) == len(v["values"]) for v in d["decisions"].values()))
    def test_source_alignment(self):
        d = load("story/story_chapter_6_stage_6-6_before_partial_ru_v140.json")
        a = load("reports/CHAPTER_6_STAGE_6-6_BEFORE_SOURCE_AUDIT_v140.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"], d["source"]["en_git_blob_sha1"]), ("d9b97caa573a9fb012a391f09a7541506a372eae", "cd1b3f1efa9dd935320740521f6d200ec91b2da5"))
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["cn_plain"], a["alignment"]["cn_non_decision_commands"]), (150, 2, 139))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(a["alignment"]["source_choice_options"], 9)
    def test_manifest_index_and_selection_unchanged(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v140.json")
        q = load("reports/QA_MAIN_STORY_v140.json")
        s = load("story/story_main_selection_ru_v139.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_files"]), (107, 1))
        self.assertEqual((m["partial_scene_next_text_ordinal"], m["partial_scene_next_source_line"]), (54, 118))
        self.assertNotIn(SCENE, s["files"])
        self.assertEqual((q["partial_scene_text_entries"], q["selection_vs_historical_manifest_delta"]), (53, 1))
        idx = (ROOT / "story/CHAPTER_6_INDEX_v140.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-06_beg.txt\tpartial_first_draft\t53\t0\t53", idx)

if __name__ == "__main__":
    unittest.main()
