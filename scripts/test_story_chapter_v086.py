# coding: utf-8
"""Regression tests for chapter 4-10 before battle (v0.86)."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-10_beg.txt"
NEW = "story/story_chapter_4_stage_4-10_before_ru_v086.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter410BeforeV086(unittest.TestCase):
    def test_source_pins_and_all_text(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (108, 108, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 109))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (
            "004e9d1f063be08ee4fa7a3ef66d5abbeb574003",
            "6e72bb8320db4bb033c4a6b27c8084d1c6d9f890"))
        self.assertEqual([len(cfg["decisions"][str(i)]) for i in (1, 2)], [3, 1])
        self.assertIn("принцесса йети", cfg["dialogues"]["16"])
        self.assertIn("кристаллов льда", cfg["dialogues"]["102"])
        for s in cfg["dialogues"].values():
            self.assertTrue(isinstance(s, str) and s.strip())
            self.assertFalse(any(c in s for c in "\r\n\t"))

    def test_selection_unchanged_previous_scenes(self):
        old = load("story/story_main_selection_ru_v085.json")
        new = load("story/story_main_selection_ru_v086.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (78, 79))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4729)
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_manifest_index(self):
        a = load("reports/CHAPTER_4_STAGE_4-10_BEFORE_SOURCE_AUDIT_v086.json")["alignment"]
        self.assertEqual((a["cn_named"], a["en_named"], a["ru_complete_text_entries"]), (108, 108, 108))
        self.assertEqual((a["source_non_dialogue_commands_cn"], a["source_non_dialogue_commands_en"]), (97, 97))
        self.assertEqual(a["cn_en_decision_option_counts"], [3, 1])
        self.assertTrue(a["cn_en_text_source_line_positions_equal"] and a["cn_en_non_dialogue_commands_equal_excluding_decision_text"])
        m = load("chronology/CHRONOLOGY_MANIFEST_v086.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-10_end.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (79, 4713))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (19, 1182, 16))
        q = load("reports/QA_MAIN_STORY_v086.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"], q["source_choice_options"]), (108, 79, 4))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v086.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-10_beg.txt\tfirst_draft_complete\t108\t0\t108", idx)

    def test_preview_preserves_commands_choices(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        lines = ['[HEADER(key="title_test")]\n', '[Background(image="bg_cher_6")]\n']
        for i in range(1, 109):
            lines.append('[Character(name="char_test")]\n')
            lines.append('[name="FrostNova"]   EN dialogue ' + str(i) + '\n')
            if i == 35:
                lines.append('[Decision(options="Way ahead of you!;(Nod);Affirmative!", values="1;2;3")]\n')
                lines.append('[Predicate(references="1;2;3")]\n')
            if i == 108:
                lines.append('[Decision(options="Rhodes Island, we are going all out!", values="1")]\n')
                lines.append('[Predicate(references="1")]\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"], ru_choices=cfg["decisions"])
        self.assertEqual(count, 108)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image", "[Predicate")):
                self.assertEqual(x, y)
            if x.startswith("[Decision"):
                self.assertEqual(re.sub(r'options="[^"]*"', 'options=""', x), re.sub(r'options="[^"]*"', 'options=""', y))
        self.assertIn('[name="ФростНова"]', patched.decode())
        self.assertIn(cfg["dialogues"]["108"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]), ru_choices=cfg["decisions"])

if __name__ == "__main__":
    unittest.main()
