# coding: utf-8
"""Regression tests for Arknights RU v1.07, chapter 5 stage 5-9 after battle."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-09_end.txt"
NEW = "story/story_chapter_5_stage_5-9_after_ru_v107.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter59AfterV107(unittest.TestCase):
    def test_full_contiguous_source_pinned(self):
        d = load(NEW)
        c = d["files"][REL]
        self.assertEqual((c["dialogue_count"], c["named_dialogue_count"], c["unnamed_dialogue_count"]), (136, 136, 0))
        self.assertEqual(set(c["dialogues"]), {str(i) for i in range(1, 137)})
        self.assertEqual((c["cn_git_blob_sha1"], c["en_git_blob_sha1"]), ("ced45a6cd4fe5679c87cdd7ddae10fe051ef9465", "e02b0f41bbaf69d866c1ba86b73d5f361227b6fb"))
        self.assertEqual((c["source_dialogue_line_numbers"]["94"], c["source_dialogue_line_numbers"]["136"]), (226, 298))
        self.assertEqual(len(c["source_dialogue_line_numbers"]), 136)
        self.assertTrue(all(v.strip() and not any(x in v for x in "\r\n\t") for v in c["dialogues"].values()))
        self.assertIn("внезапный удар", c["dialogues"]["106"])

    def test_previous_93_unchanged_and_selection(self):
        old = load("story/story_chapter_5_stage_5-9_after_partial_ru_v106.json")
        cur = load(NEW)["files"][REL]["dialogues"]
        self.assertEqual({k: cur[k] for k in old["dialogues"]}, old["dialogues"])
        prev = load("story/story_main_selection_ru_v103.json")
        sel = load("story/story_main_selection_ru_v107.json")
        self.assertEqual((len(prev["files"]), len(sel["files"])), (93, 94))
        self.assertEqual(set(sel["files"]) - set(prev["files"]), {REL})
        for k, v in prev["files"].items():
            self.assertEqual(sel["files"][k], v)
        self.assertEqual(sel["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in sel["files"].values()), 5740)

    def test_manifest_qa_audit_index(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v107.json")
        q = load("reports/QA_MAIN_STORY_v107.json")
        a = load("reports/CHAPTER_5_STAGE_5-9_AFTER_SOURCE_AUDIT_v107.json")
        self.assertEqual((m["next_file"], m["translation_integrity"]["main_story_files"]), ("obt/main/level_main_05-10_beg.txt", 94))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"], 5740)
        self.assertEqual((q["new_text_entries"], q["completed_story_files"], q["source_text_entries_remaining"]), (43, 94, 0))
        self.assertEqual((a["alignment"]["cn_named"], a["alignment"]["en_named"]), (136, 136))
        self.assertTrue(a["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertIn("level_main_05-09_end.txt\tfirst_draft_complete\t136\t0\t136", (ROOT / "story/CHAPTER_5_INDEX_v107.tsv").read_text(encoding="utf-8"))

    def test_preview_preserves_commands_and_corrupted_speakers(self):
        c = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        special = {48: "ReUni N MemBr", 49: "ReUMmbr? N;E? OE", 51: "Mephisto's hERd", 53: "Mephisto's HeRd", 99: "Mephisto's Guard", 121: "Wei Yenwu"}
        lines = ['[Character(name="char_test")]', '[PlaySound(key="$test")]']
        for i in range(1, 137):
            name = special.get(i, "Ch'en")
            lines.append('[name="' + name + '"]  EN line ' + str(i))
        lines.append("[Dialog]")
        raw = "\n".join(lines) + "\n"
        patched, count = ap.patch_bytes(raw.encode("utf-8"), c["dialogues"])
        out = patched.decode("utf-8").splitlines()
        self.assertEqual(count, 136)
        self.assertEqual(out[:2], lines[:2])
        self.assertEqual(out[-1], "[Dialog]")
        self.assertEqual(out[100], '[name="Страж Мефисто"]  ' + c["dialogues"]["99"])
        self.assertEqual(out[122], '[name="Вэй Яньу"]  ' + c["dialogues"]["121"])
        self.assertEqual(out[49], '[name="ReUni N MemBr"]  ' + c["dialogues"]["48"])
        with self.assertRaises(ValueError):
            ap.patch_bytes(raw.encode("utf-8"), {k: v for k, v in c["dialogues"].items() if k != "136"})

if __name__ == "__main__":
    unittest.main()
