# coding: utf-8
"""Chapter 6-3 after battle v1.26 partial draft regression invariants."""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
class Chapter603AfterV126(unittest.TestCase):
    def test_contiguous_and_preserves_prior_translation(self):
        d=load("story/story_chapter_6_stage_6-3_after_partial_ru_v126.json")
        prev=load("story/story_chapter_6_stage_6-3_after_partial_ru_v125.json")
        self.assertEqual(list(d["dialogues"]), [str(i) for i in range(1,39)])
        self.assertEqual(list(d["source_dialogue_line_numbers"]),list(d["dialogues"]))
        self.assertEqual({k:d["dialogues"][k] for k in prev["dialogues"]},prev["dialogues"])
        self.assertEqual({k:d["source_dialogue_line_numbers"][k] for k in prev["source_dialogue_line_numbers"]},prev["source_dialogue_line_numbers"])
        self.assertEqual([d["source_dialogue_line_numbers"][str(i)] for i in range(27,39)],[92,93,95,97,99,101,102,104,106,108,109,111])
        self.assertTrue(all(s.strip() and "\n" not in s and "\t" not in s for s in d["dialogues"].values()))
    def test_progress_and_source_invariants(self):
        d=load("story/story_chapter_6_stage_6-3_after_partial_ru_v126.json")
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["unnamed_ru_lines"],d["progress"]["remaining_text_entries"]),(36,2,33))
        self.assertEqual((d["progress"]["next_text_ordinal"],d["progress"]["next_source_line"],d["progress"]["complete"]),(39,113,False))
        self.assertEqual(d["progress"]["total_ru_text_entries"]+d["progress"]["remaining_text_entries"],71)
        self.assertEqual(d["source"]["cn_git_blob_sha1"],"051c88071492555fa8678a174411fc228e81a1e6")
        self.assertEqual(d["source"]["en_git_blob_sha1"],"08d87f3b76129c54ba28bf56ddbfcc61d87ca26e")
        self.assertEqual(d["decisions"],{})
    def test_manifest_index_and_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v126.json")
        q=load("reports/QA_MAIN_STORY_v126.json")
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"],6744)
        self.assertEqual(m["translation_integrity"]["main_story_partial_named_ru_lines"],36)
        self.assertEqual((q["scene_ru_named"],q["scene_ru_unnamed"],q["scene_remaining_named"],q["scene_remaining_unnamed"]),(36,2,32,1))
        self.assertFalse(q["included_in_complete_story_selection"])
        idx=(ROOT/"story/CHAPTER_6_INDEX_v126.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-03_end.txt\tpartial_first_draft_38_of_71\t36\t2\t38",idx)
    def test_complete_selection_not_modified(self):
        s=load("story/story_main_selection_ru_v124.json")
        self.assertEqual(len(s["files"]),102)
        self.assertNotIn("obt/main/level_main_06-03_end.txt",s["files"])
if __name__=="__main__": unittest.main()
