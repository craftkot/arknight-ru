# coding: utf-8
"""Regression checks for Arknights RU v1.00: main story 5-6 after battle."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-06_end.txt"
NEW = "story/story_chapter_5_stage_5-6_after_ru_v100.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter56AfterV100(unittest.TestCase):
    def test_complete_and_hashes(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (36, 36, 0))
        self.assertEqual(set(cfg["dialogues"]), {str(i) for i in range(1, 37)})
        self.assertTrue(all(v.strip() and not any(c in v for c in "\r\n\t") for v in cfg["dialogues"].values()))
        self.assertEqual(cfg["cn_git_blob_sha1"], "3cbc5dcddaf63bef2a2f2adc9e8c63b5c8c8f470")
        self.assertEqual(cfg["en_git_blob_sha1"], "d865c31782838546087dd83faf3d0120b880a653")
        self.assertIn("Паси-Плаза", cfg["dialogues"]["11"])
        self.assertIn("Фал", cfg["dialogues"]["23"])
        self.assertIn("взрывчатки", cfg["dialogues"]["29"])

    def test_selection_preserves_previous_scenes(self):
        old = load("story/story_main_selection_ru_v099.json")
        new = load("story/story_main_selection_ru_v100.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (89, 90))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 5418)

    def test_audit_manifest_index_and_qa(self):
        audit = load("reports/CHAPTER_5_STAGE_5-6_AFTER_SOURCE_AUDIT_v100.json")
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v100.json")
        qa = load("reports/QA_MAIN_STORY_v100.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (36, 36))
        self.assertEqual((audit["alignment"]["cn_non_dialogue_commands"], audit["alignment"]["en_non_dialogue_commands"]), (64, 64))
        self.assertTrue(audit["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(manifest["next_file"], "obt/main/level_main_05-07_beg.txt")
        self.assertEqual((manifest["translation_integrity"]["main_story_files"], manifest["translation_integrity"]["main_story_named_ru_lines"]), (90, 5387))
        self.assertEqual((qa["new_text_entries"], qa["source_text_entries_remaining"], qa["completed_story_files"]), (36, 0, 90))
        self.assertIn("level_main_05-06_end.txt\tfirst_draft_complete\t36\t0\t36", (ROOT / "story/CHAPTER_5_INDEX_v100.tsv").read_text(encoding="utf-8"))

    def test_preview_preserves_commands_and_speaker_labels(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        source_lines = ['[HEADER(key="title_test")] sample', '[Image]']
        for i in range(1, 37):
            speaker = "Hoshiguma" if i <= 6 else ("Reunion Caster" if i <= 28 else "Ch'en")
            source_lines.append('[name="' + speaker + '"]  EN line ' + str(i))
        source_lines.append('[Dialog]')
        source = "\n".join(source_lines) + "\n"
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"])
        result = patched.decode("utf-8").splitlines()
        self.assertEqual(count, 36)
        self.assertEqual(result[:2], source_lines[:2])
        self.assertEqual(result[-1], "[Dialog]")
        self.assertEqual(result[2], '[name="Хосигума"]  ' + cfg["dialogues"]["1"])
        self.assertEqual(result[-2], '[name="Чэнь"]  ' + cfg["dialogues"]["36"])
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), {k:v for k,v in cfg["dialogues"].items() if k != "36"})

if __name__ == "__main__":
    unittest.main()
