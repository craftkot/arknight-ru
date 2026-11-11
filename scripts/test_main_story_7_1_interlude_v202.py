# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v202.json")
A = load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v202.json")
Q = load("reports/QA_MAIN_STORY_v202.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v362.json")
S = load("story/story_main_selection_ru_v192.json")
I = (ROOT / "story/CHAPTER_7_INDEX_v202.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

CN_SHA = "1c613bfbf006470b3b8e131b9fcb8b8f53e19ea5"
EN_SHA = "7a204cb0010abcbf60f12017f0b2b4d02eaba156"
EXPECTED_LINES = [13,14,15,16,17,18,19,20,30,31,36,38,39,41,43,45,47,48,49,50,51,52,53,55,56,58,60,61,62,63,64,65,66,68,70,72,74,76,78,80]
EXPECTED_COMMAND_LINES = [1,2,3,4,5,6,7,8,9,10,11,12,21,22,23,24,25,26,27,28,29,32,33,34,35,37,40,42,44,46,54,57,59,67,69,71,73,75,77,79]

class TestMainStory701InterludeV202(unittest.TestCase):
    def test_partial_prefix_and_ordinals(self):
        self.assertEqual(T["version"], "v2.02")
        self.assertEqual(T["status"], "partial_first_draft")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (40, 286, 246, False))
        self.assertEqual((p["named_translated"], p["named_total"], p["unnamed_translated"], p["unnamed_total"]), (32, 215, 8, 71))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 41)))
        self.assertEqual([x["source_line"] for x in rows], EXPECTED_LINES)
        self.assertEqual([x["source_line"] for x in rows if x["kind"] == "unnamed"], EXPECTED_LINES[:8])
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 32)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 8)
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (41, 82))
        self.assertTrue(all(x["text_ru"].strip() for x in rows))
        payload = "\\n".join(x["text_ru"] for x in rows)
        self.assertIsNone(re.search(r"[\\u3400-\\u9fff]", payload))
        self.assertEqual(payload.count("{@nickname}"), 0)
        self.assertEqual({x["speaker_cn"] for x in rows if x["kind"] == "named"}, {"W", "塔露拉"})

    def test_source_alignment_and_command_preservation(self):
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
        self.assertEqual(a["decision_commands"], 0)
        self.assertEqual(a["predicate_branches"], 0)
        self.assertEqual(a["placeholder_count_ru"], 0)
        tr = a["translated_range"]
        self.assertEqual(tr["translated_source_lines"], EXPECTED_LINES)
        self.assertEqual(tr["command_line_numbers"], EXPECTED_COMMAND_LINES)
        self.assertEqual(tr["command_lines_in_range"], 40)
        self.assertEqual(sum(tr["command_counts"].values()), 40)
        self.assertEqual(sum(a["command_counts"].values()), 276)
        self.assertEqual(A["progress"]["translated"], 40)
        self.assertEqual(A["progress"]["remaining"], 246)
        self.assertFalse(A["integrity"]["complete"])

    def test_qa_chronology_and_index(self):
        self.assertEqual(Q["version"], "v2.02")
        self.assertEqual((Q["completed_story_files"], Q["completed_story_text_entries"]), (124, 9962))
        self.assertEqual((Q["partial_scene_files"], Q["partial_scene_named_ru"], Q["partial_scene_unnamed_ru"], Q["partial_scene_text_entries"]), (1, 32, 8, 40))
        self.assertEqual(Q["all_story_text_entries_including_partial"], 10002)
        self.assertEqual(Q["next_scene"]["source_file"], "obt/main/level_st_07-01.txt")
        self.assertEqual((Q["next_scene"]["translated"], Q["next_scene"]["total"], Q["next_scene"]["next_ordinal"], Q["next_scene"]["next_source_line"]), (40, 286, 41, 82))
        self.assertEqual(M["version"], "v3.62")
        self.assertEqual(M["next_file"], "obt/main/level_st_07-01.txt")
        self.assertEqual((M["next_text_ordinal"], M["next_text_source_line"]), (41, 82))
        self.assertIn("level_st_07-01.txt", I)
        self.assertIn("partial_first_draft\\t32\\t8\\t40", I)
        self.assertEqual(S["summary"]["complete_files"], 124)
        self.assertNotIn("obt/main/level_st_07-01.txt", json.dumps(S, ensure_ascii=False))

    def test_readme_corrects_v361_mapping_and_keeps_history(self):
        self.assertIn("v3.62", R)
        self.assertIn("7-1 32:00:00", R)
        self.assertIn("obt/main/level_st_07-01.txt", R)
        self.assertIn("level_main_07-01_beg.txt", R)
        self.assertIn("v3.61", R)
        self.assertIn("220/290", R)
        self.assertIn("№221, CN-строка 440", R)
        self.assertIn("55/290", R)

if __name__ == "__main__":
    unittest.main()
