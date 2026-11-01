# coding: utf-8
"""Regression tests for main story 5-2 after battle, v0.93."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-02_end.txt"
NEW = "story/story_chapter_5_stage_5-2_after_ru_v093.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter52AfterV093(unittest.TestCase):
    def test_complete_counts_and_pinned_sources(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (67, 67, 0))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 68))))
        self.assertEqual(cfg["cn_git_blob_sha1"], "12b57140bdc7e18cbd6f58ffe7cb49b8d38d5b5d")
        self.assertEqual(cfg["en_git_blob_sha1"], "e12dd37761ad03a4e16dc77e84709e2a2b64662b")
        self.assertEqual(cfg["dialogues"]["67"], "На склад Мук-Во.")
        self.assertIn("{@nickname}", cfg["dialogues"]["11"])
        self.assertIn("{@nickname}", cfg["dialogues"]["57"])
        self.assertTrue(all(v.strip() and not any(c in v for c in "\r\n\t") for v in cfg["dialogues"].values()))

    def test_selection_preserves_previous_83(self):
        old = load("story/story_main_selection_ru_v092.json")
        new = load("story/story_main_selection_ru_v093.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (83, 84))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 5104)

    def test_manifest_audit_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v093.json")
        a = load("reports/CHAPTER_5_STAGE_5-2_AFTER_SOURCE_AUDIT_v093.json")
        q = load("reports/QA_MAIN_STORY_v093.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_05-03_beg.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (84, 5083))
        self.assertEqual((q["new_named_ru"], q["new_unnamed_ru"], q["completed_story_files"]), (67, 0, 84))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (68, 68))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v093.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-02_end.txt\tfirst_draft_complete\t67\t0\t67", idx)

    def test_preview_preserves_commands_and_inline_tokens(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        source = '[HEADER(key="title_test")] sample\n' + ''.join(
            '[name="Ch\'en"]   EN line ' + str(i) + (' {@nickname}' if i in (11, 57) else '') + '\n'
            for i in range(1, 68)
        ) + '[Image]\n'
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"])
        self.assertEqual(count, 67)
        self.assertIn('[Image]\n', patched.decode())
        self.assertIn('[name="Чэнь"]   ' + cfg["dialogues"]["1"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
