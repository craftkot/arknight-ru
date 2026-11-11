# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

TRANSLATION = load("story/story_chapter_6_stage_6-14_before_ru_v186.json")
AUDIT = load("reports/MAIN_6-14_BEFORE_SOURCE_AUDIT_v186.json")
QA = load("reports/QA_MAIN_STORY_v186.json")
MANIFEST = load("chronology/CHRONOLOGY_MANIFEST_v346.json")
SELECTION = load("story/story_main_selection_ru_v186.json")
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v186.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

EXPECTED_NEW_LINES = [646,647,648,649,650,658,659,671,679,680,684,686,687,688,689,691,692,694,696,698,700,701,702,704,706,708,714,715,716]
EXPECTED_DECISION_LINES = [143,170,180,193,195,385,519,592,603,643,681,711]

class TestMainStory616BeforeV186(unittest.TestCase):
    def test_complete_first_draft_and_ordinals(self):
        self.assertEqual(TRANSLATION["version"], "v1.86")
        self.assertIn("COMPLETE_FIRST_DRAFT", TRANSLATION["status"])
        p = TRANSLATION["progress"]
        rows = TRANSLATION["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"]), (329,329,0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_ordinal"])
        self.assertIsNone(p["next_source_line"])
        self.assertEqual([x["ordinal"] for x in rows], list(range(1,330)))
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 327)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 2)
        self.assertEqual(rows[-29]["source_line"], 646)
        self.assertEqual(rows[-1]["source_line"], 716)

    def test_final_tail_translation(self):
        rows = TRANSLATION["dialogues"][-29:]
        self.assertEqual([x["source_line"] for x in rows], EXPECTED_NEW_LINES)
        self.assertEqual([x["ordinal"] for x in rows], list(range(301,330)))
        self.assertTrue(all(x["kind"] == "named" for x in rows))
        self.assertEqual(rows[0]["text_ru"], "Доктор {@nickname}…")
        self.assertEqual(rows[7]["text_ru"], "Если вы победите меня, кому-то из вас, возможно, повезёт выжить —")
        self.assertEqual(rows[-1]["text_ru"], "…Победите меня. Дайте мне увидеть надежду.")
        self.assertEqual(rows[23]["speaker_cn"], "煌")
        self.assertEqual(rows[24]["speaker_cn"], "灰喉")

    def test_all_decision_options(self):
        options = TRANSLATION["decision_options_ru"]
        self.assertEqual([x["source_line"] for x in options], EXPECTED_DECISION_LINES)
        self.assertEqual(sum(len(x["options_ru"]) for x in options), 18)
        self.assertEqual(options[-3]["options_ru"], ["…Говори, Амия."])
        self.assertEqual(options[-2]["options_ru"], ["Надеюсь, ты сдержишь своё обещание."])
        self.assertEqual(options[-1]["options_ru"], ["ФростНова!"])
        self.assertTrue(all(x["values"] == ["1"] for x in options[-3:]))

    def test_russian_payload_placeholders_and_markup(self):
        payload = "\n".join(x["text_ru"] for x in TRANSLATION["dialogues"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertEqual(payload.count("{@nickname}"), 3)
        self.assertTrue(all(x["text_ru"].strip() for x in TRANSLATION["dialogues"]))
        marker = next(x for x in TRANSLATION["dialogues"] if x["source_line"] == 377)
        self.assertEqual(marker["text_ru"].count("**"), 1)
        a = AUDIT["alignment"]
        self.assertEqual(a["cn_only_markup_source_lines"], [377])
        self.assertTrue(a["cn_only_markup_ru_preserved"])
        self.assertEqual((a["untranslated_cjk_in_ru"], a["empty_ru_entries"]), (0,0))
        self.assertEqual((a["inline_markup_pairs_ru"], a["inline_markup_unpaired_source_markers_ru"]), (1,1))

    def test_source_hashes_and_full_structure(self):
        s = TRANSLATION["source"]
        a = AUDIT["alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "0af35351ae66a4f4dc21670ef30b833180154f05")
        self.assertEqual(s["en_git_blob_sha1"], "4a17d2af3e8752dc67b5601dcbc9be21615422ab")
        self.assertEqual((a["cn_physical_lines"], a["en_physical_lines"]), (720,721))
        self.assertEqual((a["cn_named_positions"], a["en_named_positions"]), (327,327))
        self.assertEqual((a["cn_unnamed_positions"], a["en_unnamed_positions"]), (2,2))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (391,391))
        self.assertTrue(a["named_text_line_numbers_match"])
        self.assertTrue(a["unnamed_text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"])
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual((a["decision_commands"],a["predicate_branches"]), (12,12))
        self.assertEqual((a["decision_option_total"],a["decision_option_strings_translated"],a["decision_option_strings_remaining"]), (18,18,0))
        self.assertEqual(a["translated_range"]["translated_source_lines"], [x["source_line"] for x in TRANSLATION["dialogues"]])
        self.assertEqual(a["translated_range"]["command_lines_in_range"], 391)

    def test_index_manifest_selection_and_qa(self):
        row = [x for x in INDEX.splitlines() if x.startswith("level_main_06-14_beg.txt\t")]
        self.assertEqual(len(row), 1)
        self.assertIn("first_draft_complete\t327\t2\t329\t0af35351ae66a4f4dc21670ef30b833180154f05\t4a17d2af3e8752dc67b5601dcbc9be21615422ab", row[0])
        self.assertEqual(MANIFEST["version"], "v3.46")
        self.assertEqual(MANIFEST["next_file"], "obt/main/level_main_06-15_end.txt")
        self.assertEqual((MANIFEST["next_text_ordinal"],MANIFEST["next_text_source_line"]), (1,16))
        t = MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_files"],t["main_story_named_ru_lines"],t["main_story_unnamed_ru_lines"]), (120,8998,113))
        self.assertEqual((t["main_story_partial_files"],t["main_story_partial_text_entries"]), (0,0))
        self.assertEqual((t["main_story_selection_files"],t["main_story_selection_text_entries"],t["main_story_selection_vs_historical_manifest_delta"]), (120,9110,1))
        self.assertEqual((t["main_story_chapter_6_files"],t["main_story_chapter_6_complete_text_entries"]), (23,2866))
        entry = SELECTION["files"]["obt/main/level_main_06-14_beg.txt"]
        self.assertEqual((entry["dialogue_count"],entry["named_dialogue_count"],entry["unnamed_dialogue_count"]), (329,327,2))
        self.assertEqual(len(entry["dialogues"]), 329)
        self.assertEqual(len(entry["decisions"]), 12)
        self.assertEqual(SELECTION["summary"]["complete_files"], 120)
        self.assertEqual(SELECTION["summary"]["total_dialogue_entries"], 9110)
        self.assertEqual((QA["completed_story_files"],QA["partial_scene_files"],QA["chapter_6_complete_files"]), (120,0,23))
        self.assertEqual((QA["completed_scene_audit"]["text_positions"],QA["completed_scene_audit"]["decision_options_translated"]), (329,18))
        self.assertEqual(QA["next_scene"]["source_file"], "obt/main/level_main_06-15_end.txt")
        self.assertEqual(QA["next_scene"]["remaining"], 89)
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])

    def test_next_scene_source_mapping_and_project_terms(self):
        self.assertEqual(MANIFEST["next_source"]["cn_git_blob_sha1"], "b8dc8453340f5eeb673c81bc82ad81be9ac7280a")
        self.assertEqual(MANIFEST["next_source"]["en_git_blob_sha1"], "bc8db9e49aa225aef8e57bf62c87488d3cd05ff9")
        self.assertEqual((MANIFEST["next_source"]["text_positions"],MANIFEST["next_source"]["command_lines"]), (89,97))
        self.assertEqual((MANIFEST["next_source"]["decision_commands"],MANIFEST["next_source"]["predicate_branches"],MANIFEST["next_source"]["decision_option_strings"]), (15,15,20))
        self.assertIn("v3.46", README)
        self.assertIn("329/329", README)
        self.assertIn("6-17 After Operation", README)
        self.assertIn("Следующая позиция — №301", README)
        self.assertIn("GreyThroat / 灰喉 — Грейтроут", TERMS)

if __name__ == "__main__":
    unittest.main()
