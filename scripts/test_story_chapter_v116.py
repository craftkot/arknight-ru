# coding: utf-8
"""Regression tests for 5-ST-1 complete Russian first draft v1.16."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_st_05-01.txt"
NEW = "story/story_chapter_5_extra_5-st-1_ru_v116.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter5ExtraST01V116(unittest.TestCase):
    def test_contiguous_dialogue_and_source_lines(self):
        d = load(NEW)
        self.assertEqual(d["source_file"], REL)
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1, 108)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        self.assertEqual(d["source_dialogue_line_numbers"]["1"], 4)
        self.assertEqual(d["source_dialogue_line_numbers"]["107"], 219)
        self.assertEqual(sorted(d["source_dialogue_line_numbers"].values()), list(d["source_dialogue_line_numbers"].values()))
        self.assertTrue(all(isinstance(s, str) and s.strip() and "\\n" not in s and "\\r" not in s for s in d["dialogues"].values()))

    def test_source_hashes_progress_and_tokens(self):
        d = load(NEW)
        p, src = d["progress"], d["source"]
        self.assertEqual((p["named_ru_lines"], p["unnamed_ru_lines"], p["total_ru_text_entries"], p["remaining_text_entries"], p["complete"]), (103, 4, 107, 0, True))
        self.assertEqual(src["cn_git_blob_sha1"], "f3c8c8c19702ca4ad0ca96ba9a5c89bcc62d4ad1")
        self.assertEqual(src["en_git_blob_sha1"], "f1bce8b8d9dd6a335925464dfbc59862376f0f36")
        self.assertIn("{@nickname}", d["dialogues"]["7"])
        self.assertIn("{@nickname}", d["dialogues"]["51"])
        self.assertEqual(d["source_alignment"]["non_text_command_count"], 117)
        self.assertFalse(d["status"].find("NOT_GAME_TESTED") < 0)

    def test_decisions_and_branch_values(self):
        d = load(NEW)
        self.assertEqual(set(d["decisions"]), {str(i) for i in range(1, 7)})
        self.assertEqual([d["decisions"][str(i)]["line"] for i in range(1, 7)], [15, 33, 49, 51, 63, 88])
        self.assertEqual([len(d["decisions"][str(i)]["options"]) for i in range(1, 7)], [3, 1, 1, 1, 1, 3])
        self.assertEqual([d["decisions"][str(i)]["values"] for i in range(1, 7)], [["1","2","3"],["1"],["1"],["1"],["1"],["1","2","3"]])
        self.assertTrue(all(x.strip() for v in d["decisions"].values() for x in v["options"]))
        self.assertEqual(d["progress"]["decision_ru_options"], 10)

    def test_index_manifest_selection_and_audit(self):
        d = load(NEW)
        m = load("chronology/CHRONOLOGY_MANIFEST_v116.json")
        q = load("reports/QA_MAIN_STORY_v116.json")
        a = load("reports/CHAPTER_5_ST01_SOURCE_AUDIT_v116.json")
        s = load("story/story_main_selection_ru_v116.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_06-01_beg.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"], m["translation_integrity"]["main_story_text_entries_including_unnamed"]), (97, 6203, 6245))
        self.assertEqual((q["completed_story_files"], q["completed_story_named_ru"], q["completed_story_unnamed_ru"]), (97,6203,42))
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["en_tagged"], a["alignment"]["source_choice_options"]), (107,107,10))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(len(s["files"]), 97)
        self.assertEqual(s["files"][REL]["dialogues"], d["dialogues"])
        self.assertEqual(s["files"][REL]["decisions"], d["decisions"])
        index = (ROOT / "story/CHAPTER_5_INDEX_v116.tsv").read_text(encoding="utf-8")
        self.assertIn("level_st_05-01.txt\tfirst_draft_complete\t103\t4\t107", index)

if __name__ == "__main__":
    unittest.main()
