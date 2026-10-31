# coding: utf-8
"""v0.68: chapter 4-1 after battle PARTIAL opening; never treat as full preview."""
import json
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parent.parent
REL="obt/main/level_main_04-01_end.txt"
PARTIAL="story/story_chapter_4_stage_4-1_after_partial_ru_v068.json"
CN="311a849380f0cc13048d20f1bdf052d71d6870d5"
EN="a86c16ded890cedd0be9d41be3ebdef8781f1ff5"
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Chapter41AfterPartialV068(unittest.TestCase):
    def test_partial_exact_ordinals(self):
        x=load(PARTIAL)
        self.assertEqual(x["version"],"v0.68")
        self.assertIn("PARTIAL",x["stage"])
        self.assertEqual(set(x["files"]),{REL})
        s=x["files"][REL]
        self.assertEqual((s["source_dialogue_count"],s["translated_dialogue_count"]),(76,23))
        self.assertEqual((s["source_named_dialogue_count"],s["source_unnamed_dialogue_count"]),(71,5))
        self.assertEqual((s["translated_named_dialogue_count"],s["translated_unnamed_dialogue_count"]),(21,2))
        self.assertEqual((s["source_line_start"],s["source_line_end"]),(5,42))
        self.assertEqual((s["translated_ordinals_start"],s["translated_ordinals_end"]),(1,23))
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,24))))
        self.assertEqual((s["cn_git_blob_sha1"],s["en_git_blob_sha1"]),(CN,EN))
        self.assertEqual(s["decisions_translated"],0)
        for val in s["dialogues"].values():
            self.assertIsInstance(val,str)
            self.assertTrue(val.strip())
            self.assertFalse(any(c in val for c in "\r\n\t"))
            self.assertFalse(re.search(r"\{@\w+\}",val))
        self.assertIn("19 км",s["dialogues"]["1"])
        self.assertIn("Нирл",s["dialogues"]["9"])
        self.assertIn("вернёмся к заданию",s["dialogues"]["23"])
    def test_not_in_complete_selection(self):
        old=load("story/story_main_selection_ru_v067.json")
        self.assertEqual(len(old["files"]),61)
        self.assertNotIn(REL,old["files"])
        self.assertEqual(sum(s["dialogue_count"] for s in old["files"].values()),3622)
    def test_manifest_index_audit_and_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v068.json")
        i=m["translation_integrity"]
        self.assertEqual(m["next_file"],REL)
        self.assertEqual((i["main_story_files"],i["main_story_named_ru_lines"]),(61,3620))
        self.assertEqual((i["main_story_chapter_4_partial_named_ru_lines"],i["main_story_chapter_4_partial_unnamed_ru_lines"]),(21,2))
        a=load("reports/CHAPTER_4_STAGE_4-1_AFTER_SOURCE_AUDIT_v068.json")
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"],a["sources"]["en"]["git_blob_sha1"]),(CN,EN))
        self.assertEqual((a["alignment"]["cn_named"],a["alignment"]["en_named"]),(71,71))
        self.assertEqual((a["alignment"]["cn_unnamed"],a["alignment"]["en_unnamed"]),(5,5))
        self.assertEqual(a["alignment"]["decision_option_counts"],[3,2,3])
        q=load("reports/QA_MAIN_STORY_v068.json")
        self.assertEqual((q["new_text_entries"],q["source_text_entries_remaining"]),(23,53))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx=(ROOT/"story/CHAPTER_4_INDEX_v068.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-01_end.txt\tpartial_first_draft\t21\t2\t23",idx)
if __name__=="__main__":
    unittest.main()
