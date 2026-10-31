# coding: utf-8
"""Regression checks for complete chapter 4-10 after-battle translation v0.89."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-10_end.txt"
OLD = "story/story_chapter_4_stage_4-10_after_partial_ru_v088.json"
NEW = "story/story_chapter_4_stage_4-10_after_ru_v089.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter410AfterCompleteV089(unittest.TestCase):
    def test_complete_and_old_translations_unchanged(self):
        old, new = load(OLD), load(NEW)
        cfg = new["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (157, 156, 1))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 158))))
        self.assertEqual({k: cfg["dialogues"][k] for k in old["dialogues"]}, old["dialogues"])
        self.assertEqual((cfg["cn_git_blob_sha1"], cfg["en_git_blob_sha1"]), (old["source"]["cn_git_blob_sha1"], old["source"]["en_git_blob_sha1"]))
        self.assertIn("Патриот", cfg["dialogues"]["152"])
        self.assertIn("символ Воссоединения", cfg["dialogues"]["108"])
        for s in cfg["dialogues"].values():
            self.assertTrue(isinstance(s, str) and s.strip())
            self.assertFalse(any(c in s for c in "\r\n\t"))

    def test_selection_preserves_79_previous_files(self):
        old, new = load("story/story_main_selection_ru_v086.json"), load("story/story_main_selection_ru_v089.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (79, 80))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 4886)
        for k, v in old["files"].items():
            self.assertEqual(new["files"][k], v)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_manifest_audit_index_qa(self):
        m, a, q = (load(p) for p in (
            "chronology/CHRONOLOGY_MANIFEST_v089.json",
            "reports/CHAPTER_4_STAGE_4-10_AFTER_SOURCE_AUDIT_v089.json",
            "reports/QA_MAIN_STORY_v089.json"))
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (80, 4869))
        self.assertEqual((t["main_story_chapter_4_files"], t["main_story_chapter_4_named_ru_lines"], t["main_story_chapter_4_unnamed_ru_lines"]), (20, 1338, 17))
        self.assertEqual(m["next_file"], "obt/main/level_main_05-01_beg.txt")
        self.assertEqual((q["new_named_ru"], q["new_unnamed_ru"], q["new_text_entries"]), (70, 1, 71))
        self.assertEqual((q["completed_story_files"], q["completed_story_text_entries_including_unnamed"]), (80, 4886))
        self.assertTrue(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        x = a["alignment"]
        self.assertEqual((x["cn_named"], x["en_named"], x["cn_unnamed"], x["en_unnamed"]), (156, 156, 1, 1))
        self.assertEqual((x["cn_non_dialogue_commands"], x["en_non_dialogue_commands"]), (210, 210))
        self.assertTrue(x["cn_en_text_source_line_positions_equal"] and x["cn_en_non_dialogue_commands_equal"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v089.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-10_end.txt\tfirst_draft_complete\t156\t1\t157", idx)

    def test_local_preview_preserves_commands_and_unnamed_speaker(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        lines = ['[HEADER(key="title_test")]\n', '[Background(image="bg_cher_6")]\n']
        for i in range(1, 158):
            lines.append('[Character(name="char_test")]\n')
            name = "" if i == 147 else "FrostNova"
            lines.append('[name="' + name + '"]   EN dialogue ' + str(i) + '\n')
        lines.append('[Image]\n')
        source = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(source, cfg["dialogues"])
        self.assertEqual(count, 157)
        before, after = source.decode().splitlines(), patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith(("[HEADER", "[Background", "[Character", "[Image")):
                self.assertEqual(x, y)
        self.assertIn('[name=""]   ' + cfg["dialogues"]["147"], patched.decode())
        self.assertIn(cfg["dialogues"]["157"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source, dict(list(cfg["dialogues"].items())[:-1]))

if __name__ == "__main__":
    unittest.main()
