# coding: utf-8
"""Regression checks for the contiguous 5-10 after-battle v1.13 partial draft."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-10_end.txt"
NEW = "story/story_chapter_5_stage_5-10_after_partial_ru_v113.json"
OLD = "story/story_chapter_5_stage_5-10_after_partial_ru_v112.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter510AfterPartialV113(unittest.TestCase):
    def test_contiguous_and_previous_unchanged(self):
        a, b = load(OLD), load(NEW)
        self.assertEqual(b["source_file"], REL)
        self.assertEqual(set(b["dialogues"]), {str(i) for i in range(1, 78)})
        self.assertEqual(set(b["source_dialogue_line_numbers"]), set(b["dialogues"]))
        self.assertEqual({k:b["dialogues"][k] for k in a["dialogues"]}, a["dialogues"])
        self.assertEqual({k:b["source_dialogue_line_numbers"][k] for k in a["source_dialogue_line_numbers"]}, a["source_dialogue_line_numbers"])

    def test_progress_and_semantic_exception(self):
        c = load(NEW)
        self.assertEqual((c["progress"]["named_ru_lines"], c["progress"]["remaining_text_entries"], c["progress"]["next_named_ordinal"], c["progress"]["first_untranslated_named_source_line"]), (77, 73, 78, 210))
        self.assertEqual((c["source_dialogue_line_numbers"]["46"], c["source_dialogue_line_numbers"]["77"]), (115, 201))
        self.assertIn("обнажить клинок", c["dialogues"]["75"])
        self.assertIn("{@nickname}", c["dialogues"]["42"])
        self.assertFalse(c["progress"]["complete"])
        self.assertTrue(all(s.strip() and "\n" not in s and "\r" not in s for s in c["dialogues"].values()))

    def test_source_audit_and_selection(self):
        a = load("reports/CHAPTER_5_STAGE_5-10_AFTER_SOURCE_AUDIT_v113.json")
        q = load("reports/QA_MAIN_STORY_v113.json")
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["en_tagged"], a["alignment"]["cn_bracket_commands"], a["alignment"]["en_bracket_commands"]), (150, 150, 265, 265))
        self.assertEqual((a["alignment"]["ru_tagged_entries"], a["alignment"]["ru_remaining_entries"]), (77, 73))
        self.assertEqual((q["new_named_ru"], q["scene_ru_named"], q["scene_remaining_named"]), (32, 77, 73))
        self.assertFalse(q["included_in_complete_story_selection"])
        sel = load("story/story_main_selection_ru_v111.json")
        self.assertEqual(len(sel["files"]), 95)
        self.assertNotIn(REL, sel["files"])

    def test_manifest_and_index(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v113.json")
        t = m["translation_integrity"]
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 78))
        self.assertEqual((t["main_story_files"], t["main_story_partial_named_ru_lines"], t["main_story_text_entries_including_partial"]), (95, 77, 6065))
        idx = (ROOT / "story/CHAPTER_5_INDEX_v113.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-10_end.txt\tpartial_first_draft_77_of_150\t77\t0\t77", idx)

if __name__ == "__main__":
    unittest.main()
