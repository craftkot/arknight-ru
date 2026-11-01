# coding: utf-8
"""Regression checks for Arknights RU v0.98: main story 5-4 after battle."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-04_end.txt"
NEW = "story/story_chapter_5_stage_5-4_after_ru_v098.json"
BARE = {33, 34, 35, 36, 41, 42, 43, 44}

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter54AfterV098(unittest.TestCase):
    def test_complete_text_entries_and_source_hashes(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (59, 51, 8))
        self.assertEqual(set(cfg["dialogues"]), {str(i) for i in range(1, 60)})
        self.assertTrue(all(v.strip() and not any(c in v for c in "\\r\\n\\t") for v in cfg["dialogues"].values()))
        self.assertEqual(cfg["cn_git_blob_sha1"], "1cd797556e223bd17552b9f7c81231b32d1433e1")
        self.assertEqual(cfg["en_git_blob_sha1"], "8fa937063c53ac4904fb0bcf4824ab41a1d5501e")
        self.assertIn("комнату", cfg["dialogues"]["39"])
        self.assertIn("зацепка", cfg["dialogues"]["56"])

    def test_selection_preserves_all_previous_scenes(self):
        old = load("story/story_main_selection_ru_v097.json")
        new = load("story/story_main_selection_ru_v098.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (87, 88))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 5328)

    def test_audit_manifest_index_and_qa(self):
        audit = load("reports/CHAPTER_5_STAGE_5-4_AFTER_SOURCE_AUDIT_v098.json")
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v098.json")
        qa = load("reports/QA_MAIN_STORY_v098.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["cn_bare"]), (51, 8))
        self.assertEqual((audit["alignment"]["cn_non_dialogue_commands"], audit["alignment"]["en_non_dialogue_commands"]), (105, 105))
        self.assertTrue(audit["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(manifest["next_file"], "obt/main/level_main_05-06_beg.txt")
        self.assertEqual((manifest["translation_integrity"]["main_story_files"], manifest["translation_integrity"]["main_story_named_ru_lines"]), (88, 5297))
        self.assertEqual((qa["new_text_entries"], qa["source_text_entries_remaining"], qa["completed_story_files"]), (59, 0, 88))
        self.assertIn("level_main_05-04_end.txt\\tfirst_draft_complete\\t51\\t8\\t59", (ROOT / "story/CHAPTER_5_INDEX_v098.tsv").read_text(encoding="utf-8"))

    def test_preview_preserves_commands_and_bare_narration(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        source_lines = ['[HEADER(key="title_test")] sample', '[Image]']
        for i in range(1, 60):
            if i in BARE:
                source_lines.append("EN narration " + str(i))
            else:
                source_lines.append('[name="Ch\'en"]  EN line ' + str(i))
        source_lines.append('[Dialog]')
        source = "\\n".join(source_lines) + "\\n"
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"], include_bare=True)
        result = patched.decode("utf-8").splitlines()
        self.assertEqual(count, 59)
        self.assertEqual(result[0:2], source_lines[0:2])
        self.assertEqual(result[-1], "[Dialog]")
        self.assertEqual(result[2 + 32], cfg["dialogues"]["33"])
        self.assertEqual(result[2 + 40], cfg["dialogues"]["41"])
        self.assertEqual(result[2 + 58], '[name="Чэнь"]  ' + cfg["dialogues"]["59"])
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), {k:v for k,v in cfg["dialogues"].items() if k != "59"}, include_bare=True)

if __name__ == "__main__":
    unittest.main()
