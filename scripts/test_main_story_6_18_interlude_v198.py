# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_6_stage_6-18_interlude_partial_ru_v198.json")
A = load("reports/MAIN_6-18_INTERLUDE_SOURCE_AUDIT_v198.json")
Q = load("reports/QA_MAIN_STORY_v198.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v358.json")
I = (ROOT / "story/CHAPTER_6_INDEX_v198.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

SOURCE_LINES = [30,31,32,33,37,38,40,41,43,45,47,49,51,53,55,57,58,59,61,63,65,67,69,71,72,73,74,75,77,78,80,82,84,86,88,90,91,92,94,95,104,106,108,109,119,120,123,124,126,127,129,130,131,133,134,143,144,145,146,147,149,151,152,154,155,157,158,160,162,164,166,167,169,171,173,175,177,178,179,181,183,185,186,187,188,189,190,191,192,193,194,196,198,199,200,202,204,206,208,209,210,211,213,214,216,217,218,220,222,223,225,227,229]
NEW_LINES = [143,144,145,146,147,149,151,152,154,155,157,158,160,162,164,166,167,169,171,173,175,177,178,179,181,183,185,186,187,188,189,190,191,192,193,194,196,198,199,200,202,204,206,208,209,210,211,213,214,216,217,218,220,222,223,225,227,229]
NEW_COMMAND_LINES = [135,136,137,138,139,140,141,142,148,150,153,156,159,161,163,165,168,170,172,174,176,180,182,184,195,197,201,203,205,207,212,215,219,221,224,226,228]
RANGE_COMMAND_COUNTS = {"Dialog":4,"Character":61,"delay":4,"Blocker":6,"Background":3,"PlaySound":2,"Decision":2,"Predicate":5}

class TestMainStory618InterludeV198(unittest.TestCase):
    def test_positions_speakers_and_progress(self):
        self.assertEqual(T["version"], "v1.98")
        self.assertEqual(T["status"], "partial_first_draft")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"],p["total"],p["remaining"],p["complete"]),(113,290,177,False))
        self.assertEqual((p["named_translated"],p["named_total"],p["unnamed_translated"],p["unnamed_total"]),(109,285,4,5))
        self.assertEqual([x["ordinal"] for x in rows],list(range(1,114)))
        self.assertEqual([x["source_line"] for x in rows],SOURCE_LINES)
        self.assertEqual(sum(x["kind"]=="named" for x in rows),109)
        self.assertEqual(sum(x["kind"]=="unnamed" for x in rows),4)
        self.assertEqual([x["source_line"] for x in rows if x["kind"]=="unnamed"],[30,31,32,33])
        self.assertEqual({x["speaker_cn"] for x in rows if x["ordinal"]>=56},{"煌","灰喉"})
        self.assertEqual([x["source_line"] for x in rows if x["ordinal"]>=56],NEW_LINES)

    def test_decision_predicate_and_placeholders(self):
        p=T["progress"]
        self.assertEqual((p["decision_commands_translated"],p["decision_commands_total"],p["decision_commands_remaining"]),(2,2,0))
        self.assertEqual((p["decision_option_strings_translated"],p["decision_option_strings_total"],p["decision_option_strings_remaining"]),(4,4,0))
        self.assertEqual((p["predicate_branches_translated"],p["predicate_branches_total"],p["predicate_branches_remaining"]),(5,5,0))
        self.assertEqual(len(T["decision_options_ru"]),2)
        self.assertEqual(T["decision_options_ru"][1],{"source_line":135,"values":["1"],"options_ru":["Погиб один заражённый."]})
        payload="\n".join(x["text_ru"] for x in T["dialogues"])+"\n"+"\n".join(y for x in T["decision_options_ru"] for y in x["options_ru"])
        self.assertEqual(payload.count("{@nickname}"),4)
        self.assertIsNone(re.search(r"[\u3400-\u9fff]",payload))
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertTrue(all(y.strip() for x in T["decision_options_ru"] for y in x["options_ru"]))

    def test_source_alignment_and_range_commands(self):
        s,a=T["source"],T["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"],"f0b744c48b2a6592674a42e7c9c3e61cd8c226d8")
        self.assertEqual(s["en_git_blob_sha1"],"9f0a4ae9762665a21262d72ecd2ff09b34544187")
        self.assertEqual((a["cn_text_positions"],a["en_text_positions"]),(290,290))
        self.assertEqual((a["cn_named_positions"],a["cn_unnamed_positions"]),(285,5))
        self.assertEqual((a["command_lines_cn"],a["command_lines_en"]),(284,284))
        self.assertTrue(a["commands_match_cn_en"] and a["text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"] and a["speaker_label_names_match_after_localization"])
        self.assertTrue(a["command_line_numbers_match"] and a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        r=A["translated_range"]
        self.assertEqual((r["ordinal_start"],r["ordinal_end"],r["command_lines"]),(1,113,87))
        self.assertEqual(r["translated_source_lines"],SOURCE_LINES)
        self.assertEqual(r["command_counts"],RANGE_COMMAND_COUNTS)
        self.assertEqual(r["command_line_numbers"],sorted(r["command_line_numbers"]))
        self.assertEqual(len(r["command_line_numbers"]),87)
        self.assertTrue(set(NEW_COMMAND_LINES).issubset(set(r["command_line_numbers"])))
        self.assertEqual((r["decision_commands_translated"],r["decision_option_strings_translated"],r["predicate_branches_translated"]),(2,4,5))
        self.assertEqual(r["decision_option_source_lines"],[121,135])
        self.assertEqual(r["predicate_source_lines"],[122,125,128,132,136])
        self.assertEqual((r["placeholder_count_cn"],r["placeholder_count_en"],r["placeholder_count_ru"]),(4,4,4))
        self.assertEqual(A["integrity"]["untranslated_positions"],177)
        self.assertEqual(A["integrity"]["untranslated_cjk_in_ru"],0)
        self.assertFalse(A["integrity"]["complete"])

    def test_qa_index_readme_and_chronology(self):
        self.assertEqual(Q["version"],"v1.98")
        self.assertEqual((Q["completed_story_files"],Q["partial_scene_files"]),(123,1))
        self.assertEqual((Q["partial_scene_named_ru"],Q["partial_scene_unnamed_ru"],Q["partial_scene_text_entries"]),(109,4,113))
        self.assertEqual((Q["completed_story_text_entries"],Q["all_story_text_entries_including_partial"]),(9672,9785))
        self.assertEqual((Q["chapter_6_complete_files"],Q["chapter_6_partial_files"]),(26,1))
        self.assertEqual((Q["chapter_6_partial_named_ru"],Q["chapter_6_partial_unnamed_ru"],Q["chapter_6_partial_text_entries"]),(109,4,113))
        self.assertEqual((Q["chapter_6_text_entries_including_partial"],Q["chapter_6_named_ru_lines_including_partial"],Q["chapter_6_unnamed_ru_lines_including_partial"]),(3540,3421,119))
        self.assertEqual((Q["main_story_partial_decision_commands_ru"],Q["main_story_partial_decision_option_strings_ru"],Q["main_story_partial_predicate_branches_ru"]),(2,4,5))
        row=[x for x in I.splitlines() if x.startswith("level_st_06-03.txt\t")]
        self.assertEqual(len(row),1)
        self.assertIn("partial_first_draft\t109\t4\t113\tf0b744c48b2a6592674a42e7c9c3e61cd8c226d8\t9f0a4ae9762665a21262d72ecd2ff09b34544187",row[0])
        self.assertEqual(M["version"],"v3.58")
        self.assertEqual(M["next_file"],"obt/main/level_st_06-03.txt")
        self.assertEqual((M["next_text_ordinal"],M["next_text_source_line"]),(114,231))
        self.assertEqual((M["next_source"]["translated_positions"],M["next_source"]["remaining_positions"]),(113,177))
        self.assertEqual((M["next_source"]["decision_commands_translated"],M["next_source"]["decision_option_strings_translated"],M["next_source"]["predicate_branches_translated"]),(2,4,5))
        self.assertIn("113/290",R)
        self.assertIn("№114, CN-строка 231",R)
        self.assertFalse(Q["editorial_review"] or Q["in_game_test"])

    def test_source_scripts_are_not_committed(self):
        self.assertEqual(T["source_file"],"obt/main/level_st_06-03.txt")
        self.assertEqual(T["progress"]["remaining"],177)
        self.assertNotIn("source_script_cn",T)
        self.assertNotIn("source_script_en",T)
        self.assertIn("No complete CN or EN source script is included",T["notes_v198"][-1])

if __name__ == "__main__":
    unittest.main()
