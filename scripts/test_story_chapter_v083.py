# coding: utf-8
"""Regression tests for chapter 4-8 after battle (v0.83)."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-08_end.txt"
NEW = "story/story_chapter_4_stage_4-8_after_ru_v083.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter48AfterV083(unittest.TestCase):
    def test_complete_and_source_pins(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (67, 67, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 68))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (
            "427e9591d473c3d33e39690f5d970d7b6218403d",
            "d95d8662b81f24a6e31ed3d9c6f59474d50931bc"))
        self.assertIn("предплечье", cfg["dialogues"]["27"])
        self.assertIn("Кальцит", cfg["dialogues"]["67"])
        for value in cfg["dialogues"].values():
            self.assertTrue(isinstance(value, str) and value.strip())
            self.assertFalse(any(c in value for c in "\\r\\n\\t"))

    def test_previous_scenes_unchanged(self):
        old = load("story/story_main_selection_ru_v082.json")
        new = load("story/story_main_selection_ru_v083.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (75, 76))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4492)
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_manifest_and_index(self):
        a = load("reports/CHAPTER_4_STAGE_4-8_AFTER_SOURCE_AUDIT_v083.json")["alignment"]
        self.assertEqual((a["cn_named"], a["en_named"], a["ru_complete_text_entries"]), (67, 67, 67))
        self.assertEqual((a["source_non_dialogue_commands_cn"], a["source_non_dialogue_commands_en"]), (105, 105))
        self.assertTrue(a["cn_en_text_source_line_positions_equal"] and a["cn_en_non_dialogue_commands_equal"])
        m = load("chronology/CHRONOLOGY_MANIFEST_v083.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-09_beg.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (76, 4476))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (16, 945, 16))
        q = load("reports/QA_MAIN_STORY_v083.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"]), (67, 76))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v083.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-08_end.txt\\tfirst_draft_complete\\t67\\t0\\t67", idx)

    def test_preview_preserves_commands(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        lines = ['[HEADER(key="title_test")]\\n', '[Background(image="bg_cher_2")]\\n']
        for i in range(1, 68):
            lines.append('[Character(name="char_test")]\\n')
            lines.append('[name="Amiya"]   EN dialogue ' + str(i) + '\\n')
        lines.append('[Image]\\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 67)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn(cfg["dialogues"]["67"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
