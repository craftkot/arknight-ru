# coding: utf-8
"""Regression invariants for 6-1 after battle partial translation v1.19."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))
class Chapter601AfterV119(unittest.TestCase):
    def test_contiguous_positions(self):
        d = load("story/story_chapter_6_stage_6-1_after_partial_ru_v119.json")
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1, 58)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        positions = list(d["source_dialogue_line_numbers"].values())
        self.assertEqual(positions, sorted(positions))
        self.assertEqual((positions[0], positions[-1], d["progress"]["first_untranslated_source_line"]), (11, 135, 141))
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]", s) for s in d["dialogues"].values()))
    def test_choices_and_source_alignment(self):
        d = load("story/story_chapter_6_stage_6-1_after_partial_ru_v119.json")
        a = load("reports/CHAPTER_6_STAGE_6-1_AFTER_SOURCE_AUDIT_v119.json")
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["cn_plain"], a["alignment"]["cn_non_decision_commands"]), (138, 0, 166))
        self.assertEqual((a["alignment"]["source_choice_commands"], a["alignment"]["source_choice_options"]), (9, 21))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual([x["line"] for x in d["decisions"].values()], [50, 130])
        self.assertTrue(all(x["values"] == ["1", "2", "3"] and len(x["options"]) == 3 for x in d["decisions"].values()))
        self.assertEqual(d["source"]["cn_git_blob_sha1"], "59437f1fe11a9e0712229888e232fa5f86f7caf9")
        self.assertEqual(d["source"]["en_git_blob_sha1"], "db3d5de405ada39426d8a936ea0308dd9e140576")
    def test_partial_progress_not_complete(self):
        d = load("story/story_chapter_6_stage_6-1_after_partial_ru_v119.json")
        self.assertEqual((d["progress"]["total_ru_text_entries"], d["progress"]["remaining_text_entries"]), (57, 81))
        self.assertFalse(d["progress"]["complete"])
        self.assertIn("NOT_GAME_TESTED", d["status"])
        self.assertIn("SCENE_NOT_COMPLETE", d["status"])
    def test_manifest_index_and_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v119.json")
        q = load("reports/QA_MAIN_STORY_v119.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_partial_files"]), (98, 1))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"], 6389)
        self.assertEqual((q["scene_ru_named"], q["scene_remaining_named"], q["included_in_complete_story_selection"]), (57, 81, False))
        self.assertEqual(m["next_file"], "obt/main/level_main_06-01_end.txt")
        idx = (ROOT / "story/CHAPTER_6_INDEX_v119.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-01_end.txt\tpartial_first_draft\t57\t0\t57", idx)
if __name__ == "__main__":
    unittest.main()
