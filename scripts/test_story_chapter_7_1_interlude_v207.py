# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStory71InterludeV207(unittest.TestCase):
    def test_contiguous_prefix_and_new_positions(self):
        old = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v206.json")
        new = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v207.json")
        self.assertEqual(new["version"], "v2.07")
        self.assertEqual(new["dialogues"][:200], old["dialogues"])
        self.assertEqual(len(new["dialogues"]), 240)
        self.assertEqual([x["ordinal"] for x in new["dialogues"]], list(range(1, 241)))
        self.assertEqual([x["source_line"] for x in new["dialogues"][200:]], [
            418,424,430,431,433,435,437,438,439,440,442,443,445,446,448,449,
            451,453,454,456,457,458,459,461,463,465,466,468,470,471,473,474,
            476,478,480,481,482,484,485,487
        ])
        new_entries = new["dialogues"][200:]
        self.assertEqual(sum(x["kind"] == "named" for x in new_entries), 39)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in new_entries), 1)
        self.assertEqual((new["progress"]["translated"], new["progress"]["total"],
                          new["progress"]["remaining"], new["progress"]["complete"]),
                         (240, 286, 46, False))
        self.assertEqual((new["progress"]["named_translated"], new["progress"]["unnamed_translated"]), (169, 71))
        self.assertEqual((new["progress"]["next_ordinal"], new["progress"]["next_source_line"]), (241, 489))

    def test_source_pins_and_cn_primary_differences(self):
        d = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v207.json")
        self.assertEqual(d["source"]["cn_git_blob_sha1"], "1c613bfbf006470b3b8e131b9fcb8b8f53e19ea5")
        self.assertEqual(d["source"]["en_git_blob_sha1"], "7a204cb0010abcbf60f12017f0b2b4d02eaba156")
        self.assertEqual((d["source_alignment"]["cn_text_positions"], d["source_alignment"]["en_text_positions"]), (286, 286))
        self.assertEqual((d["source_alignment"]["command_lines_cn"], d["source_alignment"]["command_lines_en"]), (276, 276))
        self.assertTrue(d["source_alignment"]["commands_match_cn_en"])
        self.assertIn("Ten lexical/meaning differences", d["source"]["version_difference"])
        self.assertIn("line 238", d["source"]["version_difference"])
        self.assertIn("465–466", d["source"]["version_difference"])

    def test_command_preservation_and_audit(self):
        d = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v207.json")
        a = load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v207.json")
        self.assertEqual(d["source_alignment"]["translated_range"]["command_lines_in_range"], 247)
        self.assertEqual(d["source_alignment"]["translated_range"]["new_segment_command_lines"], 30)
        self.assertEqual(sum(d["source_alignment"]["translated_range"]["command_counts"].values()), 247)
        self.assertEqual(a["translated_range"]["newly_translated_positions"], 40)
        self.assertEqual(a["translated_range"]["remaining_positions"], 46)
        self.assertEqual(a["command_preservation"]["translated_range_command_positions"], 247)
        self.assertEqual(a["command_preservation"]["new_segment_command_positions"], 30)
        self.assertTrue(a["command_preservation"]["all_source_command_positions_preserved"])
        self.assertEqual([x["source_line"] for x in a["version_differences"]][-2:], [238, 465])

    def test_qa_manifest_readme_and_terms(self):
        q = load("reports/QA_MAIN_STORY_v207.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v367.json")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertEqual((q["partial_scene_named_ru"], q["partial_scene_unnamed_ru"],
                          q["partial_scene_text_entries"], q["all_story_text_entries_including_partial"]),
                         (169, 71, 240, 10202))
        self.assertEqual((q["next_scene"]["next_ordinal"], q["next_scene"]["next_source_line"]), (241, 489))
        self.assertEqual((m["version"], m["next_text_ordinal"], m["next_text_source_line"]), ("v3.67", 241, 489))
        self.assertEqual((m["translation_integrity"]["main_story_partial_text_entries"],
                          m["translation_integrity"]["main_story_partial_named_ru_lines"],
                          m["translation_integrity"]["main_story_partial_unnamed_ru_lines"]), (240, 169, 71))
        self.assertIn("240/286", readme)
        self.assertIn("№241", readme)
        self.assertIn("десять лексических/смысловых расхождений", readme)
        self.assertIn("Patriot / 爱国者 — Патриот", terms)

    def test_russian_entries_are_nonempty_and_have_no_untranslated_cjk(self):
        d = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v207.json")
        for entry in d["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertFalse(re.search(r"[\u4e00-\u9fff]", entry["text_ru"]))

if __name__ == "__main__":
    unittest.main()
