# coding: utf-8
"""Regression checks for CN-primary chapter 4-4 before battle v0.74."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-04_beg.txt"
NEW = "story/story_chapter_4_stage_4-4_before_ru_v074.json"
CN = "459bb9347e3ba15ff3e148c3532fcf8401de8341"
EN = "13a5dc8c2a90e74e8b2208c9d49ef6e54b98f178"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Chapter44BeforeV074(unittest.TestCase):
    def test_all_78_dialogues_and_source_pins(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.74")
        self.assertEqual(set(doc["files"]), {REL})
        cfg = doc["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (78, 78, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 79))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertNotIn("decisions", cfg)
        for line in cfg["dialogues"].values():
            self.assertIsInstance(line, str)
            self.assertTrue(line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
        self.assertIn("Патриот", cfg["dialogues"]["56"])
        self.assertIn("заражённая", cfg["dialogues"]["33"])

    def test_selection_preserves_all_66_previous_files(self):
        old = load("story/story_main_selection_ru_v073.json")
        new = load("story/story_main_selection_ru_v074.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (66, 67))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 4083)
        for name, cfg in old["files"].items():
            self.assertEqual(new["files"][name], cfg)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_index_manifest_and_qa(self):
        audit = load("reports/CHAPTER_4_STAGE_4-4_BEFORE_SOURCE_AUDIT_v074.json")
        align = audit["alignment"]
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        self.assertEqual((align["cn_named"], align["en_named"], align["ru_complete_text_entries"]), (78, 78, 78))
        self.assertEqual((align["source_non_dialogue_commands_cn"], align["source_non_dialogue_commands_en"]), (73, 73))
        self.assertTrue(align["cn_en_text_source_line_positions_equal"])
        self.assertTrue(align["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(align["remaining_text_entries"], 0)
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v074.json")
        totals = manifest["translation_integrity"]
        self.assertEqual(manifest["next_file"], "obt/main/level_main_04-04_end.txt")
        self.assertEqual((totals["main_story_files"], totals["main_story_named_ru_lines"]), (67, 4067))
        self.assertEqual((totals["main_story_chapter_4_files"], totals["main_story_chapter_4_named_ru_lines"], totals["main_story_chapter_4_unnamed_ru_lines"]), (7, 536, 16))
        qa = load("reports/QA_MAIN_STORY_v074.json")
        self.assertEqual((qa["new_text_entries"], qa["completed_story_files"]), (78, 67))
        self.assertFalse(qa["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v074.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-04_beg.txt\tfirst_draft_complete\t78\t0\t78", idx)

    def test_safe_preview_preserves_commands_and_header(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="test")]\n', '[Background(image="bg_cher_2")]\n']
        names = ["Amiya", "Ch'en", "Hoshiguma", "Jessica", "W", "Mephisto", "Meteorite", "Frostleaf", "Reunion Member", "???"]
        for i in range(1, 79):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="' + names[(i - 1) % len(names)] + '"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 78)
        before = original.decode().splitlines()
        after = patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn(cfg["dialogues"]["78"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))


if __name__ == "__main__":
    unittest.main()
