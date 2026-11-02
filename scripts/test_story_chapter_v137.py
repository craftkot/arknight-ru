# coding: utf-8
"""Regression checks for completed CN-primary 6-5 before battle v1.37."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENE = "obt/main/level_main_06-05_beg.txt"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter605BeforeV137(unittest.TestCase):
    def test_complete_contiguous_russian_dialogues(self):
        d = load("story/story_chapter_6_stage_6-5_before_ru_v137.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1, 111)])
        self.assertEqual((d["progress"]["named_ru_lines"], d["progress"]["remaining_text_entries"], d["progress"]["complete"]), (110, 0, True))
        self.assertEqual(d["source_dialogue_line_numbers"]["110"], 215)
        self.assertEqual(d["decisions"], {})
        self.assertTrue(all(s.strip() and "\n" not in s and not any(0x4e00 <= ord(c) <= 0x9fff for c in s) for s in d["dialogues"].values()))

    def test_prior_87_entries_preserved(self):
        old = load("story/story_chapter_6_stage_6-5_before_partial_ru_v136.json")
        new = load("story/story_chapter_6_stage_6-5_before_ru_v137.json")
        self.assertEqual(old["dialogues"], {k: new["dialogues"][k] for k in old["dialogues"]})
        self.assertEqual(old["source_dialogue_line_numbers"], new["source_dialogue_line_numbers"])
        self.assertEqual(old["source_dialogue_speakers_en"], new["source_dialogue_speakers_en"])

    def test_source_pins_and_structure(self):
        d = load("story/story_chapter_6_stage_6-5_before_ru_v137.json")
        a = load("reports/CHAPTER_6_STAGE_6-5_BEFORE_SOURCE_AUDIT_v137.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"], d["source"]["en_git_blob_sha1"]), ("21dbb955fd9e12151a8754930dae6c6e348b1fc2", "aedc8fd8cfa764ecccdcadfd81260cdd27c4fa0e"))
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["en_tagged"], a["alignment"]["cn_non_decision_commands"]), (110, 110, 109))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual((a["alignment"]["ru_tagged_entries"], a["alignment"]["ru_remaining_entries"]), (110, 0))

    def test_selection_manifest_index_and_qa(self):
        s = load("story/story_main_selection_ru_v137.json")
        d = load("story/story_chapter_6_stage_6-5_before_ru_v137.json")
        self.assertEqual(len(s["files"]), 106)
        self.assertEqual(s["files"][SCENE]["dialogues"], d["dialogues"])
        self.assertEqual(sum(len(v.get("dialogues", {})) + len(v.get("plain_lines", {})) for v in s["files"].values()), 7094)
        m = load("chronology/CHRONOLOGY_MANIFEST_v137.json")
        q = load("reports/QA_MAIN_STORY_v137.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_files"]), (106, 0))
        self.assertEqual((q["scene_ru_named"], q["scene_remaining_named"], q["included_in_complete_story_selection"]), (110, 0, True))
        self.assertEqual(m["next_file"], "obt/main/level_main_06-05_end.txt")
        idx = (ROOT / "story/CHAPTER_6_INDEX_v137.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-05_beg.txt\tfirst_draft_complete\t110\t0\t110", idx)

if __name__ == "__main__":
    unittest.main()
