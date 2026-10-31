# coding: utf-8
"""Regression checks for 4-6 after battle, v0.79."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-06_end.txt"
NEW = "story/story_chapter_4_stage_4-6_after_ru_v079.json"
CN = "b415c977314118c00eb5e30a96d9d74415d3c6a0"
EN = "d623d010b680404cdb40097260a6ccabed9fc9c8"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter46AfterV079(unittest.TestCase):
    def test_complete_and_pinned_sources(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (40, 40, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 41))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        for line in cfg["dialogues"].values():
            self.assertTrue(isinstance(line, str) and line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
        self.assertIn("оригиния", cfg["dialogues"]["10"])
        self.assertIn("некроз", cfg["dialogues"]["37"])
        self.assertIn("обморожения", cfg["dialogues"]["40"])

    def test_selection_preserves_previous_71(self):
        old = load("story/story_main_selection_ru_v078.json")
        new = load("story/story_main_selection_ru_v079.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (71, 72))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4279)
        for k, val in old["files"].items():
            self.assertEqual(new["files"][k], val)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_manifest_qa_index(self):
        a = load("reports/CHAPTER_4_STAGE_4-6_AFTER_SOURCE_AUDIT_v079.json")
        z = a["alignment"]
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"], a["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        self.assertEqual((z["cn_named"], z["en_named"], z["ru_complete_text_entries"]), (40, 40, 40))
        self.assertEqual((z["source_non_dialogue_commands_cn"], z["source_non_dialogue_commands_en"]), (39, 39))
        self.assertTrue(z["cn_en_text_source_line_positions_equal"] and z["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(z["remaining_text_entries"], 0)
        m = load("chronology/CHRONOLOGY_MANIFEST_v079.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-07_beg.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (72, 4263))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (12, 732, 16))
        q = load("reports/QA_MAIN_STORY_v079.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"]), (40, 72))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v079.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-06_end.txt\tfirst_draft_complete\t40\t0\t40", idx)

    def test_preview_preserves_commands(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="title_test")]\n', '[Background(image="bg_cher_2")]\n']
        for i in range(1, 41):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="Amiya"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 40)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertIn(cfg["dialogues"]["37"], patched.decode())
        self.assertIn(cfg["dialogues"]["40"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
