# coding: utf-8
"""Regression tests for complete chapter 4-5 after battle, v0.77."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-05_end.txt"
NEW = "story/story_chapter_4_stage_4-5_after_ru_v077.json"
CN = "2e9bba7a2cf6f4f551fd32da271ecec535c795d9"
EN = "498a4ac51797e711761b22858660a0949e0c8953"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter45AfterV077(unittest.TestCase):
    def test_complete_37_dialogues_and_pinned_sources(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.77")
        self.assertEqual(set(doc["files"]), {REL})
        cfg = doc["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (37, 37, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 38))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertNotIn("decisions", cfg)
        for line in cfg["dialogues"].values():
            self.assertIsInstance(line, str)
            self.assertTrue(line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
        self.assertIn("отделившегося района", cfg["dialogues"]["10"])
        self.assertIn("Метеорит", cfg["dialogues"]["24"])

    def test_previous_69_files_unchanged(self):
        old = load("story/story_main_selection_ru_v076.json")
        new = load("story/story_main_selection_ru_v077.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (69, 70))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4197)
        for key, cfg in old["files"].items():
            self.assertEqual(new["files"][key], cfg)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_manifest_qa_and_index(self):
        a = load("reports/CHAPTER_4_STAGE_4-5_AFTER_SOURCE_AUDIT_v077.json")
        z = a["alignment"]
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"], a["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        self.assertEqual((z["cn_named"], z["en_named"], z["ru_complete_text_entries"]), (37, 37, 37))
        self.assertEqual((z["source_non_dialogue_commands_cn"], z["source_non_dialogue_commands_en"]), (33, 33))
        self.assertTrue(z["cn_en_text_source_line_positions_equal"] and z["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(z["remaining_text_entries"], 0)
        m = load("chronology/CHRONOLOGY_MANIFEST_v077.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-06_beg.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (70, 4181))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (10, 650, 16))
        q = load("reports/QA_MAIN_STORY_v077.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"]), (37, 70))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v077.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-05_end.txt\tfirst_draft_complete\t37\t0\t37", idx)

    def test_preview_keeps_all_commands(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="title_test")]\n', '[Background(image="bg_lungmen_m")]\n']
        names = ["Amiya", "Ch'en", "Kal'tsit", "Hoshiguma"]
        for i in range(1, 38):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="' + names[(i-1) % len(names)] + '"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 37)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn(cfg["dialogues"]["37"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
