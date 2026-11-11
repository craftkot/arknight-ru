# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

TRANSLATION = load("story/story_chapter_6_stage_6-6_interlude_partial_ru_v187.json")
AUDIT = load("reports/MAIN_6-6_INTERLUDE_SOURCE_AUDIT_v187.json")
QA = load("reports/QA_MAIN_STORY_v187.json")
MANIFEST = load("chronology/CHRONOLOGY_MANIFEST_v347.json")
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v187.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
EXPECTED_SOURCE_LINES = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,34,35,36,37,38,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,61,62,63,68,69,70,71,72,76,77,78,79,80,85,86,87,88,89,90,91,92,93,94,95,96,100,101,102,103,104,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133]

class TestMainStory66InterludeV187(unittest.TestCase):
    def test_partial_progress_and_ordinals(self):
        self.assertEqual(TRANSLATION["version"], "v1.87")
        self.assertIn("PARTIAL_FIRST_DRAFT", TRANSLATION["status"])
        p, rows = TRANSLATION["progress"], TRANSLATION["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"]), (100, 203, 103))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (101, 134))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 101)))
        self.assertEqual([x["source_line"] for x in rows], EXPECTED_SOURCE_LINES)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 82)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 18)
        self.assertEqual(rows[0]["text_ru"], "Эно, о чём эта книга?")
        self.assertEqual(rows[-1]["text_ru"], "Они тоже били меня. И тебя ранили.")

    def test_translation_payload_and_names(self):
        rows = TRANSLATION["dialogues"]
        payload = "\n".join(x["text_ru"] for x in rows)
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertTrue(all(x["text_ru"].strip() for x in rows))
        self.assertEqual(rows[0]["speaker_cn"], "？？？")
        self.assertEqual(rows[1]["speaker_cn"], "伊诺")
        self.assertEqual(rows[3]["speaker_cn"], "萨沙")
        self.assertEqual(TRANSLATION["decision_options_ru"], [])
        self.assertEqual(TRANSLATION["progress"]["decision_option_strings_remaining"], 0)
        self.assertIn("Eno / 伊诺 — Эно", TERMS)
        self.assertIn("Sasha / 萨沙 — Саша", TERMS)

    def test_source_hashes_and_full_structure(self):
        s, a = TRANSLATION["source"], TRANSLATION["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "026bf7f38a9e0794661a54635a137df90ff4fba0")
        self.assertEqual(s["en_git_blob_sha1"], "9eefd6f8b7e7a7956d7a5e4d9464004cd6ad9676")
        self.assertEqual((s["cn_physical_lines"], s["en_physical_lines"]), (312, 313))
        self.assertEqual((a["cn_text_positions"], a["en_text_positions"]), (203, 203))
        self.assertEqual((a["cn_named_positions"], a["en_named_positions"]), (174, 174))
        self.assertEqual((a["cn_unnamed_positions"], a["en_unnamed_positions"]), (29, 29))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (109, 109))
        self.assertTrue(a["named_text_line_numbers_match"])
        self.assertTrue(a["unnamed_text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"])
        self.assertTrue(a["speaker_label_names_match_after_anonymous_normalization"])
        self.assertEqual(a["speaker_label_spelling_exceptions"], [{"line": 188, "cn": "？？？", "en": "????"}])
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertEqual((a["decision_commands"], a["predicate_branches"], a["decision_option_total"]), (0, 0, 0))
        self.assertEqual(a["translated_range"]["translated_source_lines"], EXPECTED_SOURCE_LINES)
        self.assertEqual(a["untranslated_positions"], 103)
        self.assertEqual((a["empty_ru_entries"], a["untranslated_cjk_in_ru"]), (0, 0))
        self.assertEqual(AUDIT["alignment"]["command_lines_cn"], 109)

    def test_index_manifest_and_qa(self):
        row = [x for x in INDEX.splitlines() if x.startswith("level_st_06-01.txt")]
        self.assertEqual(len(row), 1)
        self.assertIn("partial_first_draft\t82\t18\t100\t026bf7f38a9e0794661a54635a137df90ff4fba0\t9eefd6f8b7e7a7956d7a5e4d9464004cd6ad9676", row[0])
        self.assertEqual(MANIFEST["version"], "v3.47")
        self.assertEqual(MANIFEST["next_file"], "obt/main/level_st_06-01.txt")
        self.assertEqual((MANIFEST["next_text_ordinal"], MANIFEST["next_text_source_line"]), (101, 134))
        t = MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_partial_files"], t["main_story_partial_text_entries"]), (120, 1, 100))
        self.assertEqual((t["main_story_partial_named_ru_lines"], t["main_story_partial_unnamed_ru_lines"]), (82, 18))
        self.assertEqual((t["main_story_selection_files"], t["main_story_selection_text_entries"], t["main_story_selection_vs_historical_manifest_delta"]), (120, 9110, 1))
        self.assertEqual((t["main_story_chapter_6_files"], t["main_story_chapter_6_partial_files"], t["main_story_chapter_6_partial_text_entries"]), (23, 1, 100))
        self.assertEqual((QA["completed_story_files"], QA["partial_scene_files"], QA["partial_scene_text_entries"]), (120, 1, 100))
        self.assertEqual(QA["next_scene"]["source_file"], "obt/main/level_st_06-01.txt")
        self.assertEqual((QA["next_scene"]["translated"], QA["next_scene"]["total"], QA["next_scene"]["next_ordinal"]), (100, 203, 101))
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])
        self.assertIn("level_st_06-02.txt", README)
        self.assertIn("100/203", README)
        self.assertIn("6-6 Interlude", README)

if __name__ == "__main__":
    unittest.main()
