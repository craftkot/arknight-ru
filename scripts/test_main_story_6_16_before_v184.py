# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

TRANSLATION = load("story/story_chapter_6_stage_6-14_before_partial_ru_v184.json")
AUDIT = load("reports/MAIN_6-14_BEFORE_SOURCE_AUDIT_v184.json")
QA = load("reports/QA_MAIN_STORY_v184.json")
MANIFEST = load("chronology/CHRONOLOGY_MANIFEST_v344.json")
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v184.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

EXPECTED_NEW_LINES = [434,435,436,437,439,440,442,443,444,446,448,449,451,453,454,456,458,460,462,463,464,466,468,470,478,480,482,490,492,494,495,496,497,499,500,501,502,504,506,508,510,511,512,513,514,515,516,522,523,524,525,526,528,530,531,532,540,541,543,545]
EXPECTED_NEW_ORDINALS = list(range(181, 241))


class TestMainStory616BeforeV184(unittest.TestCase):
    def test_contiguous_partial_range(self):
        p = TRANSLATION["progress"]
        rows = TRANSLATION["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"]), (240, 329, 89))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (241, 546))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 241)))
        self.assertEqual([x["source_line"] for x in rows[-60:]], EXPECTED_NEW_LINES)
        self.assertEqual([x["ordinal"] for x in rows[-60:]], EXPECTED_NEW_ORDINALS)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 238)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 2)
        self.assertTrue(all(x["text_ru"].strip() for x in rows))

    def test_russian_payload_and_source_markup(self):
        payload = "\n".join(x["text_ru"] for x in TRANSLATION["dialogues"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertEqual(payload.count("{@nickname}"), 2)
        marker = next(x for x in TRANSLATION["dialogues"] if x["source_line"] == 377)
        self.assertEqual(marker["text_ru"].count("**"), 1)
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
        self.assertEqual([x["source_line"] for x in options], [143, 170, 180, 193, 195, 385, 519])
        self.assertEqual(sum(len(x["options_ru"]) for x in options), 13)
        self.assertEqual(options[-1]["values"], ["1", "2", "3"])
        self.assertEqual(len(options[-1]["options_ru"]), 3)
        a = AUDIT["alignment"]
        self.assertEqual((a["decision_commands"], a["predicate_branches"]), (12, 12))
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual((a["decision_option_total"], a["decision_option_strings_translated"], a["decision_option_strings_remaining"]), (18, 13, 5))
        r = a["translated_range"]
        self.assertEqual((r["first_ordinal"], r["last_ordinal"], r["named_positions"], r["unnamed_positions"]), (1, 240, 238, 2))
        self.assertEqual((r["command_lines_in_range"], r["decision_commands_in_range"], r["predicate_commands_in_range"]), (295, 7, 7))
        self.assertEqual((r["next_ordinal"], r["next_source_line"], r["remaining_positions"]), (241, 546, 89))

    def test_index_manifest_and_qa(self):
        rows = [x for x in INDEX.splitlines() if x.startswith("level_main_06-14_beg.txt\t")]
        self.assertEqual(len(rows), 1)
        self.assertIn("partial_first_draft\t238\t2\t240\t0af35351ae66a4f4dc21670ef30b833180154f05\t4a17d2af3e8752dc67b5601dcbc9be21615422ab", rows[0])
        self.assertEqual(MANIFEST["version"], "v3.44")
        self.assertEqual((MANIFEST["next_text_ordinal"], MANIFEST["next_text_source_line"]), (241, 546))
        t = MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_partial_named_ru_lines"], t["main_story_partial_unnamed_ru_lines"], t["main_story_partial_text_entries"]), (238, 2, 240))
        self.assertEqual(t["main_story_named_ru_lines_including_partial"], 8909)
        self.assertEqual(t["main_story_text_entries_including_partial"], 9022)
        self.assertEqual(t["main_story_chapter_6_text_entries_including_partial"], 2777)
        self.assertEqual((t["main_story_partial_decision_option_strings_ru"], t["main_story_partial_decision_option_strings_remaining"]), (13, 5))
        self.assertEqual((QA["partial_scene_named_ru"], QA["partial_scene_unnamed_ru"], QA["partial_scene_text_entries"]), (238, 2, 240))
        self.assertEqual(QA["next_scene"]["remaining"], 89)
        self.assertEqual(QA["next_scene"]["decision_option_strings_translated"], 13)
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])

    def test_mapping_readme_and_terms(self):
        self.assertEqual(AUDIT["stage_mapping"]["in_game_operation"], "6-16")
        self.assertEqual(AUDIT["stage_mapping"]["section"], "Before Operation")
        self.assertIn("6-16/Story", AUDIT["stage_mapping"]["wiki_url"])
        self.assertIn("v3.44", README)
        self.assertIn("240/329", README)
        self.assertIn("6-16 Before Operation", README)
        self.assertIn("Следующая позиция — №241", README)
        self.assertIn("GreyThroat / 灰喉 — Грейтроут", TERMS)


if __name__ == "__main__":
    unittest.main()
