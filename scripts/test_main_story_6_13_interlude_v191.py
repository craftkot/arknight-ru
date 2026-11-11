# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

TRANSLATION = load("story/story_chapter_6_stage_6-13_interlude_partial_ru_v191.json")
AUDIT = load("reports/MAIN_6-13_INTERLUDE_SOURCE_AUDIT_v191.json")
QA = load("reports/QA_MAIN_STORY_v191.json")
MANIFEST = load("chronology/CHRONOLOGY_MANIFEST_v351.json")
SELECTION = load("story/story_main_selection_ru_v189.json")
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v191.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
OLD_LINES = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,31,32,33,34,41,42,52,58,59,62,63,66,67,69,70,71,73,76,77,78,82,83,84,85,86,87,88,91,94,100]
NEW_LINES = list(range(101,131)) + [137,138] + list(range(142,150)) + [161,162,163,164,171,172,173,174,177,178,179,183,186,187,188,191,194,196,198,200,204,205]

class TestMainStory613InterludeV191(unittest.TestCase):
    def test_progress_ordinals_and_types(self):
        self.assertEqual(TRANSLATION["version"], "v1.91")
        self.assertIn("PARTIAL_FIRST_DRAFT", TRANSLATION["status"])
        p, rows = TRANSLATION["progress"], TRANSLATION["dialogues"]
        self.assertEqual((p["translated"],p["total"],p["remaining"],p["complete"]),(112,269,157,False))
        self.assertEqual((p["named_translated"],p["named_total"]),(100,257))
        self.assertEqual((p["unnamed_translated"],p["unnamed_total"]),(12,12))
        self.assertEqual((p["next_ordinal"],p["next_source_line"]),(113,206))
        self.assertEqual([x["ordinal"] for x in rows],list(range(1,113)))
        self.assertEqual([x["source_line"] for x in rows],OLD_LINES+NEW_LINES)
        self.assertEqual(sum(x["kind"]=="named" for x in rows),100)
        self.assertEqual(sum(x["kind"]=="unnamed" for x in rows),12)
        self.assertEqual(TRANSLATION["source_alignment"]["translated_range"]["ordinal_end"],112)
        self.assertEqual(TRANSLATION["source_alignment"]["untranslated_positions"],157)

    def test_russian_payload_and_choices(self):
        rows=TRANSLATION["dialogues"]
        payload="\n".join(x["text_ru"] for x in rows)
        options="\n".join(s for d in TRANSLATION["decision_options_ru"] for s in d["options_ru"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]",payload+options))
        self.assertTrue(all(x["text_ru"].strip() for x in rows))
        self.assertEqual(len(TRANSLATION["decision_options_ru"]),15)
        self.assertEqual(sum(len(x["options_ru"]) for x in TRANSLATION["decision_options_ru"]),26)
        self.assertEqual(TRANSLATION["progress"]["decision_option_strings_remaining"],27)
        self.assertEqual(rows[-1]["text_ru"],"Хе-хе…")
        self.assertEqual(TRANSLATION["header_title_ru"],"Шестой этап (после боя)")
        self.assertEqual(TRANSLATION["decision_options_ru"][-2]["options_ru"],["(Съесть конфету)"]*3)

    def test_sources_and_structure(self):
        s,a=TRANSLATION["source"],TRANSLATION["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"],"ffa8947a78abc196f2ebfcb90ae2283ee136c953")
        self.assertEqual(s["en_git_blob_sha1"],"79204a97fedbc6e1950440f86a618c8d6efa37ba")
        self.assertEqual((a["cn_text_positions"],a["en_text_positions"]),(269,269))
        self.assertEqual((a["cn_named_positions"],a["en_named_positions"]),(257,257))
        self.assertEqual((a["cn_unnamed_positions"],a["en_unnamed_positions"]),(12,12))
        self.assertEqual((a["command_lines_cn"],a["command_lines_en"]),(141,141))
        self.assertTrue(a["named_text_line_numbers_match"])
        self.assertTrue(a["unnamed_text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"])
        self.assertTrue(a["speaker_label_names_match_after_localization"])
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual((a["translated_range"]["command_lines_in_range"],a["translated_range"]["decision_commands"],a["translated_range"]["decision_option_strings"],a["translated_range"]["predicate_branches"]),(93,15,26,23))
        self.assertEqual((a["translated_chunks"][-1]["ordinal_start"],a["translated_chunks"][-1]["ordinal_end"]),(51,112))
        self.assertEqual(AUDIT["integrity"]["translated_text_positions"],112)
        self.assertEqual(AUDIT["integrity"]["next_source_line"],206)

    def test_index_manifest_qa_and_selection(self):
        rows=[x for x in INDEX.splitlines() if x.startswith("level_st_06-02.txt")]
        self.assertEqual(len(rows),1)
        self.assertIn("partial_first_draft\t100\t12\t112\tffa8947a78abc196f2ebfcb90ae2283ee136c953\t79204a97fedbc6e1950440f86a618c8d6efa37ba",rows[0])
        self.assertEqual(MANIFEST["version"],"v3.51")
        self.assertEqual(MANIFEST["next_file"],"obt/main/level_st_06-02.txt")
        self.assertEqual((MANIFEST["next_text_ordinal"],MANIFEST["next_text_source_line"]),(113,206))
        t=MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_files"],t["main_story_partial_files"],t["main_story_partial_text_entries"]),(121,1,112))
        self.assertEqual((t["main_story_partial_named_ru_lines"],t["main_story_partial_unnamed_ru_lines"]),(100,12))
        self.assertEqual((t["main_story_selection_files"],t["main_story_selection_text_entries"],t["main_story_selection_vs_historical_manifest_delta"]),(121,9313,1))
        self.assertEqual((t["main_story_chapter_6_files"],t["main_story_chapter_6_partial_files"],t["main_story_chapter_6_partial_text_entries"]),(24,1,112))
        self.assertEqual((t["main_story_partial_decision_option_strings_ru"],t["main_story_partial_decision_option_strings_total"],t["main_story_partial_decision_option_strings_remaining"]),(26,53,27))
        self.assertEqual((t["main_story_partial_decision_commands_ru"],t["main_story_partial_decision_commands_remaining"]),(15,19))
        self.assertEqual((t["main_story_partial_predicate_branches_ru"],t["main_story_partial_predicate_branches_remaining"]),(23,22))
        self.assertEqual(SELECTION["summary"]["complete_files"],121)
        self.assertNotIn("obt/main/level_st_06-02.txt",SELECTION["files"])
        self.assertEqual((QA["completed_story_files"],QA["partial_scene_files"],QA["partial_scene_text_entries"]),(121,1,112))
        self.assertEqual((QA["next_scene"]["translated"],QA["next_scene"]["total"],QA["next_scene"]["next_ordinal"]),(112,269,113))
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])
        self.assertIn("112/269",README)
        self.assertIn("No Light Without Fire",README)
        self.assertIn("v3.46",README)
        self.assertIn("329/329",README)
        self.assertIn("6-17 After Operation",README)
        self.assertIn("Следующая позиция — №301",README)

if __name__ == "__main__":
    unittest.main()
