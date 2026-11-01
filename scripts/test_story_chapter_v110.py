# coding: utf-8
"""Regression checks for chapter 5 stage 5-10 partial v1.10."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-10_beg.txt"
NEW = "story/story_chapter_5_stage_5-10_before_partial_ru_v110.json"
OLD = "story/story_chapter_5_stage_5-10_before_partial_ru_v109.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter510BeforePartialV110(unittest.TestCase):
    def test_contiguous_partial_translation(self):
        p = load(NEW)
        self.assertEqual(p["source_file"], REL)
        self.assertEqual(set(p["dialogues"]), {str(i) for i in range(1, 158)})
        self.assertFalse(p["progress"]["complete"])
        self.assertEqual((p["progress"]["named_ru_lines"], p["progress"]["next_named_ordinal"]), (157, 158))
        self.assertEqual((p["progress"]["source_lines_translated_through"], p["progress"]["first_untranslated_named_source_line"]), (470, 484))
        self.assertEqual((p["source_dialogue_line_numbers"]["99"], p["source_dialogue_line_numbers"]["157"]), (299, 470))
        self.assertTrue(all(v.strip() and "\n" not in v and "\r" not in v for v in p["dialogues"].values()))

    def test_previous_translation_preserved_and_cn_meaning(self):
        prev, cur = load(OLD), load(NEW)
        self.assertEqual({k: cur["dialogues"][k] for k in prev["dialogues"]}, prev["dialogues"])
        self.assertEqual({k: cur["source_dialogue_line_numbers"][k] for k in prev["source_dialogue_line_numbers"]}, prev["source_dialogue_line_numbers"])
        self.assertEqual(len(cur["dialogues"]) - len(prev["dialogues"]), 59)
        self.assertIn("теплового потока", cur["dialogues"]["125"])
        self.assertIn("десяток с лишним секунд", cur["dialogues"]["138"])
        self.assertIn("обрушения", cur["dialogues"]["154"])

    def test_sources_and_selection(self):
        cur = load(NEW)
        self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", cur["source"]["cn_git_blob_sha1"]))
        self.assertEqual((cur["source"]["cn_git_blob_sha1"], cur["source"]["en_git_blob_sha1"]), ("922973f06fdda4acb1ad0207ef2ae6f07e3472f1", "dbf64cfdcc8e97b720398c386000477d0da81ea8"))
        a = load("reports/CHAPTER_5_STAGE_5-10_BEFORE_SOURCE_AUDIT_v110.json")["alignment"]
        self.assertEqual((a["cn_named"], a["en_named"], a["cn_bracket_commands"], a["en_bracket_commands"]), (247, 247, 425, 425))
        self.assertEqual((a["ru_partial_named_entries"], a["remaining_named_entries"], a["remaining_bare_entries"]), (157, 90, 1))
        self.assertEqual((a["source_choice_commands"], a["source_choice_options"]), (6, 10))
        sel = load("story/story_main_selection_ru_v107.json")
        self.assertEqual((len(sel["files"]), sum(x["dialogue_count"] for x in sel["files"].values())), (94, 5740))
        self.assertNotIn(REL, sel["files"])

    def test_manifest_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v110.json")
        q = load("reports/QA_MAIN_STORY_v110.json")
        t = m["translation_integrity"]
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 158))
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (94, 5705))
        self.assertEqual((t["main_story_partial_named_ru_lines"], t["main_story_named_ru_lines_including_partial"]), (157, 5862))
        self.assertEqual(t["main_story_text_entries_including_partial"], 5897)
        self.assertEqual((q["new_named_ru"], q["partial_scene_text_entries"], q["source_text_entries_remaining_excluding_choices"]), (59, 157, 91))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v110.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-10_beg.txt\tpartial_first_draft_157_of_247\t157\t0\t157", idx)

if __name__ == "__main__":
    unittest.main()
