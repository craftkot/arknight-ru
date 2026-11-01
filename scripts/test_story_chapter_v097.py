# coding: utf-8
"""Regression checks for completed main story 5-4 before battle, v0.97."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-04_beg.txt"
NEW = "story/story_chapter_5_stage_5-4_before_ru_v097.json"

def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

class Chapter54BeforeV097(unittest.TestCase):
    def test_complete_and_previous_lines_preserved(self):
        cfg = load(NEW)["files"][REL]
        previous = load("story/story_chapter_5_stage_5-4_before_partial_ru_v096.json")
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (41, 41, 0))
        self.assertEqual(set(cfg["dialogues"]), {str(i) for i in range(1, 42)})
        self.assertEqual({k: cfg["dialogues"][k] for k in previous["dialogues"]}, previous["dialogues"])
        self.assertTrue(all(v.strip() and not any(c in v for c in "\r\n\t") for v in cfg["dialogues"].values()))
        self.assertIn("радиостанцию", cfg["dialogues"]["39"])

    def test_selection_preserves_86_scenes(self):
        old = load("story/story_main_selection_ru_v095.json")
        new = load("story/story_main_selection_ru_v097.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (86, 87))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for k, v in old["files"].items():
            self.assertEqual(new["files"][k], v)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 5269)

    def test_audit_manifest_index_and_qa(self):
        cfg = load(NEW)["files"][REL]
        audit = load("reports/CHAPTER_5_STAGE_5-4_BEFORE_SOURCE_AUDIT_v097.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v097.json")
        qa = load("reports/QA_MAIN_STORY_v097.json")
        self.assertEqual(cfg["cn_git_blob_sha1"], "54a9f0ea3102c4a0918bee64fed05f5131f97cfd")
        self.assertEqual(cfg["en_git_blob_sha1"], "8a998d4848d426c07ad88b17a1fb84379257f4f8")
        self.assertEqual(audit["alignment"]["cn_non_dialogue_commands"], 65)
        self.assertTrue(audit["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertEqual(m["next_file"], "obt/main/level_main_05-04_end.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (87, 5246))
        self.assertEqual((qa["new_text_entries"], qa["source_text_entries_remaining"], qa["completed_story_files"]), (21, 0, 87))
        self.assertIn("level_main_05-04_beg.txt\tfirst_draft_complete\t41\t0\t41", (ROOT / "story/CHAPTER_5_INDEX_v097.tsv").read_text(encoding="utf-8"))

    def test_preview_invariants(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        source = "[Image]\n" + "".join('[name="Hoshiguma"]  EN line '+str(i)+"\n" for i in range(1, 42)) + "[Dialog]\n"
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"])
        self.assertEqual(count, 41)
        self.assertIn("[Image]\n", patched.decode())
        self.assertIn("[Dialog]\n", patched.decode())
        self.assertIn('[name="Хосигума"]  '+cfg["dialogues"]["41"], patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), {k:v for k,v in cfg["dialogues"].items() if k != "41"})

if __name__ == "__main__":
    unittest.main()
