# coding: utf-8
"""Regression tests for main story 5-3 after battle, v0.95."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-03_end.txt"
NEW = "story/story_chapter_5_stage_5-3_after_ru_v095.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter53AfterV095(unittest.TestCase):
    def test_complete_counts_hashes_and_meaning(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (95, 95, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 96))))
        self.assertEqual(cfg["cn_git_blob_sha1"], "75172bb631b20d4f3497228bfb4e0033c332fc52")
        self.assertEqual(cfg["en_git_blob_sha1"], "6f6259b98075841bf0e37a1c14afc2bf9baf5c7c")
        self.assertIn("Фал", cfg["dialogues"]["76"])
        self.assertIn("Рёв", cfg["dialogues"]["31"])
        self.assertIn("Хання", cfg["dialogues"]["12"])
        self.assertEqual(cfg["dialogues"]["95"], "И я — на вашей.")
        self.assertTrue(all(v.strip() and not any(c in v for c in "\\r\\n\\t") for v in cfg["dialogues"].values()))

    def test_selection_preserves_previous_85(self):
        old = load("story/story_main_selection_ru_v094.json")
        new = load("story/story_main_selection_ru_v095.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (85, 86))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 5228)

    def test_manifest_audit_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v095.json")
        a = load("reports/CHAPTER_5_STAGE_5-3_AFTER_SOURCE_AUDIT_v095.json")
        q = load("reports/QA_MAIN_STORY_v095.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_05-04_beg.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (86, 5205))
        self.assertEqual((q["new_named_ru"], q["new_unnamed_ru"], q["completed_story_files"]), (95, 0, 86))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (111, 111))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v095.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-03_end.txt\\tfirst_draft_complete\\t95\\t0\\t95", idx)

    def test_preview_preserves_commands_and_names(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertEqual(ap.SPEAKER_RU["Informant"], "Осведомитель")
        source = '[HEADER(key="title_test")] sample\\n' + ''.join(
            ('[name="Informant"]  ' if i in (44, 45, 46) else '[name="Ch\\'en"]  ') + "EN line " + str(i) + "\\n"
            for i in range(1, 96)
        ) + '[Image]\\n'
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"])
        self.assertEqual(count, 95)
        self.assertIn('[Image]\\n', patched.decode())
        self.assertIn('[name="Осведомитель"]  ' + cfg["dialogues"]["45"], patched.decode())
        self.assertIn('[name="Чэнь"]  ' + cfg["dialogues"]["1"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
