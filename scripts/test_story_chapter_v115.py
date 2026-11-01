# coding: utf-8
"""Regression tests for chapter 5-10 after-battle complete v1.15."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-10_end.txt"
OLD = "story/story_chapter_5_stage_5-10_after_partial_ru_v114.json"
NEW = "story/story_chapter_5_stage_5-10_after_ru_v115.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter510AfterCompleteV115(unittest.TestCase):
    def test_contiguous_and_previous_unchanged(self):
        old, new = load(OLD), load(NEW)
        self.assertEqual(new["source_file"], REL)
        self.assertEqual(set(new["dialogues"]), {str(i) for i in range(1, 151)})
        self.assertEqual(set(new["source_dialogue_line_numbers"]), set(new["dialogues"]))
        self.assertEqual({k: new["dialogues"][k] for k in old["dialogues"]}, old["dialogues"])
        self.assertEqual({k: new["source_dialogue_line_numbers"][k] for k in old["source_dialogue_line_numbers"]}, old["source_dialogue_line_numbers"])
        self.assertTrue(all(x.strip() and "\n" not in x and "\r" not in x for x in new["dialogues"].values()))

    def test_source_and_progress(self):
        d = load(NEW)
        p = d["progress"]
        self.assertEqual((p["named_ru_lines"], p["remaining_text_entries"], p["complete"]), (150, 0, True))
        self.assertEqual((d["source_dialogue_line_numbers"]["116"], d["source_dialogue_line_numbers"]["150"]), (326, 406))
        self.assertEqual(d["source"]["cn_git_blob_sha1"], "7f4138c8b615b4965c98c08f08bff695d37555c5")
        self.assertEqual(d["source"]["en_git_blob_sha1"], "a26bb1d24231785c98762193454268f5f8fbf081")
        self.assertIn("контратаки", d["dialogues"]["147"])
        self.assertIn("следующему этапу", d["dialogues"]["150"])

    def test_selection_and_qa(self):
        a, q = load("reports/CHAPTER_5_STAGE_5-10_AFTER_SOURCE_AUDIT_v115.json"), load("reports/QA_MAIN_STORY_v115.json")
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["en_tagged"], a["alignment"]["cn_bracket_commands"], a["alignment"]["en_bracket_commands"]), (150,150,265,265))
        self.assertEqual((a["alignment"]["ru_tagged_entries"], a["alignment"]["ru_remaining_entries"]), (150,0))
        self.assertEqual((q["new_named_ru"], q["scene_ru_named"], q["scene_remaining_named"]), (35,150,0))
        self.assertTrue(q["included_in_complete_story_selection"])
        sel = load("story/story_main_selection_ru_v115.json")
        self.assertEqual(len(sel["files"]), 96)
        self.assertEqual(sel["files"][REL]["dialogues"], load(NEW)["dialogues"])
        self.assertEqual(sel["files"][REL]["source_dialogue_line_numbers"], load(NEW)["source_dialogue_line_numbers"])

    def test_manifest_index(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v115.json")
        t = m["translation_integrity"]
        self.assertEqual(m["next_file"], "obt/main/level_st_05-01.txt")
        self.assertEqual((t["main_story_files"], t["main_story_partial_named_ru_lines"], t["main_story_text_entries_including_partial"]), (96,0,6138))
        self.assertEqual((t["main_story_named_ru_lines"], t["main_story_text_entries_including_unnamed"]), (6100,6138))
        index = (ROOT / "story/CHAPTER_5_INDEX_v115.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-10_end.txt\tfirst_draft_complete\t150\t0\t150", index)

if __name__ == "__main__":
    unittest.main()
