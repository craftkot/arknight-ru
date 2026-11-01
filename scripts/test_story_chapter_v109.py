# coding: utf-8
"""Regression checks for chapter 5 stage 5-10 partial v1.09."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-10_beg.txt"
NEW = "story/story_chapter_5_stage_5-10_before_partial_ru_v109.json"
OLD = "story/story_chapter_5_stage_5-10_before_partial_ru_v108.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter510BeforePartialV109(unittest.TestCase):
    def test_contiguous_partial_translation(self):
        p = load(NEW)
        self.assertEqual(p["source_file"], REL)
        self.assertEqual(set(p["dialogues"]), {str(i) for i in range(1, 99)})
        self.assertFalse(p["progress"]["complete"])
        self.assertEqual((p["progress"]["named_ru_lines"], p["progress"]["next_named_ordinal"]), (98, 99))
        self.assertEqual((p["progress"]["source_lines_translated_through"], p["progress"]["first_untranslated_named_source_line"]), (284, 299))
        self.assertEqual((p["source_dialogue_line_numbers"]["52"], p["source_dialogue_line_numbers"]["98"]), (139, 284))
        self.assertTrue(all(v.strip() and not any(x in v for x in "\r\n\t") for v in p["dialogues"].values()))

    def test_previous_translation_preserved_and_cn_meaning(self):
        prev, cur = load(OLD), load(NEW)
        self.assertEqual({k: cur["dialogues"][k] for k in prev["dialogues"]}, prev["dialogues"])
        self.assertEqual(len(cur["dialogues"]) - len(prev["dialogues"]), 47)
        self.assertIn("их руках", cur["dialogues"]["54"])
        self.assertIn("полдюйма", cur["dialogues"]["59"])
        self.assertIn("Она знает", cur["dialogues"]["92"])
        self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", cur["source"]["cn_git_blob_sha1"]))

    def test_sources_and_selection(self):
        cur = load(NEW)
        self.assertEqual((cur["source"]["cn_git_blob_sha1"], cur["source"]["en_git_blob_sha1"]), ("922973f06fdda4acb1ad0207ef2ae6f07e3472f1", "dbf64cfdcc8e97b720398c386000477d0da81ea8"))
        a = load("reports/CHAPTER_5_STAGE_5-10_BEFORE_SOURCE_AUDIT_v109.json")["alignment"]
        self.assertEqual((a["cn_named"], a["en_named"], a["cn_bracket_commands"], a["en_bracket_commands"]), (247, 247, 425, 425))
        self.assertEqual((a["ru_partial_named_entries"], a["remaining_named_entries"], a["remaining_bare_entries"]), (98, 149, 1))
        self.assertEqual((a["source_choice_commands"], a["source_choice_options"]), (6, 10))
        sel = load("story/story_main_selection_ru_v107.json")
        self.assertEqual((len(sel["files"]), sum(x["dialogue_count"] for x in sel["files"].values())), (94, 5740))
        self.assertNotIn(REL, sel["files"])

    def test_manifest_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v109.json")
        q = load("reports/QA_MAIN_STORY_v109.json")
        t = m["translation_integrity"]
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 99))
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (94, 5705))
        self.assertEqual((t["main_story_partial_named_ru_lines"], t["main_story_named_ru_lines_including_partial"]), (98, 5803))
        self.assertEqual(t["main_story_text_entries_including_partial"], 5838)
        self.assertEqual((q["new_named_ru"], q["partial_scene_text_entries"], q["source_text_entries_remaining_excluding_choices"]), (47, 98, 150))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v109.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-10_beg.txt\tpartial_first_draft_98_of_247\t98\t0\t98", idx)

if __name__ == "__main__":
    unittest.main()
