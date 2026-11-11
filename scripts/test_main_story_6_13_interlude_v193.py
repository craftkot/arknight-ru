# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

TRANSLATION = load("story/story_chapter_6_stage_6-13_interlude_partial_ru_v193.json")
AUDIT = load("reports/MAIN_6-13_INTERLUDE_SOURCE_AUDIT_v193.json")
QA = load("reports/QA_MAIN_STORY_v193.json")
MANIFEST = load("chronology/CHRONOLOGY_MANIFEST_v353.json")
SELECTION = load("story/story_main_selection_ru_v189.json")
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v193.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

NEW_LINES = list(range(301, 313))

class TestMainStory613InterludeV193(unittest.TestCase):
    def test_progress_ordinals_and_continuity(self):
        self.assertEqual(TRANSLATION["version"], "v1.93")
        p, rows = TRANSLATION["progress"], TRANSLATION["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (192, 269, 77, False))
        self.assertEqual((p["named_translated"], p["named_total"]), (180, 257))
        self.assertEqual((p["unnamed_translated"], p["unnamed_total"]), (12, 12))
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (193, 313))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 193)))
        self.assertEqual([x["source_line"] for x in rows[-12:]], NEW_LINES)
        self.assertEqual([x["ordinal"] for x in rows[-12:]], list(range(181, 193)))
        self.assertTrue(all(x["kind"] == "named" and x["speaker_cn"] == "霜星" for x in rows[-12:]))

    def test_russian_payload_and_placeholders(self):
        rows = TRANSLATION["dialogues"]
        payload = "\\n".join(x["text_ru"] for x in rows)
        options = "\\n".join(s for d in TRANSLATION["decision_options_ru"] for s in d["options_ru"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload + options))
        self.assertTrue(all(x["text_ru"].strip() for x in rows))
        self.assertEqual(len(TRANSLATION["decision_options_ru"]), 26)
        self.assertEqual(sum(len(x["options_ru"]) for x in TRANSLATION["decision_options_ru"]), 39)
        self.assertEqual(payload.count("{@nickname}"), 3)
        self.assertEqual(TRANSLATION["source_alignment"]["placeholder_count_ru"], 3)

    def test_pinned_sources_and_structure(self):
        s, a = TRANSLATION["source"], TRANSLATION["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "ffa8947a78abc196f2ebfcb90ae2283ee136c953")
        self.assertEqual(s["en_git_blob_sha1"], "79204a97fedbc6e1950440f86a618c8d6efa37ba")
        self.assertEqual((a["cn_text_positions"], a["en_text_positions"]), (269, 269))
        self.assertEqual((a["cn_named_positions"], a["en_named_positions"]), (257, 257))
        self.assertEqual((a["cn_unnamed_positions"], a["en_unnamed_positions"]), (12, 12))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (141, 141))
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual((a["translated_range"]["ordinal_start"], a["translated_range"]["ordinal_end"]), (1, 192))
        self.assertEqual(a["translated_range"]["command_lines_in_range"], 120)
        self.assertEqual(a["translated_range"]["decision_commands"], 26)
        self.assertEqual(a["translated_range"]["decision_option_strings"], 39)
        self.assertEqual(a["translated_range"]["predicate_branches"], 37)
        self.assertEqual(a["untranslated_positions"], 77)
        self.assertEqual(AUDIT["integrity"]["translated_text_positions"], 192)
        self.assertEqual(AUDIT["integrity"]["next_source_line"], 313)

    def test_index_manifest_qa_and_selection(self):
        rows = [x for x in INDEX.splitlines() if x.startswith("level_st_06-02.txt")]
        self.assertEqual(len(rows), 1)
        self.assertIn("level_st_06-02.txt\\tpartial_first_draft\\t180\\t12\\t192\\tffa8947a78abc196f2ebfcb90ae2283ee136c953\\t79204a97fedbc6e1950440f86a618c8d6efa37ba", rows[0])
        self.assertEqual(MANIFEST["version"], "v3.53")
        self.assertEqual((MANIFEST["next_text_ordinal"], MANIFEST["next_text_source_line"]), (193, 313))
        t = MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_partial_files"], t["main_story_partial_text_entries"]), (1, 192))
        self.assertEqual((t["main_story_partial_named_ru_lines"], t["main_story_partial_unnamed_ru_lines"]), (180, 12))
        self.assertEqual((t["main_story_partial_decision_option_strings_ru"], t["main_story_partial_decision_option_strings_total"]), (39, 53))
        self.assertEqual((t["main_story_partial_predicate_branches_ru"], t["main_story_partial_predicate_branches_total"]), (37, 45))
        self.assertNotIn("obt/main/level_st_06-02.txt", SELECTION["files"])
        self.assertEqual((QA["partial_scene_text_entries"], QA["partial_scene_named_ru"], QA["partial_scene_unnamed_ru"]), (192, 180, 12))
        self.assertEqual((QA["next_scene"]["translated"], QA["next_scene"]["next_ordinal"], QA["next_scene"]["next_source_line"]), (192, 193, 313))
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])
        self.assertIn("192/269", README)
        self.assertIn("Следующая позиция — №193", README)

if __name__ == "__main__":
    unittest.main()
