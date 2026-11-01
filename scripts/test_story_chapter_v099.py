# coding: utf-8
"""Regression checks for Arknights RU v0.99: main story 5-6 before battle."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-06_beg.txt"
NEW = "story/story_chapter_5_stage_5-6_before_ru_v099.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter56BeforeV099(unittest.TestCase):
    def test_complete_and_hashes(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (54, 54, 0))
        self.assertEqual(set(cfg["dialogues"]), {str(i) for i in range(1, 55)})
        self.assertTrue(all(v.strip() and not any(c in v for c in "\r\n\t") for v in cfg["dialogues"].values()))
        self.assertEqual(cfg["cn_git_blob_sha1"], "2671e34a7bfc23ec744fbb871919ea65dd8d9dac")
        self.assertEqual(cfg["en_git_blob_sha1"], "2f41636c370d8051f5b528c6de3918e08b3f6c41")
        self.assertIn("Паси-Плаза", cfg["dialogues"]["7"])
        self.assertIn("миллион восемьсот тысяч", cfg["dialogues"]["40"])

    def test_selection_preserves_previous_scenes(self):
        old = load("story/story_main_selection_ru_v098.json")
        new = load("story/story_main_selection_ru_v099.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (88, 89))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 5382)

    def test_audit_manifest_index_and_qa(self):
        audit = load("reports/CHAPTER_5_STAGE_5-6_BEFORE_SOURCE_AUDIT_v099.json")
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v099.json")
        qa = load("reports/QA_MAIN_STORY_v099.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (54, 54))
        self.assertEqual((audit["alignment"]["cn_non_dialogue_commands"], audit["alignment"]["en_non_dialogue_commands"]), (93, 93))
        self.assertTrue(audit["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(manifest["next_file"], "obt/main/level_main_05-06_end.txt")
        self.assertEqual((manifest["translation_integrity"]["main_story_files"], manifest["translation_integrity"]["main_story_named_ru_lines"]), (89, 5351))
        self.assertEqual((qa["new_text_entries"], qa["source_text_entries_remaining"], qa["completed_story_files"]), (54, 0, 89))
        self.assertIn("level_main_05-06_beg.txt\tfirst_draft_complete\t54\t0\t54", (ROOT / "story/CHAPTER_5_INDEX_v099.tsv").read_text(encoding="utf-8"))

    def test_preview_preserves_commands_and_speaker_labels(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        source_lines = ['[HEADER(key="title_test")] sample', '[Image]']
        for i in range(1, 55):
            source_lines.append('[name="Reunion Member"]  EN line ' + str(i) if i <= 30 else '[name="Ch\'en"]  EN line ' + str(i))
        source_lines.append('[Dialog]')
        source = "\n".join(source_lines) + "\n"
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"])
        result = patched.decode("utf-8").splitlines()
        self.assertEqual(count, 54)
        self.assertEqual(result[:2], source_lines[:2])
        self.assertEqual(result[-1], "[Dialog]")
        self.assertEqual(result[2], '[name="Боец Воссоединения"]  ' + cfg["dialogues"]["1"])
        self.assertEqual(result[-2], '[name="Чэнь"]  ' + cfg["dialogues"]["54"])
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), {k:v for k,v in cfg["dialogues"].items() if k != "54"})

if __name__ == "__main__":
    unittest.main()
