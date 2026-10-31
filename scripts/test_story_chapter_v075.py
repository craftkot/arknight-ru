# coding: utf-8
"""Regression checks for CN-primary chapter 4-4 after battle v0.75."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-04_end.txt"
NEW = "story/story_chapter_4_stage_4-4_after_ru_v075.json"
CN = "733375fbdec770566efaaefadca1b758eb56d00f"
EN = "42dadbb654c2328693c5ba0e90bb63192b6de71a"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Chapter44AfterV075(unittest.TestCase):
    def test_all_51_dialogues_and_source_pins(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.75")
        self.assertEqual(set(doc["files"]), {REL})
        cfg = doc["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (51, 51, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 52))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertNotIn("decisions", cfg)
        for line in cfg["dialogues"].values():
            self.assertIsInstance(line, str)
            self.assertTrue(line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
        self.assertIn("йети", cfg["dialogues"]["38"].lower())
        self.assertIn("отделившийся район", cfg["dialogues"]["51"])

    def test_selection_preserves_all_67_previous_files(self):
        old = load("story/story_main_selection_ru_v074.json")
        new = load("story/story_main_selection_ru_v075.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (67, 68))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 4134)
        for name, cfg in old["files"].items():
            self.assertEqual(new["files"][name], cfg)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_index_manifest_and_qa(self):
        audit = load("reports/CHAPTER_4_STAGE_4-4_AFTER_SOURCE_AUDIT_v075.json")
        align = audit["alignment"]
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        self.assertEqual((align["cn_named"], align["en_named"], align["ru_complete_text_entries"]), (51, 51, 51))
        self.assertEqual((align["source_non_dialogue_commands_cn"], align["source_non_dialogue_commands_en"]), (44, 44))
        self.assertTrue(align["cn_en_text_source_line_positions_equal"])
        self.assertTrue(align["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(align["remaining_text_entries"], 0)
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v075.json")
        totals = manifest["translation_integrity"]
        self.assertEqual(manifest["next_file"], "obt/main/level_main_04-05_beg.txt")
        self.assertEqual((totals["main_story_files"], totals["main_story_named_ru_lines"]), (68, 4118))
        self.assertEqual((totals["main_story_chapter_4_files"], totals["main_story_chapter_4_named_ru_lines"], totals["main_story_chapter_4_unnamed_ru_lines"]), (8, 587, 16))
        qa = load("reports/QA_MAIN_STORY_v075.json")
        self.assertEqual((qa["new_text_entries"], qa["completed_story_files"]), (51, 68))
        self.assertFalse(qa["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v075.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-04_end.txt\tfirst_draft_complete\t51\t0\t51", idx)

    def test_safe_preview_preserves_commands_and_header(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="test")]\n', '[Background(image="bg_cher_2")]\n']
        names = ["Frostleaf", "Jessica", "Meteorite", "Mephisto", "Reunion Member"]
        for i in range(1, 52):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="' + names[(i - 1) % len(names)] + '"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 51)
        before = original.decode().splitlines()
        after = patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn(cfg["dialogues"]["51"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))


if __name__ == "__main__":
    unittest.main()
