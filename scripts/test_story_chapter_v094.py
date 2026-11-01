# coding: utf-8
"""Regression tests for main story 5-3 before battle, v0.94."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-03_beg.txt"
NEW = "story/story_chapter_5_stage_5-3_before_ru_v094.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter53BeforeV094(unittest.TestCase):
    def test_counts_hashes_and_translation(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (29, 27, 2))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 30))))
        self.assertEqual(cfg["cn_git_blob_sha1"], "bbe0b6e49e57146f9d221d6e968783735aae2dfc")
        self.assertEqual(cfg["en_git_blob_sha1"], "5a36a518ae389f9604f22ca7e3a5bd5a8f4f5211")
        self.assertIn("Только три минуты", cfg["dialogues"]["28"])
        self.assertIn("Мук-Во", cfg["dialogues"]["2"])
        self.assertTrue(all(v.strip() and not any(c in v for c in "\r\n\t") for v in cfg["dialogues"].values()))

    def test_selection_preserves_previous_84(self):
        old = load("story/story_main_selection_ru_v093.json")
        new = load("story/story_main_selection_ru_v094.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (84, 85))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 5133)

    def test_manifest_audit_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v094.json")
        a = load("reports/CHAPTER_5_STAGE_5-3_BEFORE_SOURCE_AUDIT_v094.json")
        q = load("reports/QA_MAIN_STORY_v094.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_05-03_end.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (85, 5110))
        self.assertEqual((q["new_named_ru"], q["new_unnamed_ru"], q["completed_story_files"]), (27, 2, 85))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (35, 35))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v094.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-03_beg.txt\tfirst_draft_complete\t27\t2\t29", idx)

    def test_preview_preserves_commands_and_unnamed_captions(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        source = '[HEADER(key="title_test")] 第三关（前）\n' + ''.join(
            ('[name=""]  EN caption ' if i in (1, 2) else '[name="Ch\'en"]  EN line ') + str(i) + '\n'
            for i in range(1, 30)
        ) + '[Image]\n'
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"], include_bare=True)
        self.assertEqual(count, 29)
        self.assertIn('[HEADER(key="title_test")] 第三关（前）\n', patched.decode())
        self.assertIn('[Image]\n', patched.decode())
        self.assertIn('[name=""]  ' + cfg["dialogues"]["1"], patched.decode())
        self.assertIn('[name="Чэнь"]  ' + cfg["dialogues"]["3"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), dict(list(cfg["dialogues"].items())[:-1]), include_bare=True)

if __name__ == "__main__":
    unittest.main()
