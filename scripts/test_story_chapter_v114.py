# coding: utf-8
"""Regression tests for contiguous chapter 5-10 after-battle v1.14 partial."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-10_end.txt"
NEW = "story/story_chapter_5_stage_5-10_after_partial_ru_v114.json"
OLD = "story/story_chapter_5_stage_5-10_after_partial_ru_v113.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter510AfterPartialV114(unittest.TestCase):
    def test_contiguous_and_previous_unchanged(self):
        old, new = load(OLD), load(NEW)
        self.assertEqual(new["source_file"], REL)
        self.assertEqual(set(new["dialogues"]), {str(i) for i in range(1, 116)})
        self.assertEqual(set(new["source_dialogue_line_numbers"]), set(new["dialogues"]))
        self.assertEqual({k:new["dialogues"][k] for k in old["dialogues"]}, old["dialogues"])
        self.assertEqual({k:new["source_dialogue_line_numbers"][k] for k in old["source_dialogue_line_numbers"]}, old["source_dialogue_line_numbers"])
        self.assertTrue(all(x.strip() and "\n" not in x and "\r" not in x for x in new["dialogues"].values()))

    def test_progress_and_source_specifics(self):
        d = load(NEW)
        p = d["progress"]
        self.assertEqual((p["named_ru_lines"], p["remaining_text_entries"], p["next_named_ordinal"], p["first_untranslated_named_source_line"]), (115, 35, 116, 326))
        self.assertFalse(p["complete"])
        self.assertEqual((d["source_dialogue_line_numbers"]["78"], d["source_dialogue_line_numbers"]["115"]), (210, 316))
        self.assertIn("урсусском", d["dialogues"]["81"])
        self.assertIn("Прочь с дороги", d["dialogues"]["88"])
        self.assertIn("созвал Воссоединение", d["dialogues"]["107"])
        self.assertEqual(d["source"]["cn_git_blob_sha1"], "7f4138c8b615b4965c98c08f08bff695d37555c5")
        self.assertEqual(d["source"]["en_git_blob_sha1"], "a26bb1d24231785c98762193454268f5f8fbf081")

    def test_audit_and_selection(self):
        a = load("reports/CHAPTER_5_STAGE_5-10_AFTER_SOURCE_AUDIT_v114.json")
        q = load("reports/QA_MAIN_STORY_v114.json")
        self.assertEqual((a["alignment"]["cn_tagged"], a["alignment"]["en_tagged"], a["alignment"]["cn_bracket_commands"], a["alignment"]["en_bracket_commands"]), (150,150,265,265))
        self.assertEqual((a["alignment"]["ru_tagged_entries"],a["alignment"]["ru_remaining_entries"]),(115,35))
        self.assertEqual((q["new_named_ru"],q["scene_ru_named"],q["scene_remaining_named"]),(38,115,35))
        self.assertFalse(q["included_in_complete_story_selection"])
        sel = load("story/story_main_selection_ru_v111.json")
        self.assertEqual(len(sel["files"]), 95)
        self.assertNotIn(REL,sel["files"])

    def test_manifest_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v114.json")
        t=m["translation_integrity"]
        self.assertEqual((m["next_file"],m["next_named_ordinal"]),(REL,116))
        self.assertEqual((t["main_story_files"],t["main_story_partial_named_ru_lines"],t["main_story_text_entries_including_partial"]),(95,115,6103))
        index=(ROOT/"story/CHAPTER_5_INDEX_v114.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-10_end.txt\tpartial_first_draft_115_of_150\t115\t0\t115",index)

if __name__ == "__main__":
    unittest.main()
