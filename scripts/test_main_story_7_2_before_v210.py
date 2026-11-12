# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStory72BeforeV210(unittest.TestCase):
    def test_prefix_and_position_order(self):
        old = load("story/story_chapter_7_stage_7-2_before_partial_ru_v209.json")
        new = load("story/story_chapter_7_stage_7-2_before_partial_ru_v210.json")
        self.assertEqual(new["version"], "v2.10")
        self.assertEqual(new["dialogues"][:40], old["dialogues"])
        self.assertEqual(len(new["dialogues"]), 80)
        self.assertEqual([x["ordinal"] for x in new["dialogues"]], list(range(1, 81)))
        expected = [9,12,13,14,15,16,24,26,28,30,32,33,34,35,36,37,38,44,47,49,50,56,58,60,62,63,64,65,67,68,69,73,77,79,81,90,91,93,94,96,97,108,115,117,120,121,123,124,126,128,129,131,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,167,168,169,170]
        self.assertEqual([x["source_line"] for x in new["dialogues"]], expected)
        self.assertEqual((new["progress"]["translated"], new["progress"]["remaining"]), (80, 132))
        self.assertEqual((new["progress"]["named_translated"], new["progress"]["unnamed_translated"]), (78, 2))
        self.assertEqual((new["progress"]["next_ordinal"], new["progress"]["next_source_line"]), (81, 171))
        for item in new["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))
            self.assertFalse(any(ch in item["text_ru"] for ch in "\r\n\t"))

    def test_cn_primary_decisions_and_differences(self):
        old = load("story/story_chapter_7_stage_7-2_before_partial_ru_v209.json")
        new = load("story/story_chapter_7_stage_7-2_before_partial_ru_v210.json")
        self.assertEqual(new["decision_options_ru"], old["decision_options_ru"])
        by_line = {x["source_line"]: x["text_ru"] for x in new["dialogues"]}
        self.assertIn("Ты ведь не поверишь", by_line[142])
        self.assertIn("сестрицей Они", by_line[158])
        self.assertIn("электромотоциклов", by_line[168])
        self.assertIn("разумными", by_line[145])
        audit = load("reports/MAIN_7-2_BEFORE_SOURCE_AUDIT_v210.json")
        self.assertEqual({x["source_line"] for x in audit["version_differences"]}, {65,128,142,145,158,168})
        self.assertFalse(audit["integrity"]["full_source_scripts_committed"])

    def test_source_hashes_and_commands(self):
        new = load("story/story_chapter_7_stage_7-2_before_partial_ru_v210.json")
        audit = load("reports/MAIN_7-2_BEFORE_SOURCE_AUDIT_v210.json")
        self.assertEqual(new["source"]["cn_git_blob_sha1"], "08b18f752b76276d36a69a6d984e429aef598051")
        self.assertEqual(new["source"]["en_git_blob_sha1"], "ce70e8bc2dcf65b80119fee693ef6bd53b88b50f")
        self.assertEqual((new["source_alignment"]["cn_text_positions"], new["source_alignment"]["en_text_positions"]), (212,212))
        self.assertEqual((new["source_alignment"]["cn_named_positions"], new["source_alignment"]["en_named_positions"]), (210,210))
        self.assertEqual((new["source_alignment"]["command_lines_cn"], new["source_alignment"]["command_lines_en"]), (133,133))
        self.assertTrue(new["source_alignment"]["commands_match_cn_en"])
        r = new["source_alignment"]["translated_range"]
        self.assertEqual((r["ordinal_start"],r["ordinal_end"]), (1,80))
        self.assertEqual((r["command_lines_in_range"],r["new_segment_command_lines"]), (90,34))
        self.assertEqual(sum(r["command_counts"].values()), 90)
        self.assertEqual(sum(r["new_segment_command_counts"].values()), 34)
        self.assertEqual(len(r["command_line_numbers"]), 90)
        self.assertEqual(len(r["new_segment_command_line_numbers"]), 34)
        self.assertEqual(audit["integrity"]["translated_positions"], 80)
        self.assertEqual(audit["integrity"]["untranslated_positions"], 132)
        self.assertTrue(audit["integrity"]["source_hashes_pinned"])
        self.assertEqual(audit["command_preservation"]["new_segment_command_positions"], 34)

    def test_qa_manifest_index_readme_glossary(self):
        q = load("reports/QA_MAIN_STORY_v210.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v370.json")
        index = (ROOT / "story/CHAPTER_7_INDEX_v210.tsv").read_text(encoding="utf-8").splitlines()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertEqual((q["partial_scene_named_ru"],q["partial_scene_unnamed_ru"],q["partial_scene_text_entries"]), (78,2,80))
        self.assertEqual((q["next_scene"]["translated"],q["next_scene"]["remaining"],q["next_scene"]["next_ordinal"],q["next_scene"]["next_source_line"]), (80,132,81,171))
        self.assertEqual((m["version"],m["next_text_ordinal"],m["next_text_source_line"]), ("v3.70",81,171))
        self.assertEqual((m["translation_integrity"]["main_story_partial_named_ru_lines"],m["translation_integrity"]["main_story_partial_text_entries"]), (78,80))
        self.assertEqual((m["translation_integrity"]["main_story_chapter_7_named_ru_lines_including_partial"],m["translation_integrity"]["main_story_chapter_7_text_entries_including_partial"]), (293,366))
        self.assertEqual(len(index),3)
        self.assertIn("level_main_07-02_beg.txt\tfirst_draft_partial\t78\t2\t80",index[2])
        self.assertIn("v3.71", readme.splitlines()[0])
        self.assertIn("v3.70", readme)
        self.assertIn("7-2 Before Operation (80/212:",readme[:5000])
        self.assertIn("сестрица Они",terms)
        self.assertIn("электромотоцикл",terms)

if __name__ == "__main__":
    unittest.main()
