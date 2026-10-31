# coding: utf-8
"""Regression tests for chapter 4-8 before battle (v0.82)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-08_beg.txt"
NEW = "story/story_chapter_4_stage_4-8_before_ru_v082.json"

def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

class Chapter48BeforeV082(unittest.TestCase):
    def test_complete_and_source_pins(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (70, 70, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 71))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), ("ec4e13901a60966766c1703324a90700a484bfac", "87773fa0b60a4ad3eae8ef5e63bd92d19bc6b1e8"))
        self.assertIn("довесок", cfg["dialogues"]["49"])
        self.assertIn("Йети", cfg["dialogues"]["53"])
        for s in cfg["dialogues"].values():
            self.assertTrue(isinstance(s, str) and s.strip())
            self.assertFalse(any(c in s for c in "\r\n\t"))

    def test_previous_scenes_unchanged(self):
        old = load("story/story_main_selection_ru_v081.json")
        new = load("story/story_main_selection_ru_v082.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (74, 75))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4425)
        for k, v in old["files"].items():
            self.assertEqual(new["files"][k], v)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_and_manifest(self):
        a = load("reports/CHAPTER_4_STAGE_4-8_BEFORE_SOURCE_AUDIT_v082.json")["alignment"]
        self.assertEqual((a["cn_named"], a["en_named"], a["ru_complete_text_entries"]), (70, 70, 70))
        self.assertEqual((a["source_non_dialogue_commands_cn"], a["source_non_dialogue_commands_en"]), (76, 76))
        self.assertTrue(a["cn_en_text_source_line_positions_equal"] and a["cn_en_non_dialogue_commands_equal"])
        m = load("chronology/CHRONOLOGY_MANIFEST_v082.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-08_end.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (75, 4409))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (15, 878, 16))
        q = load("reports/QA_MAIN_STORY_v082.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"]), (70, 75))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v082.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-08_beg.txt\tfirst_draft_complete\t70\t0\t70", idx)

    def test_preview_preserves_commands(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="title_test")]\n', '[Background(image="bg_cher_2")]\n']
        for i in range(1, 71):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="Amiya"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 70)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn(cfg["dialogues"]["70"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
