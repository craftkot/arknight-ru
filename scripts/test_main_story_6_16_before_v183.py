# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

TRANSLATION = load("story/story_chapter_6_stage_6-14_before_partial_ru_v183.json")
AUDIT = load("reports/MAIN_6-14_BEFORE_SOURCE_AUDIT_v183.json")
QA = load("reports/QA_MAIN_STORY_v183.json")
MANIFEST = load("chronology/CHRONOLOGY_MANIFEST_v343.json")
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v183.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

EXPECTED_NEW_LINES = [267,269,270,272,273,275,277,278,280,282,286,287,289,291,293,295,296,298,299,300,301,303,304,306,307,309,310,312,314,316,318,320,352,357,359,365,368,369,371,373,375,377,379,380,381,382,388,389,390,391,392,393,395,397,399,401,403,428,430,432]
EXPECTED_NEW_ORDINALS = list(range(121, 181))


class TestMainStory616BeforeV183(unittest.TestCase):
    def test_contiguous_partial_range(self):
        p = TRANSLATION["progress"]
        rows = TRANSLATION["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"]), (180, 329, 149))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (181, 434))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 181)))
        self.assertEqual([x["source_line"] for x in rows[-60:]], EXPECTED_NEW_LINES)
        self.assertEqual([x["ordinal"] for x in rows[-60:]], EXPECTED_NEW_ORDINALS)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 178)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 2)
        self.assertTrue(all(x["text_ru"].strip() for x in rows))

    def test_russian_payload_and_source_markup(self):
        payload = "\n".join(x["text_ru"] for x in TRANSLATION["dialogues"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertEqual(payload.count("{@nickname}"), 2)
        self.assertEqual(TRANSLATION["dialogues"][-19]["source_line"], 377)
        self.assertEqual(TRANSLATION["dialogues"][-19]["text_ru"].count("**"), 1)
        self.assertEqual(AUDIT["alignment"]["cn_only_markup_source_lines"], [377])
        self.assertTrue(AUDIT["alignment"]["cn_only_markup_ru_preserved"])
        self.assertEqual(AUDIT["alignment"]["untranslated_cjk_in_ru"], 0)
        self.assertEqual(AUDIT["alignment"]["empty_ru_entries"], 0)

    def test_source_hashes_and_alignment(self):
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

    def test_decision_options_and_predicates(self):
        options = TRANSLATION["decision_options_ru"]
        self.assertEqual([x["source_line"] for x in options], [143, 170, 180, 193, 195, 385])
        self.assertEqual(sum(len(x["options_ru"]) for x in options), 10)
        self.assertEqual(options[-1]["values"], ["1", "2", "3"])
        self.assertEqual(len(options[-1]["options_ru"]), 3)
        a = AUDIT["alignment"]
        self.assertEqual((a["decision_commands"], a["predicate_branches"]), (12, 12))
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual((a["decision_option_total"], a["decision_option_strings_translated"], a["decision_option_strings_remaining"]), (18, 10, 8))
        r = a["translated_range"]
        self.assertEqual((r["first_ordinal"], r["last_ordinal"], r["named_positions"], r["unnamed_positions"]), (1, 180, 178, 2))
        self.assertEqual((r["command_lines_in_range"], r["decision_commands_in_range"], r["predicate_commands_in_range"]), (243, 6, 6))
        self.assertEqual((r["next_ordinal"], r["next_source_line"], r["remaining_positions"]), (181, 434, 149))

    def test_index_manifest_and_qa(self):
        rows = [x for x in INDEX.splitlines() if x.startswith("level_main_06-14_beg.txt\t")]
        self.assertEqual(len(rows), 1)
        self.assertIn("partial_first_draft\t178\t2\t180\t0af35351ae66a4f4dc21670ef30b833180154f05\t4a17d2af3e8752dc67b5601dcbc9be21615422ab", rows[0])
        self.assertEqual(MANIFEST["version"], "v3.43")
        self.assertEqual((MANIFEST["next_text_ordinal"], MANIFEST["next_text_source_line"]), (181, 434))
        t = MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_partial_named_ru_lines"], t["main_story_partial_unnamed_ru_lines"], t["main_story_partial_text_entries"]), (178, 2, 180))
        self.assertEqual(t["main_story_named_ru_lines_including_partial"], 8849)
        self.assertEqual(t["main_story_text_entries_including_partial"], 8962)
        self.assertEqual(t["main_story_chapter_6_text_entries_including_partial"], 2717)
        self.assertEqual((t["main_story_partial_decision_option_strings_ru"], t["main_story_partial_decision_option_strings_remaining"]), (10, 8))
        self.assertEqual((QA["partial_scene_named_ru"], QA["partial_scene_unnamed_ru"], QA["partial_scene_text_entries"]), (178, 2, 180))
        self.assertEqual(QA["next_scene"]["remaining"], 149)
        self.assertEqual(QA["next_scene"]["decision_option_strings_translated"], 10)
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])

    def test_mapping_readme_and_terms(self):
        self.assertEqual(AUDIT["stage_mapping"]["in_game_operation"], "6-16")
        self.assertEqual(AUDIT["stage_mapping"]["section"], "Before Operation")
        self.assertIn("6-16/Story", AUDIT["stage_mapping"]["wiki_url"])
        self.assertIn("v3.43", README)
        self.assertIn("180/329", README)
        self.assertIn("6-16 Before Operation", README)
        self.assertIn("Следующая позиция — №181", README)
        self.assertIn("GreyThroat / 灰喉 — Грейтроут", TERMS)


if __name__ == "__main__":
    unittest.main()
