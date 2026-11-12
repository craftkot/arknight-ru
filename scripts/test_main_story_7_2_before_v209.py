# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStory72BeforeV209(unittest.TestCase):
    def test_partial_prefix_and_position_order(self):
        d = load("story/story_chapter_7_stage_7-2_before_partial_ru_v209.json")
        self.assertEqual(d["version"], "v2.09")
        self.assertEqual(d["status"], "first_draft_partial")
        self.assertEqual(len(d["dialogues"]), 40)
        self.assertEqual([x["ordinal"] for x in d["dialogues"]], list(range(1, 41)))
        self.assertEqual([x["source_line"] for x in d["dialogues"]], [9,12,13,14,15,16,24,26,28,30,32,33,34,35,36,37,38,44,47,49,50,56,58,60,62,63,64,65,67,68,69,73,77,79,81,90,91,93,94,96])
        self.assertEqual(sum(x["kind"] == "named" for x in d["dialogues"]), 38)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in d["dialogues"]), 2)
        self.assertEqual(d["progress"]["translated"], 40)
        self.assertEqual(d["progress"]["remaining"], 172)
        self.assertEqual((d["progress"]["named_translated"], d["progress"]["unnamed_translated"]), (38, 2))
        self.assertEqual((d["progress"]["next_ordinal"], d["progress"]["next_source_line"]), (41, 97))
        for item in d["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))

    def test_decision_options_and_predicate_branches(self):
        d = load("story/story_chapter_7_stage_7-2_before_partial_ru_v209.json")
        opts = d["decision_options_ru"]
        self.assertEqual([x["source_line"] for x in opts], [70, 74, 85])
        self.assertEqual([x["values"] for x in opts], [["1"], ["1"], ["1", "2", "3"]])
        self.assertEqual(sum(len(x["options_ru"]) for x in opts), 5)
        self.assertEqual(d["progress"]["decision_commands_translated"], 3)
        self.assertEqual(d["progress"]["decision_option_strings_translated"], 5)
        self.assertEqual(d["progress"]["predicate_branches_translated"], 5)
        self.assertEqual(d["source_alignment"]["predicate_source_lines"], [71, 75, 86])

    def test_source_hashes_and_full_structure(self):
        d = load("story/story_chapter_7_stage_7-2_before_partial_ru_v209.json")
        a = load("reports/MAIN_7-2_BEFORE_SOURCE_AUDIT_v209.json")
        self.assertEqual(d["source"]["cn_git_blob_sha1"], "08b18f752b76276d36a69a6d984e429aef598051")
        self.assertEqual(d["source"]["en_git_blob_sha1"], "ce70e8bc2dcf65b80119fee693ef6bd53b88b50f")
        self.assertEqual((d["source_alignment"]["cn_text_positions"], d["source_alignment"]["en_text_positions"]), (212, 212))
        self.assertEqual((d["source_alignment"]["cn_named_positions"], d["source_alignment"]["en_named_positions"]), (210, 210))
        self.assertEqual((d["source_alignment"]["cn_unnamed_positions"], d["source_alignment"]["en_unnamed_positions"]), (2, 2))
        self.assertEqual((d["source_alignment"]["command_lines_cn"], d["source_alignment"]["command_lines_en"]), (133, 133))
        self.assertTrue(d["source_alignment"]["commands_match_cn_en"])
        self.assertTrue(d["source_alignment"]["command_names_and_parameters_match_after_decision_option_normalization"])
        r = d["source_alignment"]["translated_range"]
        self.assertEqual(r["command_lines_in_range"], 56)
        self.assertEqual(sum(r["command_counts"].values()), 56)
        self.assertEqual(a["integrity"]["translated_positions"], 40)
        self.assertEqual(a["integrity"]["untranslated_positions"], 172)
        self.assertTrue(a["integrity"]["source_hashes_pinned"])
        self.assertFalse(a["integrity"]["full_source_scripts_committed"])

    def test_qa_manifest_and_index(self):
        q = load("reports/QA_MAIN_STORY_v209.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v369.json")
        index = (ROOT / "story/CHAPTER_7_INDEX_v209.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual((q["completed_story_files"], q["completed_story_text_entries"]), (125, 10248))
        self.assertEqual((q["partial_scene_files"], q["partial_scene_named_ru"], q["partial_scene_unnamed_ru"], q["partial_scene_text_entries"]), (1, 38, 2, 40))
        self.assertEqual(q["next_scene"]["source_file"], "obt/main/level_main_07-02_beg.txt")
        self.assertEqual((q["next_scene"]["translated"], q["next_scene"]["remaining"], q["next_scene"]["next_ordinal"], q["next_scene"]["next_source_line"]), (40, 172, 41, 97))
        self.assertEqual((m["version"], m["next_file"], m["next_text_ordinal"], m["next_text_source_line"]), ("v3.69", "obt/main/level_main_07-02_beg.txt", 41, 97))
        self.assertEqual((m["translation_integrity"]["main_story_partial_files"], m["translation_integrity"]["main_story_partial_text_entries"]), (1, 40))
        self.assertEqual(len(index), 3)
        self.assertIn("level_main_07-02_beg.txt\tfirst_draft_partial\t38\t2\t40", index[2])

    def test_readme_and_glossary_are_current(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertIn("v3.71", readme.splitlines()[0])
        self.assertIn("v3.70", readme)
        self.assertIn("7-2 Before Operation (80/212:", readme[:5000])
        self.assertIn("Крысиный король", terms)
        self.assertIn("Грейтейл", terms)
        self.assertIn("Вэй Яньу", terms)

if __name__ == "__main__":
    unittest.main()
