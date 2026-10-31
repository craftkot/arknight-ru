# coding: utf-8
"""v0.80: main story 4-7 before battle, 36 lines and 4 choice options."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-07_beg.txt"
NEW = "story/story_chapter_4_stage_4-7_before_ru_v080.json"
CN = "52cfbf4038dcf89cc0d78c4140b04b549f03c3d2"
EN = "0df9a31d2800a8f0b2c1be4c60bd264231b5c418"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter47BeforeV080(unittest.TestCase):
    def test_full_36_positions_and_pinned_sources(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (36, 36, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 37))))
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertEqual([len(cfg["decisions"][str(i)]) for i in (1, 2)], [1, 3])
        self.assertIn("ледяной крошкой", cfg["dialogues"]["2"])
        self.assertIn("когти", cfg["dialogues"]["26"])
        self.assertIn("Проект Рэд", cfg["dialogues"]["31"])
        self.assertEqual(sum("{@nickname}" in s for s in cfg["dialogues"].values()), 2)
        for s in cfg["dialogues"].values():
            self.assertTrue(isinstance(s, str) and s.strip())
            self.assertFalse(any(ch in s for ch in "\r\n\t"))

    def test_previous_72_scenes_unchanged(self):
        old = load("story/story_main_selection_ru_v079.json")
        new = load("story/story_main_selection_ru_v080.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (72, 73))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 4315)
        for k, v in old["files"].items():
            self.assertEqual(new["files"][k], v)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_manifest_audit_qa_index(self):
        audit = load("reports/CHAPTER_4_STAGE_4-7_BEFORE_SOURCE_AUDIT_v080.json")
        z = audit["alignment"]
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        self.assertEqual((z["cn_named"], z["en_named"], z["ru_complete_text_entries"]), (36, 36, 36))
        self.assertEqual((z["source_non_dialogue_commands_cn"], z["source_non_dialogue_commands_en"]), (36, 36))
        self.assertTrue(z["cn_en_text_source_line_positions_equal"])
        self.assertTrue(z["cn_en_non_dialogue_commands_equal_excluding_decision_text"])
        self.assertEqual(z["decision_option_counts"], [1, 3])
        self.assertEqual(z["remaining_text_entries"], 0)
        m = load("chronology/CHRONOLOGY_MANIFEST_v080.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_04-07_end.txt")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (73, 4299))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (13, 768, 16))
        q = load("reports/QA_MAIN_STORY_v080.json")
        self.assertEqual((q["new_text_entries"], q["completed_story_files"], q["translated_choice_options"]), (36, 73, 4))
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v080.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-07_beg.txt\tfirst_draft_complete\t36\t0\t36", idx)

    def test_preview_preserves_commands_and_choice_branches(self):
        cfg = load(NEW)["files"][REL]
        lines = ['[HEADER(key="title_test")]\n', '[Character(name="char_002_amiya_1")]\n']
        for i in range(1, 37):
            name = "Amiya" if i in list(range(1, 7)) + [12, 16, 21, 23, 24, 25, 26, 27, 28, 29, 30] else "Kal'tsit"
            line = "Dr. {@nickname}" if i in (17, 20) else "EN line " + str(i)
            lines.append('[name="' + name + '"]   ' + line + '\n')
            if i == 17:
                lines.extend(['[Decision(options="I understand.", values="1")]\n', '[Predicate(references="1")]\n'])
            if i == 26:
                lines.extend(['[Decision(options="Behind us.;Retreat cut off.;They hate us.", values="1;2;3")]\n', '[Predicate(references="1;2;3")]\n'])
        lines.append('[Image]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, cfg["dialogues"], ru_choices=cfg["decisions"])
        self.assertEqual(count, 36)
        before, after = original.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for a, b in zip(before, after):
            if a.startswith(("[Character", "[HEADER", "[Predicate", "[Image")):
                self.assertEqual(a, b)
            if a.startswith("[Decision"):
                self.assertEqual(a.split(', values="')[1], b.split(', values="')[1])
        self.assertIn("Путь к отступлению… отрезан.", patched.decode())
        self.assertIn("Доктор {@nickname}", patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, cfg["dialogues"], ru_choices={"1": ["Понятно."]})

if __name__ == "__main__":
    unittest.main()
