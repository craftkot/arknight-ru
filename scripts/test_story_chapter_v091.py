# coding: utf-8
"""Regression tests for main story 5-1 after battle, v0.91."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-01_end.txt"
NEW = "story/story_chapter_5_stage_5-1_after_ru_v091.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter51AfterV091(unittest.TestCase):
    def test_complete_source_counts_and_hashes(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (27, 25, 2))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 28))))
        self.assertEqual(cfg["cn_git_blob_sha1"], "6bf6e08161a4babf1c56439f7b05c0a51bd4bd77")
        self.assertEqual(cfg["en_git_blob_sha1"], "e1616969e600141b0fedaad27012faa1080d7a2a")
        self.assertIn("07:55", cfg["dialogues"]["1"])
        self.assertIn("Лок-Тай-Чау", cfg["dialogues"]["2"])
        for value in cfg["dialogues"].values():
            self.assertTrue(value.strip())
            self.assertFalse(any(ch in value for ch in "\\r\\n\\t"))

    def test_selection_preserves_previous_81(self):
        old = load("story/story_main_selection_ru_v090.json")
        new = load("story/story_main_selection_ru_v091.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (81, 82))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for k, v in old["files"].items():
            self.assertEqual(v, new["files"][k])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 4952)

    def test_manifest_audit_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v091.json")
        a = load("reports/CHAPTER_5_STAGE_5-1_AFTER_SOURCE_AUDIT_v091.json")
        q = load("reports/QA_MAIN_STORY_v091.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_05-02_beg.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (82, 4932))
        self.assertEqual((q["new_named_ru"], q["new_unnamed_ru"], q["completed_story_files"]), (25, 2, 82))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (25, 25))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v091.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-01_end.txt\\tfirst_draft_complete\\t25\\t2\\t27", idx)

    def test_local_preview_preserves_commands_and_unnamed_captions(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertEqual(ap.SPEAKER_RU["Swire"], "Свайр")
        source = '[HEADER(key="title_test")] sample\\n' + ''.join(
            ('[name=""]   EN caption ' + str(i) + '\\n' if i <= 2 else '[name="Swire"]   EN line ' + str(i) + '\\n')
            for i in range(1, 28)
        ) + '[Image]\\n'
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"], include_bare=True)
        self.assertEqual(count, 27)
        self.assertIn('[name=""]   ' + cfg["dialogues"]["1"], patched.decode())
        self.assertIn('[name="Свайр"]   ' + cfg["dialogues"]["3"], patched.decode())
        self.assertIn('[Image]\\n', patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), dict(list(cfg["dialogues"].items())[:-1]), include_bare=True)

if __name__ == "__main__":
    unittest.main()
