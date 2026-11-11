# -*- coding: utf-8 -*-
import json, re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

T = load("story/story_chapter_6_stage_6-17_after_ru_v196.json")
A = load("reports/MAIN_6-17_AFTER_SOURCE_AUDIT_v196.json")
Q = load("reports/QA_MAIN_STORY_v196.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v356.json")
S = load("story/story_main_selection_ru_v191.json")
I = (ROOT / "story/CHAPTER_6_INDEX_v196.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")

SOURCE_LINES = [16,17,18,19,21,22,24,26,27,29,30,31,32,36,38,40,41,42,43,45,46,49,50,51,59,60,61,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,89,90,91,92,93,94,95,96,102,112,113,114,115,121,122,123,124,125,126,127,133,134,140,143,146,147,148,153,154,155,158,159,160,161,162,163,166,167,168,169,170,171,172,181,182]
COMMAND_COUNTS = {"HEADER":1,"stopmusic":1,"Blocker":11,"PlaySound":1,"Image":6,"Character":28,"ImageTween":1,"Delay":3,"Background":2,"Decision":15,"Predicate":15,"Dialog":12,"PlayMusic":1}

class TestMainStory617AfterV196(unittest.TestCase):
    def test_complete_positions_and_speakers(self):
        self.assertEqual(T["version"], "v1.96")
        self.assertEqual(T["status"], "first_draft_complete")
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (89,89,0,True))
        self.assertEqual((p["named_translated"],p["named_total"],p["unnamed_translated"],p["unnamed_total"]),(86,86,3,3))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1,90)))
        self.assertEqual([x["source_line"] for x in rows], SOURCE_LINES)
        self.assertEqual(sum(x["kind"]=="named" for x in rows),86)
        self.assertEqual(sum(x["kind"]=="unnamed" for x in rows),3)
        self.assertEqual([x["source_line"] for x in rows if x["kind"]=="unnamed"],[127,181,182])
        self.assertEqual(set(x["speaker_cn"] for x in rows if x["kind"]=="named"),{"霜星","煌","阿米娅"})

    def test_decision_predicate_and_placeholder_integrity(self):
        p=T["progress"]
        self.assertEqual((p["decision_commands_translated"],p["decision_commands_total"],p["decision_commands_remaining"]),(15,15,0))
        self.assertEqual((p["decision_option_strings_translated"],p["decision_option_strings_total"],p["decision_option_strings_remaining"]),(20,20,0))
        self.assertEqual((p["predicate_branches_translated"],p["predicate_branches_total"],p["predicate_branches_remaining"]),(15,15,0))
        self.assertEqual(len(T["decision_options_ru"]),15)
        self.assertEqual(sum(len(x["options_ru"]) for x in T["decision_options_ru"]),20)
        self.assertTrue(all(len(x["values"])==len(x["options_ru"]) for x in T["decision_options_ru"]))
        payload="\n".join(x["text_ru"] for x in T["dialogues"])+"\n"+"\n".join(y for x in T["decision_options_ru"] for y in x["options_ru"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]",payload))
        self.assertEqual(payload.count("{@nickname}"),1)
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertEqual(T["header_title_ru"],"Этап 3 (после боя)")

    def test_source_hashes_and_full_structure(self):
        s,a=T["source"],T["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"],"b8dc8453340f5eeb673c81bc82ad81be9ac7280a")
        self.assertEqual(s["en_git_blob_sha1"],"bc8db9e49aa225aef8e57bf62c87488d3cd05ff9")
        self.assertEqual((s["cn_physical_lines"],s["en_physical_lines"]),(186,187))
        self.assertEqual((a["cn_text_positions"],a["en_text_positions"]),(89,89))
        self.assertEqual((a["cn_named_positions"],a["cn_unnamed_positions"]),(86,3))
        self.assertEqual((a["command_lines_cn"],a["command_lines_en"]),(97,97))
        self.assertEqual(a["command_counts"],COMMAND_COUNTS)
        self.assertTrue(a["named_text_line_numbers_match"])
        self.assertTrue(a["unnamed_text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"])
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual((a["decision_commands"],a["decision_option_total"],a["predicate_branches"]),(15,20,15))
        self.assertEqual((a["placeholder_count_cn"],a["placeholder_count_en"],a["placeholder_count_ru"]),(1,1,1))
        self.assertEqual((A["integrity"]["translated_text_positions"],A["integrity"]["translated_decision_option_strings"]),(89,20))
        self.assertEqual(A["integrity"]["untranslated_cjk_in_ru"],0)
        self.assertTrue(any(x["source_line"]==126 for x in A["version_differences"]))

    def test_selection_index_qa_and_manifest(self):
        entry=S["files"]["obt/main/level_main_06-15_end.txt"]
        self.assertEqual((entry["dialogue_count"],entry["named_dialogue_count"],entry["unnamed_dialogue_count"]),(89,86,3))
        self.assertEqual(len(entry["dialogues"]),89)
        self.assertEqual(sum(len(x) for x in entry["decisions"].values()),20)
        self.assertEqual(S["summary"],{"complete_files":123,"total_dialogue_entries_counted":9671,"historical_manifest_entries":9672,"inherited_delta":1})
        row=[x for x in I.splitlines() if x.startswith("level_main_06-15_end.txt\t")]
        self.assertEqual(len(row),1)
        self.assertIn("first_draft_complete\t86\t3\t89\tb8dc8453340f5eeb673c81bc82ad81be9ac7280a\tbc8db9e49aa225aef8e57bf62c87488d3cd05ff9",row[0])
        self.assertEqual(M["version"],"v3.56")
        self.assertEqual(M["next_file"],"obt/main/level_st_06-03.txt")
        self.assertEqual((M["next_text_ordinal"],M["next_text_source_line"]),(1,30))
        self.assertEqual(Q["completed_story_files"],123)
        self.assertEqual(Q["completed_story_text_entries"],9672)
        self.assertEqual(Q["selection_dialogue_entries_counted"],9671)
        self.assertEqual(Q["selection_vs_historical_manifest_delta"],1)
        self.assertEqual(Q["partial_scene_files"],0)
        self.assertEqual(Q["partial_scenes"],[])
        self.assertEqual(Q["next_scene"]["source_file"],"obt/main/level_st_06-03.txt")
        self.assertEqual(Q["next_scene"]["total"],290)
        self.assertFalse(Q["editorial_review"])
        self.assertFalse(Q["in_game_test"])
        self.assertIn("6-17 After Operation",R)
        self.assertIn("6-18 Only You Know",R)

    def test_next_scene_inventory(self):
        n=M["next_source"]
        self.assertEqual(n["file"],"obt/main/level_st_06-03.txt")
        self.assertEqual((n["text_positions"],n["named_positions"],n["unnamed_positions"]),(290,285,5))
        self.assertEqual((n["command_lines"],n["decision_commands"],n["decision_option_total"],n["predicate_branches"]),(284,2,4,5))
        self.assertEqual(n["cn_git_blob_sha1"],"f0b744c48b2a6592674a42e7c9c3e61cd8c226d8")
        self.assertEqual(n["en_git_blob_sha1"],"9f0a4ae9762665a21262d72ecd2ff09b34544187")

if __name__ == "__main__":
    unittest.main()
