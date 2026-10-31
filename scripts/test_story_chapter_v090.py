# coding: utf-8
"""Regression tests for main story 5-1 before battle, v0.90."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-01_beg.txt"
NEW = "story/story_chapter_5_stage_5-1_before_ru_v090.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter51BeforeV090(unittest.TestCase):
    def test_complete_source_counts_and_hashes(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (39, 38, 1))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 40))))
        self.assertEqual(cfg["cn_git_blob_sha1"], "20d598fa2831e101fed33ab0589e410d2cde0108")
        self.assertEqual(cfg["en_git_blob_sha1"], "88a970f8a856508e1d885c2178acaeea69f01109")
        self.assertEqual(cfg["dialogues"]["14"], "Плеск —")
        for text in cfg["dialogues"].values():
            self.assertTrue(text.strip())
            self.assertFalse(any(c in text for c in "\\r\\n\\t"))

    def test_selection_preserves_previous_80(self):
        old = load("story/story_main_selection_ru_v089.json")
        new = load("story/story_main_selection_ru_v090.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (80, 81))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for k, v in old["files"].items():
            self.assertEqual(v, new["files"][k])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 4925)

    def test_manifest_audit_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v090.json")
        a = load("reports/CHAPTER_5_STAGE_5-1_BEFORE_SOURCE_AUDIT_v090.json")
        q = load("reports/QA_MAIN_STORY_v090.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_05-01_end.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (81, 4907))
        self.assertEqual((q["new_named_ru"], q["new_unnamed_ru"], q["completed_story_files"]), (38, 1, 81))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (68, 68))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v090.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-01_beg.txt\\tfirst_draft_complete\\t38\\t1\\t39", idx)

    def test_local_preview_preserves_commands_and_bare_sound(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertEqual(ap.SPEAKER_RU["Swire"], "Свайр")
        source = '[HEADER(key="title_test")] sample\\n' + ''.join(
            ('*splash*—\\n' if i == 14 else '[name="Swire"]   EN line ' + str(i) + '\\n')
            for i in range(1, 40)
        ) + '[Image]\\n'
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"], include_bare=True)
        self.assertEqual(count, 39)
        self.assertIn("Плеск —\\n", patched.decode())
        self.assertIn('[name="Свайр"]   ' + cfg["dialogues"]["1"], patched.decode())
        self.assertIn('[Image]\\n', patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), dict(list(cfg["dialogues"].items())[:-1]), include_bare=True)

if __name__ == "__main__":
    unittest.main()
