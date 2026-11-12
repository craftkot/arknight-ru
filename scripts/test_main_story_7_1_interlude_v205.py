# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v205.json")
A = load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v205.json")
Q = load("reports/QA_MAIN_STORY_v205.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v365.json")
I = (ROOT / "story/CHAPTER_7_INDEX_v205.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

CN_SHA = "1c613bfbf006470b3b8e131b9fcb8b8f53e19ea5"
EN_SHA = "7a204cb0010abcbf60f12017f0b2b4d02eaba156"
NEW_LINES = [250,251,256,257,259,260,262,264,267,269,271,272,273,275,277,278,280,281,282,284,286,288,289,290,291,292,293,295,297,298,299,301,302,344,345,346,347,348,349,351]
NEW_COMMAND_LINES = [252,253,254,255,258,261,263,265,266,268,270,274,276,279,283,285,287,294,296,300,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,350]

class TestMainStory701InterludeV205(unittest.TestCase):
    def test_contiguous_prefix_and_new_translation(self):
        self.assertEqual(T["version"], "v2.05")
        self.assertEqual(T["status"], "partial_first_draft")
        p = T["progress"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (160, 286, 126, False))
        self.assertEqual((p["named_translated"], p["named_total"], p["unnamed_translated"], p["unnamed_total"]), (108, 215, 52, 71))
        self.assertEqual([x["ordinal"] for x in T["dialogues"]], list(range(1, 161)))
        self.assertEqual([x["source_line"] for x in T["dialogues"][-40:]], NEW_LINES)
        self.assertEqual(sum(x["kind"] == "named" for x in T["dialogues"]), 108)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in T["dialogues"]), 52)
        self.assertEqual((p["next_ordinal"], p["next_source_line"]), (161, 352))
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        payload = "\n".join(x["text_ru"] for x in T["dialogues"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertEqual(T["decision_options_ru"], [])

    def test_source_hashes_alignment_and_command_preservation(self):
        self.assertEqual(T["source"]["cn_git_blob_sha1"], CN_SHA)
        self.assertEqual(T["source"]["en_git_blob_sha1"], EN_SHA)
        a = T["source_alignment"]
        self.assertEqual((a["cn_text_positions"], a["en_text_positions"]), (286, 286))
        self.assertEqual((a["cn_named_positions"], a["en_named_positions"]), (215, 215))
        self.assertEqual((a["cn_unnamed_positions"], a["en_unnamed_positions"]), (71, 71))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (276, 276))
        self.assertTrue(a["commands_match_cn_en"])
        tr = a["translated_range"]
        self.assertEqual(tr["translated_source_lines"][-40:], NEW_LINES)
        self.assertEqual(tr["command_line_numbers"][-62:], NEW_COMMAND_LINES)
        self.assertEqual(tr["command_lines_in_range"], 191)
        self.assertEqual(sum(tr["command_counts"].values()), 191)
        self.assertEqual((tr["named_positions"], tr["unnamed_positions"]), (108, 52))
        self.assertEqual((tr["decision_commands"], tr["decision_option_strings"], tr["predicate_branches"]), (0, 0, 0))
        self.assertEqual(A["progress"]["translated"], 160)
        self.assertEqual(A["progress"]["remaining"], 126)
        self.assertEqual(A["command_preservation"]["translated_range_command_positions"], 191)
        self.assertEqual(A["command_preservation"]["translated_range_command_numbers"][-62:], NEW_COMMAND_LINES)
        self.assertFalse(A["integrity"]["complete"])

    def test_new_speakers_and_unnamed_narration(self):
        rows = T["dialogues"][-40:]
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 31)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 9)
        self.assertEqual(rows[0]["kind"], "unnamed")
        self.assertEqual(rows[1]["kind"], "unnamed")
        self.assertEqual(rows[8]["kind"], "unnamed")
        self.assertEqual(rows[-7]["kind"], "unnamed")
        self.assertEqual(rows[-2]["kind"], "unnamed")
        self.assertEqual(rows[-1]["speaker_cn"], "塔露拉")
        self.assertEqual(T["dialogues"][-38]["speaker_cn"], "塔露拉")
        self.assertEqual(T["dialogues"][-36]["speaker_cn"], "W")

    def test_qa_chronology_and_index_reconciled(self):
        self.assertEqual(Q["version"], "v2.05")
        self.assertEqual((Q["partial_scene_named_ru"], Q["partial_scene_unnamed_ru"], Q["partial_scene_text_entries"]), (108, 52, 160))
        self.assertEqual(Q["all_story_text_entries_including_partial"], 10122)
        self.assertEqual(Q["chapter_7_partial_text_entries"], 160)
        self.assertEqual((Q["chapter_7_partial_named_ru"], Q["chapter_7_partial_unnamed_ru"]), (108, 52))
        self.assertEqual(Q["chapter_7_text_entries_including_partial"], 160)
        self.assertEqual((Q["chapter_7_named_ru_lines_including_partial"], Q["chapter_7_unnamed_ru_lines_including_partial"]), (108, 52))
        self.assertEqual(Q["partial_scenes"][0]["translated"], 160)
        self.assertEqual(Q["partial_scenes"][0]["next_source_line"], 352)
        self.assertEqual(Q["partial_scene_audit"]["translated"], 160)
        self.assertEqual(Q["partial_scene_audit"]["translated_range_command_lines"], 191)
        self.assertEqual(Q["next_scene"]["translated"], 160)
        self.assertEqual(Q["next_scene"]["next_ordinal"], 161)
        self.assertEqual(Q["next_scene"]["next_source_line"], 352)
        self.assertEqual(M["version"], "v3.65")
        self.assertEqual(M["next_file"], "obt/main/level_st_07-01.txt")
        self.assertEqual((M["next_text_ordinal"], M["next_text_source_line"]), (161, 352))
        self.assertEqual(M["translation_integrity"]["main_story_partial_text_entries"], 160)
        self.assertEqual(M["translation_integrity"]["main_story_chapter_7_text_entries_including_partial"], 160)
        self.assertIn("partial_first_draft\t108\t52\t160", I)

    def test_readme_and_historical_checkpoints(self):
        self.assertIn("v3.65", R)
        self.assertIn("160/286", R)
        self.assertIn("№161, CN-строка 352", R)
        self.assertIn("v3.64", R)
        self.assertIn("120/286", R)
        self.assertIn("№121, CN-строка 250", R)
        self.assertIn("v3.62", R)
        self.assertIn("40/286", R)
        self.assertIn("CN-строка 82", R)
        self.assertIn("reports/QA_MAIN_STORY_v205.json", R)

if __name__ == "__main__":
    unittest.main()
