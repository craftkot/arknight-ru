# coding: utf-8
"""Chapter 6-3 after battle v1.27 complete draft regression invariants."""
import json
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
class Chapter603AfterV127(unittest.TestCase):
    def test_contiguous_and_preserves_prior(self):
        d=load("story/story_chapter_6_stage_6-3_after_ru_v127.json")
        prev=load("story/story_chapter_6_stage_6-3_after_partial_ru_v126.json")
        self.assertEqual(list(d["dialogues"]),[str(i) for i in range(1,72)])
        self.assertEqual(list(d["source_dialogue_line_numbers"]),list(d["dialogues"]))
        self.assertEqual({k:d["dialogues"][k] for k in prev["dialogues"]},prev["dialogues"])
        self.assertEqual({k:d["source_dialogue_line_numbers"][k] for k in prev["source_dialogue_line_numbers"]},prev["source_dialogue_line_numbers"])
        self.assertEqual([d["source_dialogue_line_numbers"][str(i)] for i in range(39,72)],[113,115,116,117,119,121,123,125,127,129,131,132,134,136,138,140,146,148,149,151,152,154,155,157,159,160,161,163,165,166,167,168,172])
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n\t]",s) for s in d["dialogues"].values()))
    def test_source_progress(self):
        d=load("story/story_chapter_6_stage_6-3_after_ru_v127.json")
        a=load("reports/CHAPTER_6_STAGE_6-3_AFTER_SOURCE_AUDIT_v127.json")
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["unnamed_ru_lines"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(68,3,0,True))
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("051c88071492555fa8678a174411fc228e81a1e6","08d87f3b76129c54ba28bf56ddbfcc61d87ca26e"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(68,68,105))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(d["decisions"],{})
    def test_selection_preserves_all(self):
        s=load("story/story_main_selection_ru_v127.json")
        old=load("story/story_main_selection_ru_v124.json")
        d=load("story/story_chapter_6_stage_6-3_after_ru_v127.json")
        self.assertEqual(len(s["files"]),103)
        for k,v in old["files"].items(): self.assertEqual(s["files"][k],v)
        f=s["files"][d["source_file"]]
        self.assertEqual((f["dialogues"],f["source_dialogue_line_numbers"],f["decisions"]),(d["dialogues"],d["source_dialogue_line_numbers"],{}))
    def test_manifest_index_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v127.json")
        q=load("reports/QA_MAIN_STORY_v127.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(103,0))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_unnamed"],6777)
        self.assertEqual((q["scene_ru_named"],q["scene_ru_unnamed"],q["included_in_complete_story_selection"]),(68,3,True))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-04_beg.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v127.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-03_end.txt\tfirst_draft_complete\t68\t3\t71",idx)
if __name__=="__main__": unittest.main()
