# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = json.loads((ROOT / "story/story_chapter_6_stage_6-14_before_partial_ru_v182.json").read_text(encoding="utf-8"))
AUDIT = json.loads((ROOT / "reports/MAIN_6-14_BEFORE_SOURCE_AUDIT_v182.json").read_text(encoding="utf-8"))
QA = json.loads((ROOT / "reports/QA_MAIN_STORY_v182.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "chronology/CHRONOLOGY_MANIFEST_v342.json").read_text(encoding="utf-8"))
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v182.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")


class TestMainStory614BeforeV182(unittest.TestCase):
    def test_partial_range_and_ordinals(self):
        p = TRANSLATION["progress"]
        rows = TRANSLATION["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"]), (120, 329, 209))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (121, 267))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 121)))
        self.assertEqual([x["source_line"] for x in rows], [
            10,12,14,16,17,19,21,23,24,25,35,37,38,40,43,44,45,46,47,49,
            51,53,54,56,57,58,60,62,64,65,66,67,68,69,71,72,74,81,82,83,
            85,87,88,89,91,93,94,96,98,99,100,101,103,105,107,108,118,119,121,122,
            123,128,129,130,131,133,135,137,139,141,142,146,147,149,151,152,153,154,
            156,158,160,161,163,165,166,168,169,172,176,177,183,185,188,189,190,
            198,199,200,202,203,205,206,208,210,212,213,231,233,234,236,238,240,
            242,243,245,247,249,264,265,266
        ])
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 118)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 2)
        self.assertTrue(all(x["text_ru"].strip() for x in rows))

    def test_russian_payload_and_placeholders(self):
        payload = "\n".join(x["text_ru"] for x in TRANSLATION["dialogues"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertEqual(payload.count("{@nickname}"), 2)
        self.assertEqual(AUDIT["alignment"]["placeholder_count_ru"], 2)
        self.assertEqual(AUDIT["alignment"]["untranslated_cjk_in_ru"], 0)
        self.assertEqual(AUDIT["alignment"]["empty_ru_entries"], 0)
        self.assertEqual(TRANSLATION["header_title_ru"], "Этап 3 (до боя)")

    def test_source_hashes_and_full_alignment(self):
        s = TRANSLATION["source"]
        a = AUDIT["alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "0af35351ae66a4f4dc21670ef30b833180154f05")
        self.assertEqual(s["en_git_blob_sha1"], "4a17d2af3e8752dc67b5601dcbc9be21615422ab")
        self.assertEqual((a["cn_physical_lines"], a["en_physical_lines"]), (720, 721))
        self.assertEqual((a["cn_named_positions"], a["en_named_positions"]), (327, 327))
        self.assertEqual((a["cn_unnamed_positions"], a["en_unnamed_positions"]), (2, 2))
        self.assertTrue(a["named_text_line_numbers_match"])
        self.assertTrue(a["unnamed_text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"])
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (391, 391))
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])

    def test_decision_and_predicate_payloads(self):
        options = TRANSLATION["decision_options_ru"]
        self.assertEqual([x["source_line"] for x in options], [143, 170, 180, 193, 195])
        self.assertEqual(sum(len(x["options_ru"]) for x in options), 7)
        self.assertEqual(options[1]["options_ru"], ["Нет.", "Нет.", "Нет."])
        self.assertEqual(options[1]["values"], ["1", "2", "3"])
        a = AUDIT["alignment"]
        self.assertEqual((a["decision_commands"], a["predicate_branches"]), (12, 12))
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual(a["decision_option_total"], 18)
        self.assertEqual(a["decision_option_strings_translated"], 7)
        r = a["translated_range"]
        self.assertEqual((r["first_ordinal"], r["last_ordinal"], r["named_positions"], r["unnamed_positions"]), (1, 120, 118, 2))
        self.assertEqual((r["command_lines_in_range"], r["decision_commands_in_range"], r["predicate_commands_in_range"]), (137, 5, 5))
        self.assertEqual((r["next_ordinal"], r["next_source_line"], r["remaining_positions"]), (121, 267, 209))

    def test_chapter_index_and_manifest(self):
        rows = [x for x in INDEX.splitlines() if x.startswith("level_main_06-14_beg.txt\t")]
        self.assertEqual(len(rows), 1)
        self.assertIn("partial_first_draft\t118\t2\t120\t0af35351ae66a4f4dc21670ef30b833180154f05\t4a17d2af3e8752dc67b5601dcbc9be21615422ab", rows[0])
        self.assertEqual(MANIFEST["version"], "v3.42")
        self.assertEqual(MANIFEST["next_file"], "obt/main/level_main_06-14_beg.txt")
        self.assertEqual((MANIFEST["next_text_ordinal"], MANIFEST["next_text_source_line"]), (121, 267))
        t = MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (119, 8671))
        self.assertEqual((t["main_story_partial_files"], t["main_story_partial_named_ru_lines"], t["main_story_partial_unnamed_ru_lines"], t["main_story_partial_text_entries"]), (1, 118, 2, 120))
        self.assertEqual(t["main_story_text_entries_including_partial"], 8902)
        self.assertEqual(t["main_story_chapter_6_text_entries_including_partial"], 2657)
        self.assertEqual(t["main_story_selection_text_entries"], 8781)
        self.assertEqual(t["main_story_partial_decision_option_strings_ru"], 7)

    def test_qa_totals_and_partial_status(self):
        self.assertEqual((QA["completed_story_files"], QA["completed_story_named_ru"], QA["completed_story_text_entries"]), (119, 8671, 8782))
        self.assertEqual((QA["partial_scene_files"], QA["partial_scene_named_ru"], QA["partial_scene_unnamed_ru"], QA["partial_scene_text_entries"]), (1, 118, 2, 120))
        self.assertEqual((QA["chapter_6_complete_files"], QA["chapter_6_complete_text_entries"]), (22, 2537))
        self.assertEqual((QA["chapter_6_partial_files"], QA["chapter_6_partial_text_entries"], QA["chapter_6_text_entries_including_partial"]), (1, 120, 2657))
        self.assertEqual(QA["next_scene"]["remaining"], 209)
        self.assertEqual(QA["next_scene"]["decision_option_strings_translated"], 7)
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])

    def test_resource_to_operation_mapping(self):
        mapping = AUDIT["stage_mapping"]
        self.assertEqual(mapping["source_resource_key"], "level_main_06-14_beg.txt")
        self.assertEqual(mapping["in_game_operation"], "6-16")
        self.assertEqual(mapping["section"], "Before Operation")
        self.assertIn("6-16/Story", mapping["wiki_url"])
        self.assertEqual(QA["stage_mapping"]["in_game_operation"], "6-16")

    def test_readme_and_glossary(self):
        self.assertIn("v3.42", README)
        self.assertIn("120/329", README)
        self.assertIn("6-16 Before Operation", README)
        self.assertIn("level_main_06-14_beg.txt", README)
        self.assertIn("GreyThroat / 灰喉 — Грейтроут", TERMS)


if __name__ == "__main__":
    unittest.main()
