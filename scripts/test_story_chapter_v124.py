# coding: utf-8
"""Chapter 6-3 before battle complete first draft v1.24: regression invariants."""
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
class Chapter603BeforeV124(unittest.TestCase):
    def test_complete_and_preserves_previous(self):
        d = load("story/story_chapter_6_stage_6-3_before_ru_v124.json")
        old = load("story/story_chapter_6_stage_6-3_before_partial_ru_v123.json")
        self.assertEqual(set(d["dialogues"]), {str(i) for i in range(1, 93)})
        self.assertEqual(set(d["source_dialogue_line_numbers"]), set(d["dialogues"]))
        self.assertEqual(list(d["source_dialogue_line_numbers"].values()), sorted(d["source_dialogue_line_numbers"].values()))
        self.assertEqual((d["source_dialogue_line_numbers"]["37"], d["source_dialogue_line_numbers"]["92"]), (99, 218))
        self.assertEqual({str(i): d["dialogues"][str(i)] for i in range(1,37)}, old["dialogues"])
        self.assertTrue(all(s.strip() and not re.search(r"[\u4e00-\u9fff\r\n]",s) for s in d["dialogues"].values()))
        self.assertEqual((d["progress"]["named_ru_lines"],d["progress"]["remaining_text_entries"],d["progress"]["complete"]),(92,0,True))
    def test_source_alignment_and_decision(self):
        d=load("story/story_chapter_6_stage_6-3_before_ru_v124.json")
        a=load("reports/CHAPTER_6_STAGE_6-3_BEFORE_SOURCE_AUDIT_v124.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("761a61b650186ed88476602440936d8d1e7116d3","328738b032366a56e2b270e8b8e77ac8fbc92ea3"))
        self.assertEqual((a["alignment"]["cn_tagged"],a["alignment"]["en_tagged"],a["alignment"]["cn_non_decision_commands"]),(92,92,128))
        self.assertTrue(a["alignment"]["cn_en_non_decision_command_text_equal"])
        self.assertEqual(d["decisions"],{"1":{"line":213,"options":["Я в порядке! Будь осторожна!"],"values":["1"]}})
        self.assertEqual(d["source_decision_line_numbers"],{"1":213})
    def test_selection_preserves_all_earlier_files(self):
        d=load("story/story_chapter_6_stage_6-3_before_ru_v124.json")
        old=load("story/story_main_selection_ru_v122.json")
        s=load("story/story_main_selection_ru_v124.json")
        self.assertEqual(len(s["files"]),102)
        for k,v in old["files"].items(): self.assertEqual(s["files"][k],v)
        f=s["files"][d["source_file"]]
        self.assertEqual((f["dialogues"],f["decisions"],f["source_dialogue_line_numbers"]),(d["dialogues"],d["decisions"],d["source_dialogue_line_numbers"]))
    def test_manifest_index_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v124.json")
        q=load("reports/QA_MAIN_STORY_v124.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_partial_files"]),(102,0))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_unnamed"],6706)
        self.assertEqual((q["scene_ru_named"],q["scene_remaining_named"],q["included_in_complete_story_selection"]),(92,0,True))
        self.assertEqual(m["next_file"],"obt/main/level_main_06-03_end.txt")
        idx=(ROOT/"story/CHAPTER_6_INDEX_v124.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-03_beg.txt\tfirst_draft_complete\t92\t0\t92",idx)
if __name__=="__main__": unittest.main()
