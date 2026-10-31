# coding: utf-8
"""Regression tests for chapter 4-9 after battle (v0.85)."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-09_end.txt"
NEW = "story/story_chapter_4_stage_4-9_after_ru_v085.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter49AfterV085(unittest.TestCase):
    def test_complete_source_pins(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (61, 61, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 62))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (
            "d5607c23768b9859f530ded3993d823ae8d77a7b", "634fc3210f9a80f7571462478f53fae4ebe1cf3c"))
        self.assertIn("принцессу йети", cfg["dialogues"]["36"])
        self.assertIn("крош", cfg["dialogues"]["39"])
        for s in cfg["dialogues"].values():
            self.assertTrue(isinstance(s, str) and s.strip())
            self.assertFalse(any(c in s for c in "\r\n\t"))

    def test_previous_scenes_unchanged(self):
        old = load("story/story_main_selection_ru_v084.json")
        new = load("story/story_main_selection_ru_v085.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (77, 78))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4621)
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_manifest_and_index(self):
        a = load("reports/CHAPTER_4_STAGE_4-9_AFTER_SOURCE_AUDIT_v085.json")["alignment"]
        self.assertEqual((a["cn_named"], a["en_named"], a["ru_complete_text_entries"]), (61, 61, 61))
        self.assertEqual((a["source_non_dialogue_commands_cn"], a["source_non_dialogue_commands_en"]), (116, 116))
        self.assertTrue(a["cn_en_text_source_line_positions_equal"] and a["cn_en_non_dialogue_commands_equal"])
        m = load("chronology/CHRONOLOGY_MANIFEST_v085.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-10_beg.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (78, 4605))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (18, 1074, 16))
        q = load("reports/QA_MAIN_STORY_v085.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"], q["source_choice_options"]), (61, 78, 0))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v085.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-09_end.txt\tfirst_draft_complete\t61\t0\t61", idx)

    def test_preview_preserves_commands_and_names(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        lines = ['[HEADER(key="title_test")]\n', '[Background(image="bg_cher_2")]\n']
        for i in range(1, 62):
            lines.append('[Character(name="char_test")]\n')
            who = "FrostNova" if i >= 59 else "Amiya"
            lines.append('[name="' + who + '"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 61)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn('[name="ФростНова"]', patched.decode())
        self.assertIn(cfg["dialogues"]["61"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
