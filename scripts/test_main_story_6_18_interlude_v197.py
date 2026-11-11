# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_6_stage_6-18_interlude_partial_ru_v197.json")
A = load("reports/MAIN_6-18_INTERLUDE_SOURCE_AUDIT_v197.json")
Q = load("reports/QA_MAIN_STORY_v197.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v357.json")
I = (ROOT / "story/CHAPTER_6_INDEX_v197.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

SOURCE_LINES = [30,31,32,33,37,38,40,41,43,45,47,49,51,53,55,57,58,59,61,63,65,67,69,71,72,73,74,75,77,78,80,82,84,86,88,90,91,92,94,95,104,106,108,109,119,120,123,124,126,127,129,130,131,133,134]
COMMAND_COUNTS = {"HEADER":1,"stopmusic":4,"Dialog":21,"Character":177,"PlayMusic":3,"Blocker":29,"Background":10,"delay":14,"playsound":1,"PlaySound":10,"Decision":2,"Predicate":5,"Delay":1,"Image":5,"ImageTween":1}
RANGE_COMMAND_COUNTS = {"Dialog":3,"Character":30,"delay":4,"Blocker":4,"Background":2,"PlaySound":2,"Decision":1,"Predicate":4}

class TestMainStory618InterludeV197(unittest.TestCase):
    def test_partial_positions_and_speakers(self):
        self.assertEqual(T["version"], "v1.97")
        self.assertEqual(T["status"], "partial_first_draft")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (55, 290, 235, False))
        self.assertEqual((p["named_translated"], p["named_total"], p["unnamed_translated"], p["unnamed_total"]), (51, 285, 4, 5))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 56)))
        self.assertEqual([x["source_line"] for x in rows], SOURCE_LINES)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 51)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 4)
        self.assertEqual([x["source_line"] for x in rows if x["kind"] == "unnamed"], [30, 31, 32, 33])
        self.assertEqual({x["speaker_cn"] for x in rows if x["kind"] == "named"}, {"陈", "诗怀雅", "近卫局成员"})
        self.assertEqual({x["speaker_cn"] for x in rows if x["kind"] == "named" and x["source_line"] >= 119}, {"近卫局成员"})

    def test_decision_predicate_and_payload_integrity(self):
        p = T["progress"]
        self.assertEqual((p["decision_commands_translated"], p["decision_commands_total"], p["decision_commands_remaining"]), (1, 2, 1))
        self.assertEqual((p["decision_option_strings_translated"], p["decision_option_strings_total"], p["decision_option_strings_remaining"]), (3, 4, 1))
        self.assertEqual((p["predicate_branches_translated"], p["predicate_branches_total"], p["predicate_branches_remaining"]), (4, 5, 1))
        self.assertEqual(len(T["decision_options_ru"]), 1)
        d = T["decision_options_ru"][0]
        self.assertEqual((d["source_line"], d["values"], len(d["options_ru"])), (121, ["1", "2", "3"], 3))
        payload = "\n".join(x["text_ru"] for x in T["dialogues"]) + "\n" + "\n".join(y for x in T["decision_options_ru"] for y in x["options_ru"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertNotIn("{@nickname}", payload)
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertTrue(all(y.strip() for x in T["decision_options_ru"] for y in x["options_ru"]))

    def test_source_hashes_and_alignment(self):
        s, a = T["source"], T["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "f0b744c48b2a6592674a42e7c9c3e61cd8c226d8")
        self.assertEqual(s["en_git_blob_sha1"], "9f0a4ae9762665a21262d72ecd2ff09b34544187")
        self.assertEqual((s["cn_physical_lines"], s["en_physical_lines"]), (574, 575))
        self.assertEqual((a["cn_text_positions"], a["en_text_positions"]), (290, 290))
        self.assertEqual((a["cn_named_positions"], a["cn_unnamed_positions"]), (285, 5))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (284, 284))
        self.assertEqual(a["command_counts"], COMMAND_COUNTS)
        self.assertTrue(a["commands_match_cn_en"])
        self.assertTrue(a["text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"])
        self.assertTrue(a["speaker_label_names_match_after_localization"])
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual((a["decision_commands"], a["decision_option_total"], a["predicate_branches"]), (2, 4, 5))
        self.assertEqual((a["placeholder_count_cn"], a["placeholder_count_en"], a["placeholder_count_ru"]), (4, 4, 0))
        r = a["translated_range"]
        self.assertEqual((r["ordinal_start"], r["ordinal_end"], r["command_lines_in_range"]), (1, 55, 50))
        self.assertEqual(r["command_counts"], RANGE_COMMAND_COUNTS)
        self.assertEqual(r["translated_source_lines"], SOURCE_LINES)
        self.assertEqual((r["decision_commands"], r["decision_option_strings"], r["predicate_branches"]), (1, 3, 4))
        self.assertEqual((r["placeholder_count_cn"], r["placeholder_count_en"], r["placeholder_count_ru"]), (0, 0, 0))
        self.assertEqual(A["integrity"]["translated_text_positions"], 55)
        self.assertEqual(A["integrity"]["untranslated_positions"], 235)
        self.assertEqual(A["integrity"]["untranslated_cjk_in_ru"], 0)
        self.assertFalse(A["integrity"]["complete"])

    def test_index_qa_and_manifest(self):
        self.assertEqual(Q["version"], "v1.97")
        self.assertEqual((Q["completed_story_files"], Q["partial_scene_files"]), (123, 1))
        self.assertEqual((Q["partial_scene_named_ru"], Q["partial_scene_unnamed_ru"], Q["partial_scene_text_entries"]), (51, 4, 55))
        self.assertEqual((Q["completed_story_text_entries"], Q["all_story_text_entries_including_partial"]), (9672, 9727))
        self.assertEqual((Q["chapter_6_complete_files"], Q["chapter_6_partial_files"]), (26, 1))
        self.assertEqual((Q["chapter_6_partial_named_ru"], Q["chapter_6_partial_unnamed_ru"], Q["chapter_6_partial_text_entries"]), (51, 4, 55))
        self.assertEqual((Q["chapter_6_text_entries_including_partial"], Q["chapter_6_named_ru_lines_including_partial"], Q["chapter_6_unnamed_ru_lines_including_partial"]), (3482, 3363, 119))
        self.assertEqual((Q["selection_files"], Q["selection_dialogue_entries_counted"], Q["selection_vs_historical_manifest_delta"]), (123, 9671, 1))
        self.assertEqual((Q["main_story_partial_decision_commands_ru"], Q["main_story_partial_decision_option_strings_ru"], Q["main_story_partial_predicate_branches_ru"]), (1, 3, 4))
        row = [x for x in I.splitlines() if x.startswith("level_st_06-03.txt\t")]
        self.assertEqual(len(row), 1)
        self.assertIn("partial_first_draft\t51\t4\t55\tf0b744c48b2a6592674a42e7c9c3e61cd8c226d8\t9f0a4ae9762665a21262d72ecd2ff09b34544187", row[0])
        self.assertEqual(M["version"], "v3.57")
        self.assertEqual(M["next_file"], "obt/main/level_st_06-03.txt")
        self.assertEqual((M["next_text_ordinal"], M["next_text_source_line"]), (56, 143))
        self.assertEqual(M["next_source"]["translated_positions"], 55)
        self.assertEqual(M["next_source"]["remaining_positions"], 235)
        self.assertEqual(Q["next_scene"]["source_file"], "obt/main/level_st_06-03.txt")
        self.assertEqual((Q["next_scene"]["next_ordinal"], Q["next_scene"]["next_source_line"]), (56, 143))
        self.assertIn("6-18 Only You Know", R)
        self.assertIn("55/290", R)
        self.assertFalse(Q["editorial_review"])
        self.assertFalse(Q["in_game_test"])

    def test_source_scripts_are_not_committed(self):
        self.assertEqual(T["source_file"], "obt/main/level_st_06-03.txt")
        self.assertEqual(T["progress"]["remaining"], 235)
        self.assertNotIn("source_script_cn", T)
        self.assertNotIn("source_script_en", T)
        self.assertIn("No complete CN or EN source script is included", T["notes_v197"][-1])

if __name__ == "__main__":
    unittest.main()
