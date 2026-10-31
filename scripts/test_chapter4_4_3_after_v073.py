# coding: utf-8
"""Regression checks for CN-primary main story 4-3 after battle v0.73."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-03_end.txt"
NEW = "story/story_chapter_4_stage_4-3_after_ru_v073.json"
CN = "354763e2fdb6fd20ff9aaff1402510bae8e32dcb"
EN = "b01f8d853fc1c311033ecc4ebda0fed617973fbe"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Chapter43AfterV073(unittest.TestCase):
    def test_all_73_positions_and_pinned_sources(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.73")
        self.assertEqual(set(doc["files"]), {REL})
        cfg = doc["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (73, 73, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 74))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertNotIn("decisions", cfg)
        for ru in cfg["dialogues"].values():
            self.assertIsInstance(ru, str)
            self.assertTrue(ru.strip())
            self.assertFalse(any(c in ru for c in "\r\n\t"))
        self.assertIn("Отряд йети", cfg["dialogues"]["68"])
        self.assertIn("оригиния", cfg["dialogues"]["51"])

    def test_selection_preserves_all_previous_65_files(self):
        old = load("story/story_main_selection_ru_v072.json")
        new = load("story/story_main_selection_ru_v073.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (65, 66))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 4005)
        for name, cfg in old["files"].items():
            self.assertEqual(new["files"][name], cfg)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_index_chronology_and_qa(self):
        audit = load("reports/CHAPTER_4_STAGE_4-3_AFTER_SOURCE_AUDIT_v073.json")
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        align = audit["alignment"]
        self.assertEqual((align["cn_named"], align["en_named"], align["ru_complete_text_entries"]), (73, 73, 73))
        self.assertEqual((align["source_non_dialogue_commands_cn"], align["source_non_dialogue_commands_en"]), (59, 59))
        self.assertTrue(align["cn_en_text_source_line_positions_equal"])
        self.assertTrue(align["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(align["remaining_text_entries"], 0)
        chron = load("chronology/CHRONOLOGY_MANIFEST_v073.json")
        totals = chron["translation_integrity"]
        self.assertEqual(chron["next_file"], "obt/main/level_main_04-04_beg.txt")
        self.assertEqual((totals["main_story_files"], totals["main_story_named_ru_lines"]), (66, 3989))
        self.assertEqual((totals["main_story_chapter_4_files"], totals["main_story_chapter_4_named_ru_lines"], totals["main_story_chapter_4_unnamed_ru_lines"]), (6, 458, 16))
        qa = load("reports/QA_MAIN_STORY_v073.json")
        self.assertEqual((qa["new_text_entries"], qa["completed_story_files"]), (73, 66))
        self.assertFalse(qa["in_game_test"])
        index = (ROOT / "story/CHAPTER_4_INDEX_v073.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-03_end.txt\tfirst_draft_complete\t73\t0\t73", index)

    def test_safe_preview_changes_only_dialogues(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="test")]\n', '[Background(image="bg_cher_2")]\n']
        for i in range(1, 74):
            lines.append('[Character(name="char_219_meteo_1")]\n')
            lines.append('[name="Meteorite"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"])
        self.assertEqual(count, 73)
        before = original.decode("utf-8").splitlines()
        after = patched.decode("utf-8").splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[Character", "[HEADER", "[Background", "[Image")):
                self.assertEqual(x, y)
        self.assertEqual(sum(x.startswith('[name="Метеорит"]') for x in after), 73)
        self.assertIn(cfg["dialogues"]["73"], patched.decode("utf-8"))
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, dict(list(cfg["dialogues"].items())[:-1]))


if __name__ == "__main__":
    unittest.main()
