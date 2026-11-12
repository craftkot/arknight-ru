# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v206.json")
A = load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v206.json")
Q = load("reports/QA_MAIN_STORY_v206.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v366.json")
I = (ROOT / "story/CHAPTER_7_INDEX_v206.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

CN_SHA = "1c613bfbf006470b3b8e131b9fcb8b8f53e19ea5"
EN_SHA = "7a204cb0010abcbf60f12017f0b2b4d02eaba156"
NEW_LINES = [352,354,357,358,359,360,361,362,363,364,365,366,367,368,369,374,375,377,378,379,381,383,384,386,388,389,391,392,394,396,397,402,403,404,405,406,414,415,416,417]
NEW_COMMAND_LINES = [353,355,356,370,371,372,373,376,380,382,385,387,390,393,395,398,399,400,401,407,408,409,410,411,412,413]
EXPECTED_DIFFERENCE_LINES = [105,143,176,228,363,378,384,406]

class TestMainStory701InterludeV206(unittest.TestCase):
    def test_contiguous_prefix_and_translation(self):
        self.assertEqual(T["version"], "v2.06")
        self.assertEqual(T["status"], "partial_first_draft")
        p = T["progress"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (200,286,86,False))
        self.assertEqual((p["named_translated"],p["named_total"],p["unnamed_translated"],p["unnamed_total"]),(130,215,70,71))
        self.assertEqual([x["ordinal"] for x in T["dialogues"]],list(range(1,201)))
        self.assertEqual([x["source_line"] for x in T["dialogues"][-40:]],NEW_LINES)
        self.assertEqual(sum(x["kind"]=="named" for x in T["dialogues"]),130)
        self.assertEqual(sum(x["kind"]=="unnamed" for x in T["dialogues"]),70)
        self.assertEqual((p["next_ordinal"],p["next_source_line"]),(201,418))
        payload="\n".join(x["text_ru"] for x in T["dialogues"])
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertIsNone(re.search(r"[\u3400-\u9fff]",payload))
        self.assertEqual(T["decision_options_ru"],[])

    def test_source_and_commands(self):
        self.assertEqual(T["source"]["cn_git_blob_sha1"],CN_SHA)
        self.assertEqual(T["source"]["en_git_blob_sha1"],EN_SHA)
        a=T["source_alignment"]
        self.assertEqual((a["cn_text_positions"],a["en_text_positions"]),(286,286))
        self.assertEqual((a["cn_named_positions"],a["en_named_positions"]),(215,215))
        self.assertEqual((a["cn_unnamed_positions"],a["en_unnamed_positions"]),(71,71))
        self.assertEqual((a["command_lines_cn"],a["command_lines_en"]),(276,276))
        self.assertTrue(a["commands_match_cn_en"])
        tr=a["translated_range"]
        self.assertEqual(tr["translated_source_lines"][-40:],NEW_LINES)
        self.assertEqual(tr["command_line_numbers"][-26:],NEW_COMMAND_LINES)
        self.assertEqual(tr["command_lines_in_range"],217)
        self.assertEqual(sum(tr["command_counts"].values()),217)
        self.assertEqual((tr["named_positions"],tr["unnamed_positions"]),(130,70))
        self.assertEqual((tr["decision_commands"],tr["decision_option_strings"],tr["predicate_branches"]),(0,0,0))
        self.assertEqual([x["source_line"] for x in a["version_differences"]],EXPECTED_DIFFERENCE_LINES)
        self.assertEqual(A["progress"]["translated"],200)
        self.assertEqual(A["command_preservation"]["translated_range_command_positions"],217)
        self.assertEqual(A["command_preservation"]["translated_range_command_numbers"][-26:],NEW_COMMAND_LINES)
        self.assertFalse(A["integrity"]["complete"])

    def test_speakers_and_unnamed_lines(self):
        rows=T["dialogues"][-40:]
        self.assertEqual(sum(x["kind"]=="named" for x in rows),22)
        self.assertEqual(sum(x["kind"]=="unnamed" for x in rows),18)
        self.assertEqual(rows[0]["speaker_cn"],"塔露拉")
        self.assertEqual(rows[1]["speaker_cn"],"W")
        self.assertEqual(rows[2]["kind"],"unnamed")
        self.assertEqual(rows[15]["speaker_cn"],"W")
        self.assertEqual(rows[-4]["speaker_cn"],"塔露拉")
        self.assertEqual(rows[-1]["speaker_cn"],"塔露拉")

    def test_qa_chronology_index(self):
        self.assertEqual(Q["version"],"v2.06")
        self.assertEqual((Q["partial_scene_named_ru"],Q["partial_scene_unnamed_ru"],Q["partial_scene_text_entries"]),(130,70,200))
        self.assertEqual(Q["all_story_text_entries_including_partial"],10162)
        self.assertEqual((Q["chapter_7_partial_named_ru"],Q["chapter_7_partial_unnamed_ru"],Q["chapter_7_partial_text_entries"]),(130,70,200))
        self.assertEqual(Q["chapter_7_text_entries_including_partial"],200)
        self.assertEqual(Q["partial_scenes"][0]["translated"],200)
        self.assertEqual(Q["partial_scenes"][0]["next_source_line"],418)
        self.assertEqual(Q["partial_scene_audit"]["translated"],200)
        self.assertEqual(Q["partial_scene_audit"]["translated_range_command_lines"],217)
        self.assertEqual(Q["next_scene"]["translated"],200)
        self.assertEqual(Q["next_scene"]["next_ordinal"],201)
        self.assertEqual(Q["next_scene"]["next_source_line"],418)
        self.assertEqual(M["version"],"v3.66")
        self.assertEqual(M["next_file"],"obt/main/level_st_07-01.txt")
        self.assertEqual((M["next_text_ordinal"],M["next_text_source_line"]),(201,418))
        self.assertEqual(M["translation_integrity"]["main_story_partial_text_entries"],200)
        self.assertEqual(M["translation_integrity"]["main_story_chapter_7_text_entries_including_partial"],200)
        self.assertIn("partial_first_draft\t130\t70\t200",I)

    def test_readme_history(self):
        self.assertIn("v3.66",R)
        self.assertIn("200/286",R)
        self.assertIn("№201, CN-строка 418",R)
        self.assertIn("v3.65",R)
        self.assertIn("160/286",R)
        self.assertIn("№161, CN-строка 352",R)
        self.assertIn("reports/QA_MAIN_STORY_v205.json",R)
        self.assertIn("v3.64",R)
        self.assertIn("120/286",R)
        self.assertIn("v3.62",R)
        self.assertIn("40/286",R)
        self.assertIn("CN-строка 82",R)

if __name__ == "__main__":
    unittest.main()
