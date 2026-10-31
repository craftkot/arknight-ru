# coding: utf-8
"""Regression tests for chapter 4-9 before battle (v0.84)."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-09_beg.txt"
NEW = "story/story_chapter_4_stage_4-9_before_ru_v084.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter49BeforeV084(unittest.TestCase):
    def test_complete_source_pins_and_choices(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (68, 68, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 69))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (
            "b89e61bea834e926b5c3fe1efeee79f8663a775a",
            "b4a5ec21cfb3f530bfc0f34447f492b385c81959"))
        self.assertEqual([len(cfg["decisions"][str(i)]) for i in (1, 2, 3)], [1, 2, 1])
        self.assertIn("двигатели", cfg["dialogues"]["18"])
        self.assertIn("девять десятых", cfg["dialogues"]["53"])
        for s in cfg["dialogues"].values():
            self.assertTrue(isinstance(s, str) and s.strip())
            self.assertFalse(any(c in s for c in "\r\n\t"))

    def test_previous_scenes_unchanged(self):
        old = load("story/story_main_selection_ru_v083.json")
        new = load("story/story_main_selection_ru_v084.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (76, 77))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4560)
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_manifest_and_index(self):
        a = load("reports/CHAPTER_4_STAGE_4-9_BEFORE_SOURCE_AUDIT_v084.json")["alignment"]
        self.assertEqual((a["cn_named"], a["en_named"], a["ru_complete_text_entries"]), (68, 68, 68))
        self.assertEqual((a["source_non_dialogue_commands_cn"], a["source_non_dialogue_commands_en"]), (91, 91))
        self.assertTrue(a["cn_en_text_source_line_positions_equal"] and a["cn_en_non_dialogue_commands_equal_excluding_decision_text"])
        m = load("chronology/CHRONOLOGY_MANIFEST_v084.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-09_end.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (77, 4544))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (17, 1013, 16))
        q = load("reports/QA_MAIN_STORY_v084.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"], q["source_choice_options"]), (68, 77, 4))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v084.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-09_beg.txt\tfirst_draft_complete\t68\t0\t68", idx)

    def test_preview_preserves_commands_and_choices(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        lines = ['[HEADER(key="title_test")]\n', '[Background(image="bg_cher_2")]\n']
        for i in range(1, 69):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="Amiya"]   EN dialogue ' + str(i) + '\n')
            if i in (30, 31, 38):
                options = {30: '(Cover eyes)', 31: "Don't look!;...", 38: '(Let go)'}[i]
                values = {30: '1', 31: '1;2', 38: '1'}[i]
                lines.append('[Decision(options="' + options + '", values="' + values + '")]\n')
                lines.append('[Predicate(references="' + values + '")]\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"], ru_choices=cfg["decisions"])
        self.assertEqual(count, 68)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image", "[Predicate")):
                self.assertEqual(x, y)
            if x.startswith("[Decision"):
                self.assertEqual(re.sub(r'options="[^"]*"', 'options=""', x), re.sub(r'options="[^"]*"', 'options=""', y))
        self.assertIn(cfg["dialogues"]["68"], patched.decode())
        self.assertIn('options="Не смотри!;…", values="1;2"', patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]), ru_choices=cfg["decisions"])

if __name__ == "__main__":
    unittest.main()
