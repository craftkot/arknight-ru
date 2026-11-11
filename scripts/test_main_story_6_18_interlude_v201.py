# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_6_stage_6-18_interlude_ru_v201.json")
OLD = load("story/story_chapter_6_stage_6-18_interlude_partial_ru_v200.json")
A = load("reports/MAIN_6-18_INTERLUDE_SOURCE_AUDIT_v201.json")
Q = load("reports/QA_MAIN_STORY_v201.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v361.json")
S = load("story/story_main_selection_ru_v192.json")
I = (ROOT / "story/CHAPTER_6_INDEX_v201.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

RESTORED_LINES = [357,358,359,360,361]
FINAL_LINES = [440,441,443,445,447,449,451,453,455,457,459,461,463,464,465,467,468,470,472,474,475,476,477,479,481,482,484,486,487,488,489,490,492,493,494,496,497,504,506,508,510,512,514,520,522,524,525,526,528,530,532,533,540,541,542,544,545,547,553,555,557,559,560,561,562]
CN7_SHA = "93513ec7727a1646cf7248aac31363358bf70cc0"
EN7_SHA = "b4ab1d3e7baf5d40575790cbecdf5e46f35bc06a"

class TestMainStory618InterludeV201(unittest.TestCase):
    def test_full_positions_and_v200_gap_correction(self):
        self.assertEqual(T["version"], "v2.01")
        self.assertEqual(T["status"], "first_draft_complete")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (290,290,0,True))
        self.assertEqual((p["named_translated"],p["named_total"],p["unnamed_translated"],p["unnamed_total"]), (285,285,5,5))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1,291)))
        self.assertEqual(rows[:170], OLD["dialogues"][:170])
        self.assertEqual([x["source_line"] for x in rows[170:175]], RESTORED_LINES)
        self.assertTrue(all(x["speaker_cn"] == "阿米娅" for x in rows[170:175]))
        self.assertEqual([x["source_line"] for x in rows[175:225]], [x["source_line"] for x in OLD["dialogues"][170:]])
        self.assertEqual([x["ordinal"] for x in rows[175:225]], list(range(176,226)))
        self.assertEqual([x["text_ru"] for x in rows[175:225]], [x["text_ru"] for x in OLD["dialogues"][170:]])
        self.assertEqual([x["source_line"] for x in rows[225:]], FINAL_LINES)
        self.assertEqual([x["ordinal"] for x in rows[225:]], list(range(226,291)))
        self.assertEqual([x["source_line"] for x in rows], sorted(x["source_line"] for x in rows))
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 285)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 5)
        self.assertEqual([x["source_line"] for x in rows if x["kind"] == "unnamed"], [30,31,32,33,253])

    def test_commands_decisions_predicates_and_placeholders(self):
        p = T["progress"]
        self.assertEqual((p["decision_commands_translated"],p["decision_commands_total"],p["decision_commands_remaining"]), (2,2,0))
        self.assertEqual((p["decision_option_strings_translated"],p["decision_option_strings_total"],p["decision_option_strings_remaining"]), (4,4,0))
        self.assertEqual((p["predicate_branches_translated"],p["predicate_branches_total"],p["predicate_branches_remaining"]), (5,5,0))
        self.assertEqual(T["source_alignment"]["command_lines_cn"], 284)
        self.assertEqual(T["source_alignment"]["command_lines_en"], 284)
        self.assertEqual(T["source_alignment"]["translated_range"]["command_lines"], 284)
        self.assertEqual(sum(T["source_alignment"]["translated_range"]["command_counts"].values()), 284)
        self.assertEqual(len(T["source_alignment"]["translated_range"]["command_line_numbers"]), 284)
        self.assertEqual(T["source_alignment"]["placeholder_count_ru"], 4)
        payload = "\n".join(x["text_ru"] for x in T["dialogues"]) + "\n" + "\n".join(y for x in T["decision_options_ru"] for y in x["options_ru"])
        self.assertEqual(payload.count("{@nickname}"), 4)
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertTrue(all(y.strip() for x in T["decision_options_ru"] for y in x["options_ru"]))

    def test_source_audit_and_integrity(self):
        self.assertEqual(T["source"]["cn_git_blob_sha1"], "f0b744c48b2a6592674a42e7c9c3e61cd8c226d8")
        self.assertEqual(T["source"]["en_git_blob_sha1"], "9f0a4ae9762665a21262d72ecd2ff09b34544187")
        self.assertEqual((T["source_alignment"]["cn_text_positions"],T["source_alignment"]["en_text_positions"]), (290,290))
        self.assertEqual((T["source_alignment"]["cn_named_positions"],T["source_alignment"]["cn_unnamed_positions"]), (285,5))
        self.assertEqual(A["progress"]["translated"], 290)
        self.assertEqual(A["progress"]["remaining"], 0)
        self.assertTrue(A["progress"]["complete"])
        self.assertTrue(A["integrity"]["complete"])
        self.assertEqual(A["integrity"]["untranslated_positions"], 0)
        self.assertEqual(A["translated_range"]["translated_source_lines"], [x["source_line"] for x in T["dialogues"]])
        self.assertEqual(A["new_segment"]["corrective_gap_segment"]["text_positions"], 5)
        self.assertEqual(A["new_segment"]["reindexed_v200_segment"]["ordinal_start"], 176)
        self.assertEqual(A["new_segment"]["final_segment"]["ordinal_start"], 226)
        self.assertTrue(any("omitted" in x["note"] and "357–361" in x["note"] for x in A["version_differences"]))

    def test_selection_index_qa_and_manifest(self):
        self.assertEqual(S["version"], "v1.92")
        self.assertEqual(S["summary"], {"complete_files":124,"total_dialogue_entries_counted":9961,"historical_manifest_entries":9962,"inherited_delta":1})
        entry = S["files"]["obt/main/level_st_06-03.txt"]
        self.assertEqual(entry["dialogue_count"], 290)
        self.assertEqual(len(entry["dialogues"]), 290)
        self.assertEqual(entry["dialogues"]["290"], T["dialogues"][-1]["text_ru"])
        self.assertEqual(Q["version"], "v2.01")
        self.assertEqual((Q["completed_story_files"],Q["completed_story_named_ru"],Q["completed_story_unnamed_ru"],Q["completed_story_text_entries"]), (124,9800,162,9962))
        self.assertEqual((Q["selection_files"],Q["selection_dialogue_entries_counted"],Q["selection_vs_historical_manifest_delta"]), (124,9961,1))
        self.assertEqual((Q["partial_scene_files"],Q["partial_scene_text_entries"],Q["all_story_text_entries_including_partial"]), (0,0,9962))
        self.assertEqual((Q["chapter_6_complete_files"],Q["chapter_6_complete_named_ru"],Q["chapter_6_complete_unnamed_ru"],Q["chapter_6_complete_text_entries"]), (27,3597,120,3717))
        self.assertEqual((Q["chapter_6_partial_files"],Q["chapter_6_partial_text_entries"]), (0,0))
        self.assertIsNone(Q["partial_scene_audit"])
        row = [x for x in I.splitlines() if x.startswith("level_st_06-03.txt\t")]
        self.assertEqual(len(row),1)
        self.assertIn("first_draft_complete\t285\t5\t290",row[0])
        self.assertEqual(M["version"],"v3.61")
        self.assertEqual(M["next_file"],"obt/main/level_main_07-01_beg.txt")
        self.assertEqual((M["next_text_ordinal"],M["next_text_source_line"]),(1,9))
        self.assertEqual(M["next_source"]["cn_git_blob_sha1"],CN7_SHA)
        self.assertEqual(M["next_source"]["en_git_blob_sha1"],EN7_SHA)
        self.assertEqual((M["next_source"]["text_positions"],M["next_source"]["named_positions"],M["next_source"]["unnamed_positions"]),(87,85,2))
        self.assertEqual((M["next_source"]["command_lines_cn"],M["next_source"]["command_lines_en"]),(104,103))
        self.assertIn("Predicate command at line 71",M["next_source"]["version_difference"])
        self.assertEqual((Q["next_scene"]["next_ordinal"],Q["next_scene"]["next_source_line"]),(1,9))
        self.assertEqual(Q["next_scene"]["source_file"],"obt/main/level_main_07-01_beg.txt")

    def test_readme_checkpoints_and_quality_caveats(self):
        self.assertIn("v3.61",R)
        self.assertIn("124 полных первых черновика",R)
        self.assertIn("290/290",R)
        self.assertIn("7-1 32:00:00",R)
        self.assertIn("220/290",R)
        self.assertIn("№221, CN-строка 440",R)
        self.assertIn("170/290",R)
        self.assertIn("№171, CN-строка 357",R)
        self.assertIn("113/290",R)
        self.assertIn("№114, CN-строка 231",R)
        self.assertIn("55/290",R)
        self.assertFalse(Q["editorial_review"] or Q["in_game_test"])
        self.assertNotIn("source_script_cn",T)
        self.assertNotIn("source_script_en",T)

if __name__ == "__main__":
    unittest.main()
