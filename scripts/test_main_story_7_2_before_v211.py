# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStory72BeforeV211(unittest.TestCase):
    def test_prefix_and_position_order(self):
        old = load("story/story_chapter_7_stage_7-2_before_partial_ru_v210.json")
        new = load("story/story_chapter_7_stage_7-2_before_partial_ru_v211.json")
        self.assertEqual(new["version"], "v2.11")
        self.assertEqual(new["dialogues"][:80], old["dialogues"])
        self.assertEqual(len(new["dialogues"]), 120)
        self.assertEqual([x["ordinal"] for x in new["dialogues"]], list(range(1, 121)))
        expected_new_lines = list(range(171, 199)) + list(range(204, 216))
        self.assertEqual([x["source_line"] for x in new["dialogues"][80:]], expected_new_lines)
        self.assertEqual((new["progress"]["translated"], new["progress"]["remaining"]), (120, 92))
        self.assertEqual((new["progress"]["named_translated"], new["progress"]["unnamed_translated"]), (118, 2))
        self.assertEqual((new["progress"]["next_ordinal"], new["progress"]["next_source_line"]), (121, 216))
        for item in new["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))
            self.assertFalse(any(ch in item["text_ru"] for ch in "\r\n\t"))

    def test_cn_primary_lines_and_differences(self):
        old = load("story/story_chapter_7_stage_7-2_before_partial_ru_v210.json")
        new = load("story/story_chapter_7_stage_7-2_before_partial_ru_v211.json")
        self.assertEqual(new["decision_options_ru"], old["decision_options_ru"])
        by_line = {x["source_line"]: x["text_ru"] for x in new["dialogues"]}
        self.assertIn("царапина", by_line[171])
        self.assertIn("загнутый уголок", by_line[171])
        self.assertIn("жёлтое пятно", by_line[171])
        self.assertIn("лишила их последнего пристанища", by_line[175])
        self.assertIn("взгляд и методы", by_line[198])
        self.assertEqual(by_line[210], "Я заражена.")
        audit = load("reports/MAIN_7-2_BEFORE_SOURCE_AUDIT_v211.json")
        self.assertEqual(
            {x["source_line"] for x in audit["version_differences"]},
            {65, 128, 142, 145, 158, 168, 171, 174, 175, 187, 197, 198, 209}
        )
        self.assertFalse(audit["integrity"]["full_source_scripts_committed"])

    def test_source_hashes_and_commands(self):
        new = load("story/story_chapter_7_stage_7-2_before_partial_ru_v211.json")
        audit = load("reports/MAIN_7-2_BEFORE_SOURCE_AUDIT_v211.json")
        self.assertEqual(new["source"]["cn_git_blob_sha1"], "08b18f752b76276d36a69a6d984e429aef598051")
        self.assertEqual(new["source"]["en_git_blob_sha1"], "ce70e8bc2dcf65b80119fee693ef6bd53b88b50f")
        self.assertEqual((new["source_alignment"]["cn_text_positions"], new["source_alignment"]["en_text_positions"]), (212, 212))
        self.assertEqual((new["source_alignment"]["cn_named_positions"], new["source_alignment"]["en_named_positions"]), (210, 210))
        self.assertEqual((new["source_alignment"]["command_lines_cn"], new["source_alignment"]["command_lines_en"]), (133, 133))
        self.assertTrue(new["source_alignment"]["commands_match_cn_en"])
        r = new["source_alignment"]["translated_range"]
        self.assertEqual((r["ordinal_start"], r["ordinal_end"]), (1, 120))
        self.assertEqual((r["command_lines_in_range"], r["new_segment_command_lines"]), (95, 5))
        self.assertEqual(sum(r["command_counts"].values()), 95)
        self.assertEqual(sum(r["new_segment_command_counts"].values()), 5)
        self.assertEqual(r["new_segment_command_line_numbers"], [199, 200, 201, 202, 203])
        self.assertEqual(audit["integrity"]["translated_positions"], 120)
        self.assertEqual(audit["integrity"]["untranslated_positions"], 92)
        self.assertTrue(audit["integrity"]["source_hashes_pinned"])
        self.assertEqual(audit["command_preservation"]["new_segment_command_positions"], 5)
        self.assertTrue(audit["command_preservation"]["all_source_command_positions_preserved"])

    def test_qa_manifest_index_readme_and_terms(self):
        q = load("reports/QA_MAIN_STORY_v211.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v371.json")
        index = (ROOT / "story/CHAPTER_7_INDEX_v211.tsv").read_text(encoding="utf-8").splitlines()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertEqual((q["partial_scene_named_ru"], q["partial_scene_unnamed_ru"], q["partial_scene_text_entries"]), (118, 2, 120))
        self.assertEqual((q["next_scene"]["translated"], q["next_scene"]["remaining"], q["next_scene"]["next_ordinal"], q["next_scene"]["next_source_line"]), (120, 92, 121, 216))
        self.assertEqual((m["version"], m["next_text_ordinal"], m["next_text_source_line"]), ("v3.71", 121, 216))
        self.assertEqual((m["translation_integrity"]["main_story_partial_named_ru_lines"], m["translation_integrity"]["main_story_partial_text_entries"]), (118, 120))
        self.assertEqual((m["translation_integrity"]["main_story_chapter_7_named_ru_lines_including_partial"], m["translation_integrity"]["main_story_chapter_7_text_entries_including_partial"]), (333, 406))
        self.assertEqual(len(index), 3)
        self.assertIn("level_main_07-02_beg.txt\tfirst_draft_partial\t118\t2\t120", index[2])
        self.assertIn("v3.71", readme.splitlines()[0])
        self.assertIn("7-2 Before Operation (120/212:", readme[:5000])
        self.assertIn("А Фаат", terms)

if __name__ == "__main__":
    unittest.main()
