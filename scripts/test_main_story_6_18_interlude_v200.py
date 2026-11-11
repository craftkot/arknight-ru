# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_6_stage_6-18_interlude_partial_ru_v200.json")
OLD = load("story/story_chapter_6_stage_6-18_interlude_partial_ru_v199.json")
A = load("reports/MAIN_6-18_INTERLUDE_SOURCE_AUDIT_v200.json")
Q = load("reports/QA_MAIN_STORY_v200.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v360.json")
I = (ROOT / "story/CHAPTER_6_INDEX_v200.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

NEW_LINES = [363,365,366,368,370,371,372,373,375,377,378,379,381,383,385,387,388,389,391,393,394,395,396,397,398,400,402,403,404,406,408,409,417,419,421,423,424,425,426,427,428,429,430,431,432,433,434,435,437,438]
NEW_COMMAND_LINES = [362,364,367,369,374,376,380,382,384,386,390,392,399,401,405,407,410,411,412,413,414,415,416,418,420,422,436]
NEW_COMMAND_COUNTS = {"Character":22,"Dialog":1,"PlaySound":2,"delay":2}

class TestMainStory618InterludeV200(unittest.TestCase):
    def test_positions_and_append_only_integrity(self):
        self.assertEqual(T["version"], "v2.00")
        self.assertEqual(T["status"], "partial_first_draft")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (220,290,70,False))
        self.assertEqual((p["named_translated"],p["named_total"],p["unnamed_translated"],p["unnamed_total"]), (215,285,5,5))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1,221)))
        self.assertEqual(rows[:170], OLD["dialogues"])
        self.assertEqual([x["source_line"] for x in rows[170:]], NEW_LINES)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 215)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 5)
        self.assertTrue(all(x["kind"] == "named" for x in rows[170:]))
        self.assertEqual({x["speaker_cn"] for x in rows[170:]}, {"魏彦吾","阿米娅","陈"})
        self.assertEqual(rows[199]["text_ru"], "Мисс Амия, вы умеете играть в го?")
        self.assertIn("игровыми фигурами", rows[198]["text_ru"])
        self.assertIn("чёрными или белыми", rows[201]["text_ru"])

    def test_commands_decisions_predicates_and_placeholders(self):
        p = T["progress"]
        self.assertEqual((p["decision_commands_translated"],p["decision_commands_total"],p["decision_commands_remaining"]), (2,2,0))
        self.assertEqual((p["decision_option_strings_translated"],p["decision_option_strings_total"],p["decision_option_strings_remaining"]), (4,4,0))
        self.assertEqual((p["predicate_branches_translated"],p["predicate_branches_total"],p["predicate_branches_remaining"]), (5,5,0))
        payload = "\n".join(x["text_ru"] for x in T["dialogues"]) + "\n" + "\n".join(y for x in T["decision_options_ru"] for y in x["options_ru"])
        self.assertEqual(payload.count("{@nickname}"), 4)
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertTrue(all(y.strip() for x in T["decision_options_ru"] for y in x["options_ru"]))

    def test_source_alignment_and_new_segment_audit(self):
        s, a = T["source"], T["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "f0b744c48b2a6592674a42e7c9c3e61cd8c226d8")
        self.assertEqual(s["en_git_blob_sha1"], "9f0a4ae9762665a21262d72ecd2ff09b34544187")
        self.assertEqual((a["cn_text_positions"],a["en_text_positions"]), (290,290))
        self.assertEqual((a["cn_named_positions"],a["cn_unnamed_positions"]), (285,5))
        self.assertEqual((a["command_lines_cn"],a["command_lines_en"]), (284,284))
        self.assertTrue(a["commands_match_cn_en"] and a["text_line_numbers_match"])
        self.assertEqual(a["translated_range"]["ordinal_end"], 220)
        self.assertEqual(a["translated_range"]["command_lines"], 184)
        self.assertEqual(A["new_segment"]["ordinal_start"], 171)
        self.assertEqual(A["new_segment"]["ordinal_end"], 220)
        self.assertEqual(A["new_segment"]["translated_source_lines"], NEW_LINES)
        self.assertEqual(A["new_segment"]["command_line_numbers"], NEW_COMMAND_LINES)
        self.assertEqual(A["new_segment"]["command_counts"], NEW_COMMAND_COUNTS)
        self.assertEqual((A["new_segment"]["text_positions"],A["new_segment"]["named_positions"],A["new_segment"]["unnamed_positions"]), (50,50,0))
        self.assertEqual((A["new_segment"]["command_lines"],len(NEW_COMMAND_LINES)), (27,27))
        self.assertEqual(A["translated_range"]["translated_source_lines"], [x["source_line"] for x in T["dialogues"]])
        self.assertEqual(A["translated_range"]["command_lines"], 184)
        self.assertEqual(A["progress"]["next_ordinal"], 221)
        self.assertEqual(A["progress"]["next_source_line"], 440)
        self.assertEqual((A["integrity"]["translated_text_positions"],A["integrity"]["untranslated_positions"]), (220,70))
        self.assertFalse(A["integrity"]["complete"])
        self.assertTrue(any("围棋" in x["note"] and "chess" in x["note"] for x in A["version_differences"] if isinstance(x,dict)))

    def test_qa_index_readme_and_chronology(self):
        self.assertEqual(Q["version"], "v2.00")
        self.assertEqual((Q["partial_scene_named_ru"],Q["partial_scene_unnamed_ru"],Q["partial_scene_text_entries"]), (215,5,220))
        self.assertEqual(Q["all_story_text_entries_including_partial"], 9892)
        self.assertEqual((Q["chapter_6_partial_named_ru"],Q["chapter_6_partial_unnamed_ru"],Q["chapter_6_partial_text_entries"]), (215,5,220))
        self.assertEqual(Q["chapter_6_text_entries_including_partial"], 3647)
        self.assertEqual(Q["chapter_6_named_ru_lines_including_partial"], 3527)
        self.assertEqual(Q["next_scene"]["next_ordinal"], 221)
        self.assertEqual(Q["next_scene"]["next_source_line"], 440)
        self.assertEqual(Q["partial_scene_audit"]["translated_source_lines"], [x["source_line"] for x in T["dialogues"]])
        row = [x for x in I.splitlines() if x.startswith("level_st_06-03.txt\t")]
        self.assertEqual(len(row), 1)
        self.assertIn("partial_first_draft\t215\t5\t220\tf0b744c48b2a6592674a42e7c9c3e61cd8c226d8\t9f0a4ae9762665a21262d72ecd2ff09b34544187", row[0])
        self.assertEqual(M["version"], "v3.60")
        self.assertEqual((M["next_text_ordinal"],M["next_text_source_line"]), (221,440))
        self.assertEqual((M["next_source"]["translated_positions"],M["next_source"]["remaining_positions"]), (220,70))
        self.assertIn("220/290", R)
        self.assertIn("№221, CN-строка 440", R)
        self.assertIn("170/290", R)
        self.assertIn("№171, CN-строка 357", R)
        self.assertIn("113/290", R)
        self.assertFalse(Q["editorial_review"] or Q["in_game_test"])

    def test_source_scripts_not_committed(self):
        self.assertEqual(T["source_file"], "obt/main/level_st_06-03.txt")
        self.assertNotIn("source_script_cn", T)
        self.assertNotIn("source_script_en", T)
        self.assertIn("No complete CN or EN source script is included", T["notes_v200"][-1])

if __name__ == "__main__":
    unittest.main()
