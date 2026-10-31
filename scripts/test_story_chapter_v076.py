# coding: utf-8
"""Regression checks for chapter 4-5 before battle v0.76."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap
REL = "obt/main/level_main_04-05_beg.txt"
NEW = "story/story_chapter_4_stage_4-5_before_ru_v076.json"
CN = "00d953691ae6e3be350bfbf4739643ea98753d7b"
EN = "3b86d6df9bf621994e580f747924630f0f450845"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter45BeforeV076(unittest.TestCase):
    def test_all_26_dialogues_and_source_pins(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.76")
        self.assertEqual(set(doc["files"]), {REL})
        cfg = doc["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (26, 26, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 27))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertNotIn("decisions", cfg)
        for line in cfg["dialogues"].values():
            self.assertTrue(isinstance(line, str) and line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
        self.assertIn("Фростлиф", cfg["dialogues"]["1"])
        self.assertIn("Гвардию", cfg["dialogues"]["23"])

    def test_selection_preserves_previous_68(self):
        old = load("story/story_main_selection_ru_v075.json")
        new = load("story/story_main_selection_ru_v076.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (68, 69))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4160)
        for k, v in old["files"].items():
            self.assertEqual(new["files"][k], v)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_manifest_qa_and_index(self):
        a = load("reports/CHAPTER_4_STAGE_4-5_BEFORE_SOURCE_AUDIT_v076.json")
        z = a["alignment"]
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"], a["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        self.assertEqual((z["cn_named"], z["en_named"], z["ru_complete_text_entries"]), (26, 26, 26))
        self.assertEqual((z["source_non_dialogue_commands_cn"], z["source_non_dialogue_commands_en"]), (22, 22))
        self.assertTrue(z["cn_en_text_source_line_positions_equal"] and z["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(z["remaining_text_entries"], 0)
        m = load("chronology/CHRONOLOGY_MANIFEST_v076.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-05_end.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (69, 4144))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (9, 613, 16))
        q = load("reports/QA_MAIN_STORY_v076.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"]), (26, 69))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v076.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-05_beg.txt\tfirst_draft_complete\t26\t0\t26", idx)

    def test_preview_preserves_commands(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="test")]\n', '[Background(image="bg_lungmen_m")]\n']
        names = ["Amiya", "Guard", "Ch'en", "Kal'tsit", "Hoshiguma"]
        for i in range(1, 27):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="' + names[(i - 1) % len(names)] + '"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 26)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn(cfg["dialogues"]["26"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
