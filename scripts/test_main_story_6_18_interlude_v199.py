# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_6_stage_6-18_interlude_partial_ru_v199.json")
A = load("reports/MAIN_6-18_INTERLUDE_SOURCE_AUDIT_v199.json")
Q = load("reports/QA_MAIN_STORY_v199.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v359.json")
I = (ROOT / "story/CHAPTER_6_INDEX_v199.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

SOURCE_LINES = [30,31,32,33,37,38,40,41,43,45,47,49,51,53,55,57,58,59,61,63,65,67,69,71,72,73,74,75,77,78,80,82,84,86,88,90,91,92,94,95,104,106,108,109,119,120,123,124,126,127,129,130,131,133,134,143,144,145,146,147,149,151,152,154,155,157,158,160,162,164,166,167,169,171,173,175,177,178,179,181,183,185,186,187,188,189,190,191,192,193,194,196,198,199,200,202,204,206,208,209,210,211,213,214,216,217,218,220,222,223,225,227,229,231,232,233,235,236,238,240,241,242,244,245,246,253,255,257,258,260,269,271,277,279,281,283,285,288,290,292,294,296,298,299,301,303,304,312,313,315,321,326,327,329,330,332,333,334,336,337,338,340,342,344,346,348,350,352,354,356]
NEW_LINES = [231,232,233,235,236,238,240,241,242,244,245,246,253,255,257,258,260,269,271,277,279,281,283,285,288,290,292,294,296,298,299,301,303,304,312,313,315,321,326,327,329,330,332,333,334,336,337,338,340,342,344,346,348,350,352,354,356]
COMMAND_LINES = [34,35,36,39,42,44,46,48,50,52,54,56,60,62,64,66,68,70,76,79,81,83,85,87,89,93,96,97,98,99,100,101,102,103,105,107,110,111,112,113,114,115,116,117,118,121,122,125,128,132,135,136,137,138,139,140,141,142,148,150,153,156,159,161,163,165,168,170,172,174,176,180,182,184,195,197,201,203,205,207,212,215,219,221,224,226,228,230,234,237,239,243,247,248,249,250,251,252,254,256,259,261,262,263,264,265,266,267,268,270,272,273,274,275,276,278,280,282,284,286,287,289,291,293,295,297,300,302,305,306,307,308,309,310,311,314,316,317,318,319,320,322,323,324,325,328,331,335,339,341,343,345,347,349,351,353,355]
NEW_COMMAND_LINES = [230,234,237,239,243,247,248,249,250,251,252,254,256,259,261,262,263,264,265,266,267,268,270,272,273,274,275,276,278,280,282,284,286,287,289,291,293,295,297,300,302,305,306,307,308,309,310,311,314,316,317,318,319,320,322,323,324,325,328,331,335,339,341,343,345,347,349,351,353,355]
COMMAND_COUNTS = {"Dialog":10,"Character":106,"delay":6,"Blocker":14,"Background":5,"PlaySound":6,"Decision":2,"Predicate":5,"stopmusic":1,"PlayMusic":1,"Delay":1}

class TestMainStory618InterludeV199(unittest.TestCase):
    def test_positions_speakers_and_progress(self):
        self.assertEqual(T["version"], "v1.99")
        self.assertEqual(T["status"], "partial_first_draft")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (170, 290, 120, False))
        self.assertEqual((p["named_translated"], p["named_total"], p["unnamed_translated"], p["unnamed_total"]), (165, 285, 5, 5))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 171)))
        self.assertEqual([x["source_line"] for x in rows], SOURCE_LINES)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 165)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 5)
        self.assertEqual([x["source_line"] for x in rows if x["kind"] == "unnamed"], [30, 31, 32, 33, 253])
        self.assertEqual([x["source_line"] for x in rows if x["ordinal"] >= 114], NEW_LINES)
        self.assertEqual(rows[125]["kind"], "unnamed")
        self.assertEqual(rows[125]["text_ru"], "Лунмэнь, Верхний город — канцелярия главы администрации")
        self.assertEqual({x["speaker_cn"] for x in rows if x["ordinal"] >= 114 and x["kind"] == "named"},
                         {"煌", "灰喉", "阿米娅", "接待员", "太合", "苍老的男声", "？？？", "监察司", "魏彦吾"})

    def test_decision_predicate_placeholders_and_text_integrity(self):
        p = T["progress"]
        self.assertEqual((p["decision_commands_translated"], p["decision_commands_total"], p["decision_commands_remaining"]), (2, 2, 0))
        self.assertEqual((p["decision_option_strings_translated"], p["decision_option_strings_total"], p["decision_option_strings_remaining"]), (4, 4, 0))
        self.assertEqual((p["predicate_branches_translated"], p["predicate_branches_total"], p["predicate_branches_remaining"]), (5, 5, 0))
        payload = "\n".join(x["text_ru"] for x in T["dialogues"]) + "\n" + "\n".join(y for x in T["decision_options_ru"] for y in x["options_ru"])
        self.assertEqual(payload.count("{@nickname}"), 4)
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertTrue(all(y.strip() for x in T["decision_options_ru"] for y in x["options_ru"]))

    def test_source_alignment_and_command_preservation(self):
        s, a = T["source"], T["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "f0b744c48b2a6592674a42e7c9c3e61cd8c226d8")
        self.assertEqual(s["en_git_blob_sha1"], "9f0a4ae9762665a21262d72ecd2ff09b34544187")
        self.assertEqual((a["cn_text_positions"], a["en_text_positions"]), (290, 290))
        self.assertEqual((a["cn_named_positions"], a["cn_unnamed_positions"]), (285, 5))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (284, 284))
        self.assertTrue(a["commands_match_cn_en"] and a["text_line_numbers_match"])
        self.assertTrue(a["command_line_numbers_match"] and a["command_names_and_parameters_match_after_decision_option_normalization"])
        r = A["translated_range"]
        self.assertEqual((r["ordinal_start"], r["ordinal_end"]), (1, 170))
        self.assertEqual(r["translated_source_lines"], SOURCE_LINES)
        self.assertEqual(r["command_line_numbers"], COMMAND_LINES)
        self.assertEqual(r["command_counts"], COMMAND_COUNTS)
        self.assertEqual(r["command_lines"], len(COMMAND_LINES))
        self.assertEqual(A["new_segment"]["translated_source_lines"], NEW_LINES)
        self.assertEqual(A["new_segment"]["command_line_numbers"], NEW_COMMAND_LINES)
        self.assertEqual(A["new_segment"]["text_positions"], 57)
        self.assertEqual(A["new_segment"]["named_positions"], 56)
        self.assertEqual(A["new_segment"]["unnamed_positions"], 1)
        self.assertEqual(A["progress"]["next_ordinal"], 171)
        self.assertEqual(A["progress"]["next_source_line"], 357)
        self.assertEqual((A["integrity"]["translated_text_positions"], A["integrity"]["untranslated_positions"]), (170, 120))
        self.assertEqual(A["integrity"]["untranslated_cjk_in_ru"], 0)
        self.assertFalse(A["integrity"]["complete"])

    def test_qa_index_readme_and_chronology(self):
        self.assertEqual(Q["version"], "v1.99")
        self.assertEqual((Q["completed_story_files"], Q["partial_scene_files"]), (123, 1))
        self.assertEqual((Q["partial_scene_named_ru"], Q["partial_scene_unnamed_ru"], Q["partial_scene_text_entries"]), (165, 5, 170))
        self.assertEqual((Q["completed_story_text_entries"], Q["all_story_text_entries_including_partial"]), (9672, 9842))
        self.assertEqual((Q["chapter_6_complete_files"], Q["chapter_6_partial_files"]), (26, 1))
        self.assertEqual((Q["chapter_6_partial_named_ru"], Q["chapter_6_partial_unnamed_ru"], Q["chapter_6_partial_text_entries"]), (165, 5, 170))
        self.assertEqual((Q["chapter_6_text_entries_including_partial"], Q["chapter_6_named_ru_lines_including_partial"], Q["chapter_6_unnamed_ru_lines_including_partial"]), (3597, 3477, 120))
        row = [x for x in I.splitlines() if x.startswith("level_st_06-03.txt\t")]
        self.assertEqual(len(row), 1)
        self.assertIn("partial_first_draft\t165\t5\t170\tf0b744c48b2a6592674a42e7c9c3e61cd8c226d8\t9f0a4ae9762665a21262d72ecd2ff09b34544187", row[0])
        self.assertEqual(M["version"], "v3.59")
        self.assertEqual(M["next_file"], "obt/main/level_st_06-03.txt")
        self.assertEqual((M["next_text_ordinal"], M["next_text_source_line"]), (171, 357))
        self.assertEqual((M["next_source"]["translated_positions"], M["next_source"]["remaining_positions"]), (170, 120))
        self.assertEqual((M["next_source"]["translated_named_positions"], M["next_source"]["translated_unnamed_positions"]), (165, 5))
        self.assertIn("170/290", R)
        self.assertIn("№171, CN-строка 357", R)
        self.assertIn("113/290", R)
        self.assertIn("№114, CN-строка 231", R)
        self.assertFalse(Q["editorial_review"] or Q["in_game_test"])

    def test_source_scripts_are_not_committed(self):
        self.assertEqual(T["source_file"], "obt/main/level_st_06-03.txt")
        self.assertEqual(T["progress"]["remaining"], 120)
        self.assertNotIn("source_script_cn", T)
        self.assertNotIn("source_script_en", T)
        self.assertIn("No complete CN or EN source script is included", T["notes_v199"][-1])

if __name__ == "__main__":
    unittest.main()
