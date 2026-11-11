# -*- coding: utf-8 -*-
import json, re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
T = load("story/story_chapter_6_stage_6-13_interlude_ru_v195.json")
A = load("reports/MAIN_6-13_INTERLUDE_SOURCE_AUDIT_v195.json")
Q = load("reports/QA_MAIN_STORY_v195.json")
M = load("chronology/CHRONOLOGY_MANIFEST_v355.json")
S = load("story/story_main_selection_ru_v190.json")
I = (ROOT / "story/CHAPTER_6_INDEX_v195.tsv").read_text(encoding="utf-8")
R = (ROOT / "README.md").read_text(encoding="utf-8")
NEW_LINES = [361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,378,379,380,381,382,383,384,385,389,393,394,395,396,397,398,401,402,403,404,405,406,407]
FULL_COUNTS = {"HEADER":1,"stopmusic":1,"delay":3,"Decision":34,"Predicate":45,"Dialog":12,"Character":25,"Blocker":11,"Background":3,"PlayMusic":1,"Image":3,"ImageTween":1,"hideitem":1}
TAIL_COUNTS = {"Decision":4,"Predicate":4,"Character":2,"Dialog":1,"Blocker":1,"Image":1}
class TestMainStory613InterludeV195(unittest.TestCase):
    def test_complete_progress_and_ordinals(self):
        p, rows = T["progress"], T["dialogues"]
        self.assertEqual(T["version"], "v1.95")
        self.assertEqual(T["status"], "first_draft_complete")
        self.assertEqual((p["translated"],p["total"],p["remaining"],p["complete"]),(269,269,0,True))
        self.assertEqual((p["named_translated"],p["unnamed_translated"]),(257,12))
        self.assertEqual((p["decision_commands_translated"],p["decision_commands_total"],p["decision_commands_remaining"]),(34,34,0))
        self.assertEqual((p["decision_option_strings_translated"],p["decision_option_strings_total"],p["decision_option_strings_remaining"]),(53,53,0))
        self.assertEqual((p["predicate_branches_translated"],p["predicate_branches_total"],p["predicate_branches_remaining"]),(45,45,0))
        self.assertEqual([x["ordinal"] for x in rows],list(range(1,270)))
        self.assertEqual([x["source_line"] for x in rows[-37:]],NEW_LINES)
        self.assertTrue(all(x["kind"]=="named" and x["speaker_cn"]=="霜星" for x in rows[-37:]))
        self.assertEqual(len({x["source_line"] for x in rows}),269)
    def test_text_payload_and_placeholders(self):
        payload = "\n".join(x["text_ru"] for x in T["dialogues"])
        options = "\n".join(s for d in T["decision_options_ru"] for s in d["options_ru"])
        self.assertTrue(all(x["text_ru"].strip() for x in T["dialogues"]))
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload + options))
        self.assertEqual(payload.count("{@nickname}"),5)
        self.assertEqual(T["source_alignment"]["placeholder_count_ru"],5)
        self.assertEqual(len(T["decision_options_ru"]),34)
        self.assertEqual(sum(len(x["options_ru"]) for x in T["decision_options_ru"]),53)
    def test_source_and_command_invariants(self):
        s, a = T["source"], T["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"],"ffa8947a78abc196f2ebfcb90ae2283ee136c953")
        self.assertEqual(s["en_git_blob_sha1"],"79204a97fedbc6e1950440f86a618c8d6efa37ba")
        self.assertEqual((a["cn_text_positions"],a["en_text_positions"]),(269,269))
        self.assertEqual((a["command_lines_cn"],a["command_lines_en"]),(141,141))
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        tr = a["translated_range"]
        self.assertEqual((tr["ordinal_start"],tr["ordinal_end"]),(1,269))
        self.assertEqual(tr["command_lines_in_range"],141)
        self.assertEqual(tr["command_counts"],FULL_COUNTS)
        self.assertEqual((tr["decision_commands"],tr["decision_option_strings"],tr["predicate_branches"]),(34,53,45))
        self.assertEqual(a["untranslated_positions"],0)
        self.assertEqual((a["placeholder_count_cn"],a["placeholder_count_en"],a["placeholder_count_ru"]),(5,5,5))
        self.assertEqual(A["integrity"]["translated_text_positions"],269)
        self.assertTrue(A["integrity"]["complete"])
        self.assertTrue(any(x.get("source_line")==382 for x in a["version_differences"]))
    def test_final_fragment_commands_and_decisions(self):
        tail = T["source_alignment"]["translated_chunks"][-1]
        self.assertEqual((tail["ordinal_start"],tail["ordinal_end"]),(233,269))
        self.assertEqual(tail["translated_source_lines"],NEW_LINES)
        self.assertEqual(tail["command_lines_in_range"],13)
        self.assertEqual(tail["command_counts"],TAIL_COUNTS)
        self.assertEqual((tail["decision_commands"],tail["decision_option_strings"],tail["predicate_branches"]),(4,8,4))
        final_options = [x for x in T["decision_options_ru"] if x["source_line"] in (376,386,390,399)]
        self.assertEqual(len(final_options),4)
        self.assertEqual(sum(len(x["options_ru"]) for x in final_options),8)
    def test_selection_index_manifest_and_qa(self):
        entry = S["files"]["obt/main/level_st_06-02.txt"]
        self.assertEqual((entry["dialogue_count"],entry["named_dialogue_count"],entry["unnamed_dialogue_count"]),(269,257,12))
        self.assertEqual(len(entry["dialogues"]),269)
        self.assertEqual(S["summary"],{"complete_files":122,"total_dialogue_entries_counted":9582,"historical_manifest_entries":9583,"inherited_delta":1})
        row = [x for x in I.splitlines() if x.startswith("level_st_06-02.txt")]
        self.assertEqual(len(row),1)
        self.assertEqual(row[0].split("\t")[:5],["level_st_06-02.txt","first_draft_complete","257","12","269"])
        self.assertEqual(M["version"],"v3.55")
        self.assertEqual(M["next_file"],"obt/main/level_main_06-15_end.txt")
        self.assertEqual((M["next_text_ordinal"],M["next_text_source_line"]),(1,16))
        self.assertEqual(M["translation_integrity"]["main_story_files"],122)
        self.assertEqual(M["translation_integrity"]["main_story_partial_files"],0)
        self.assertEqual(M["translation_integrity"]["main_story_complete_text_entries"],9583)
        self.assertEqual(Q["completed_story_text_entries"],9583)
        self.assertEqual(Q["selection_dialogue_entries_counted"],9582)
        self.assertEqual(Q["selection_vs_historical_manifest_delta"],1)
        self.assertEqual(Q["partial_scene_files"],0)
        self.assertEqual(Q["partial_scenes"],[])
        self.assertIsNone(Q["partial_scene_audit"])
        self.assertEqual(Q["next_scene"]["source_file"],"obt/main/level_main_06-15_end.txt")
        self.assertIn("269/269",R)
        self.assertIn("6-17 After Operation",R)
    def test_next_scene_inventory(self):
        n = M["next_source"]
        self.assertEqual(n["file"],"obt/main/level_main_06-15_end.txt")
        self.assertEqual((n["text_positions"],n["named_positions"],n["unnamed_positions"]),(89,86,3))
        self.assertEqual((n["command_lines"],n["decision_commands"],n["decision_option_total"],n["predicate_branches"]),(97,15,20,15))
        self.assertEqual(n["cn_git_blob_sha1"],"b8dc8453340f5eeb673c81bc82ad81be9ac7280a")
        self.assertEqual(n["en_git_blob_sha1"],"bc8db9e49aa225aef8e57bf62c87488d3cd05ff9")
if __name__ == "__main__":
    unittest.main()
