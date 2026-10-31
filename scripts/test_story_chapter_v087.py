# coding: utf-8
"""Regression tests for the partial chapter 4-10 after-battle draft (v0.87)."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_04-10_end.txt"
PARTIAL = "story/story_chapter_4_stage_4-10_after_partial_ru_v087.json"
CN_SHA = "190af39edc748f963b26cb1ef510c63ea7c3f851"
EN_SHA = "d160f1b33b0ea43597526e8966b854623d6b0e1e"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter410AfterPartialV087(unittest.TestCase):
    def test_partial_is_contiguous_and_not_complete(self):
        p = load(PARTIAL)
        self.assertEqual(p["source_file"], REL)
        self.assertFalse(p["progress"]["complete"])
        self.assertEqual((p["progress"]["named_ru_lines"], p["progress"]["source_total_text_entries"], p["progress"]["remaining_text_entries"]), (40, 157, 117))
        self.assertEqual((p["progress"]["source_lines_translated_through"], p["progress"]["next_named_ordinal"]), (76, 41))
        self.assertEqual(set(p["dialogues"]), {str(i) for i in range(1, 41)})
        self.assertEqual(p["dialogues"]["14"], "——♩——♬——")
        self.assertEqual(p["dialogues"]["20"], "…♩…")
        for line in p["dialogues"].values():
            self.assertTrue(isinstance(line, str) and line.strip())
            self.assertFalse(any(c in line for c in "\r\n\t"))

    def test_source_pins_and_alignment(self):
        p = load(PARTIAL)
        self.assertEqual((p["source"]["cn_git_blob_sha1"], p["source"]["en_git_blob_sha1"]), (CN_SHA, EN_SHA))
        a = load("reports/CHAPTER_4_STAGE_4-10_AFTER_SOURCE_AUDIT_v087.json")
        self.assertEqual((a["alignment"]["cn_named"], a["alignment"]["en_named"]), (157, 157))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (210, 210))
        self.assertTrue(a["alignment"]["cn_en_named_source_line_positions_equal"])
        self.assertTrue(a["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(a["alignment"]["next_untranslated_dialogue_source_line"], 82)

    def test_index_manifest_and_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v087.json")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (79, 4713))
        self.assertEqual((t["main_story_chapter_4_partial_files"], t["main_story_chapter_4_partial_named_ru_lines"]), (1, 40))
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 41))
        q = load("reports/QA_MAIN_STORY_v087.json")
        self.assertEqual((q["new_text_entries"], q["source_text_entries_remaining"]), (40, 117))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v087.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-10_end.txt\tpartial_first_draft_40_of_157\t40\t0\t40", idx)

    def test_complete_selection_is_unchanged(self):
        selection = load("story/story_main_selection_ru_v086.json")
        self.assertEqual(len(selection["files"]), 79)
        self.assertNotIn(REL, selection["files"])
        self.assertEqual(sum(f["dialogue_count"] for f in selection["files"].values()), 4729)

if __name__ == "__main__":
    unittest.main()
