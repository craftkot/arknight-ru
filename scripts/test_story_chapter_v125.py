# coding: utf-8
"""Chapter 6-3 after battle v1.25: partial draft invariants."""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
class Chapter603AfterV125(unittest.TestCase):
    def test_partial_contiguous_positions(self):
        d=load("story/story_chapter_6_stage_6-3_after_partial_ru_v125.json")
        self.assertEqual(list(d["dialogues"]),[str(i) for i in range(1,27)])
        self.assertEqual(list(d["source_dialogue_line_numbers"]),list(d["dialogues"]))
        self.assertEqual(list(d["source_dialogue_line_numbers"].values()),sorted(d["source_dialogue_line_numbers"].values()))
        self.assertEqual((d["source_dialogue_line_numbers"]["1"],d["source_dialogue_line_numbers"]["11"],d["source_dialogue_line_numbers"]["26"]),(4,28,86))
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["unnamed_ru_lines"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(24,2,45,False))
        self.assertTrue(all(s.strip() and "\\n" not in s for s in d["dialogues"].values()))
    def test_source_hashes_and_structure(self):
        d=load("story/story_chapter_6_stage_6-3_after_partial_ru_v125.json")
        a=load("reports/CHAPTER_6_STAGE_6-3_AFTER_SOURCE_AUDIT_v125.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("051c88071492555fa8678a174411fc228e81a1e6","08d87f3b76129c54ba28bf56ddbfcc61d87ca26e"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["cn_plain"],a["alignment"]["cn_non_decision_commands"]),(68,3,105))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(d["decisions"],{})
    def test_previous_selection_is_unchanged(self):
        s=load("story/story_main_selection_ru_v124.json")
        self.assertEqual(len(s["files"]),102)
        self.assertNotIn("obt/main/level_main_06-03_end.txt",s["files"])
    def test_manifest_index_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v125.json")
        q=load("reports/QA_MAIN_STORY_v125.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(102,1))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"],6732)
        self.assertEqual((q["scene_ru_named"],q["scene_ru_unnamed"],q["included_in_complete_story_selection"]),(24,2,False))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-03_end.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v125.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-03_end.txt\\tpartial_first_draft_26_of_71\\t24\\t2\\t26",idx)
if __name__=="__main__": unittest.main()
