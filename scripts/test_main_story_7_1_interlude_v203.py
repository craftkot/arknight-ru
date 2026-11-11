# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v203.json")
A = load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v203.json")
Q = load("reports/QA_MAIN_STORY_v203.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v363.json")
I = (ROOT / "story/CHAPTER_7_INDEX_v203.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
CN_SHA = "1c613bfbf006470b3b8e131b9fcb8b8f53e19ea5"
EN_SHA = "7a204cb0010abcbf60f12017f0b2b4d02eaba156"
EXPECTED_LINES = [13,14,15,16,17,18,19,20,30,31,36,38,39,41,43,45,47,48,49,50,51,52,53,55,56,58,60,61,62,63,64,65,66,68,70,72,74,76,78,80,81,83,84,86,88,90,92,94,96,97,98,99,100,102,104,105,107,109,110,112,113,115,116,117,119,121,125,126,127,128,129,130,131,132,133,134,135,139,143,149]
EXPECTED_COMMAND_LINES = [1,2,3,4,5,6,7,8,9,10,11,12,21,22,23,24,25,26,27,28,29,32,33,34,35,37,40,42,44,46,54,57,59,67,69,71,73,75,77,79,82,85,87,89,91,93,95,101,103,106,108,111,114,118,120,122,123,124,136,137,138,140,141,142,144,145,146,147,148]

class TestMainStory701InterludeV203(unittest.TestCase):
    def test_contiguous_prefix_and_text_positions(self):
        self.assertEqual(T["version"], "v2.03")
        self.assertEqual(T["status"], "partial_first_draft")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (80, 286, 206, False))
        self.assertEqual((p["named_translated"], p["named_total"], p["unnamed_translated"], p["unnamed_total"]), (59, 215, 21, 71))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 81)))
        self.assertEqual([x["source_line"] for x in rows], EXPECTED_LINES)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 59)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 21)
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (81, 150))
        self.assertEqual(len({x["source_line"] for x in rows}), 80)
        self.assertTrue(all(x["text_ru"].strip() for x in rows))
        payload = "\n".join(x["text_ru"] for x in rows)
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertEqual(payload.count("{@nickname}"), 0)
        self.assertEqual(T["decision_options_ru"], [])

    def test_source_alignment_and_commands(self):
        a = T["source_alignment"]
        self.assertEqual(T["source"]["cn_git_blob_sha1"], CN_SHA)
        self.assertEqual(T["source"]["en_git_blob_sha1"], EN_SHA)
        self.assertEqual((a["cn_text_positions"], a["en_text_positions"]), (286, 286))
        self.assertEqual((a["cn_named_positions"], a["en_named_positions"]), (215, 215))
        self.assertEqual((a["cn_unnamed_positions"], a["en_unnamed_positions"]), (71, 71))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (276, 276))
        self.assertTrue(a["commands_match_cn_en"])
        self.assertTrue(a["text_line_numbers_match"])
        self.assertTrue(a["command_line_numbers_match"])
        tr = a["translated_range"]
        self.assertEqual(tr["translated_source_lines"], EXPECTED_LINES)
        self.assertEqual(tr["command_line_numbers"], EXPECTED_COMMAND_LINES)
        self.assertEqual(tr["command_lines_in_range"], 69)
        self.assertEqual(sum(tr["command_counts"].values()), 69)
        self.assertEqual(A["progress"]["translated"], 80)
        self.assertEqual(A["progress"]["remaining"], 206)
        self.assertEqual(A["command_preservation"]["translated_range_command_positions"], 69)
        self.assertEqual(sum(A["command_preservation"]["translated_range_command_counts"].values()), 69)
        self.assertFalse(A["integrity"]["complete"])

    def test_cn_primary_lexical_differences(self):
        diffs = T["source_alignment"]["version_differences"]
        self.assertEqual([x["source_line"] for x in diffs], [105, 143])
        self.assertEqual(diffs[0]["cn"], "侯爵")
        self.assertEqual(diffs[0]["resolution_ru"], "маркиз Борис")
        self.assertEqual(diffs[1]["cn"], "伊比利亚修士")
        self.assertEqual(diffs[1]["resolution_ru"], "монах из Иберии")
        self.assertIn("侯爵", "\n".join(A["editorial_flags"]))
        self.assertIn("修士", "\n".join(A["editorial_flags"]))

    def test_qa_chronology_index(self):
        self.assertEqual(Q["version"], "v2.03")
        self.assertEqual((Q["completed_story_files"], Q["completed_story_text_entries"]), (124, 9962))
        self.assertEqual((Q["partial_scene_files"], Q["partial_scene_named_ru"], Q["partial_scene_unnamed_ru"], Q["partial_scene_text_entries"]), (1, 59, 21, 80))
        self.assertEqual(Q["all_story_text_entries_including_partial"], 10042)
        self.assertEqual(Q["selection_files"], 124)
        self.assertEqual(Q["selection_dialogue_entries_counted"], 9961)
        self.assertEqual((Q["next_scene"]["translated"], Q["next_scene"]["total"], Q["next_scene"]["next_ordinal"], Q["next_scene"]["next_source_line"]), (80, 286, 81, 150))
        self.assertEqual(M["version"], "v3.63")
        self.assertEqual(M["next_file"], "obt/main/level_st_07-01.txt")
        self.assertEqual((M["next_text_ordinal"], M["next_text_source_line"]), (81, 150))
        self.assertIn("partial_first_draft\t59\t21\t80", I)

    def test_readme_and_glossary_current_status(self):
        self.assertIn("v3.63", R)
        self.assertIn("80/286", R)
        self.assertIn("№81, CN-строка 150", R)
        self.assertIn("v3.62", R)
        self.assertIn("40/286", R)
        self.assertIn("CN-строка 82", R)
        self.assertIn("маркиз", TERMS)
        self.assertIn("монах из Иберии", TERMS)
        self.assertIn("городская платформа", TERMS)
        self.assertIn("разрушенный город", TERMS)

if __name__ == "__main__":
    unittest.main()
