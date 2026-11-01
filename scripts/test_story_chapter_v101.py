# coding: utf-8
"""Regression checks for Arknights RU v1.01: main story 5-7 before battle."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-07_beg.txt"
NEW = "story/story_chapter_5_stage_5-7_before_ru_v101.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter57BeforeV101(unittest.TestCase):
    def test_complete_and_source_pins(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (48, 48, 0))
        self.assertEqual(set(cfg["dialogues"]), {str(i) for i in range(1, 49)})
        self.assertTrue(all(v.strip() and not any(c in v for c in "\r\n\t") for v in cfg["dialogues"].values()))
        self.assertEqual(cfg["cn_git_blob_sha1"], "3a6877257a6f7ffac69a34236a88f27bb04dd7c4")
        self.assertEqual(cfg["en_git_blob_sha1"], "2c5d9cd2b6fa0acc6452f60c4fb834ef3a172436")
        self.assertIn("Амию", cfg["dialogues"]["40"])
        self.assertIn("всё больше людей", cfg["dialogues"]["42"])
        self.assertIn("Мук-Во", cfg["dialogues"]["36"])

    def test_selection_preserves_previous_scenes(self):
        old = load("story/story_main_selection_ru_v100.json")
        new = load("story/story_main_selection_ru_v101.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (90, 91))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 5466)

    def test_audit_manifest_index_and_qa(self):
        audit = load("reports/CHAPTER_5_STAGE_5-7_BEFORE_SOURCE_AUDIT_v101.json")
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v101.json")
        qa = load("reports/QA_MAIN_STORY_v101.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (48, 48))
        self.assertEqual((audit["alignment"]["cn_non_dialogue_commands"], audit["alignment"]["en_non_dialogue_commands"]), (60, 60))
        self.assertTrue(audit["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(manifest["next_file"], "obt/main/level_main_05-07_end.txt")
        self.assertEqual((manifest["translation_integrity"]["main_story_files"], manifest["translation_integrity"]["main_story_named_ru_lines"]), (91, 5435))
        self.assertEqual((qa["new_text_entries"], qa["source_text_entries_remaining"], qa["completed_story_files"]), (48, 0, 91))
        self.assertIn("level_main_05-07_beg.txt\tfirst_draft_complete\t48\t0\t48", (ROOT / "story/CHAPTER_5_INDEX_v101.tsv").read_text(encoding="utf-8"))

    def test_preview_preserves_commands_and_speaker_labels(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        source_lines = ['[HEADER(key="title_test")] sample', '[Image]']
        for i in range(1, 49):
            speaker = "Ch'en" if i % 2 else "Hoshiguma"
            source_lines.append('[name="' + speaker + '"]  EN line ' + str(i))
        source_lines.append('[Dialog]')
        source = "\n".join(source_lines) + "\n"
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"])
        result = patched.decode("utf-8").splitlines()
        self.assertEqual(count, 48)
        self.assertEqual(result[:2], source_lines[:2])
        self.assertEqual(result[-1], "[Dialog]")
        self.assertEqual(result[2], '[name="Чэнь"]  ' + cfg["dialogues"]["1"])
        self.assertEqual(result[-2], '[name="Хосигума"]  ' + cfg["dialogues"]["48"])
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), {k: v for k, v in cfg["dialogues"].items() if k != "48"})

if __name__ == "__main__":
    unittest.main()
