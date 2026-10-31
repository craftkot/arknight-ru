# coding: utf-8
"""Regression checks for the partial 4-10 after-battle translation v0.88."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_04-10_end.txt"
OLD = "story/story_chapter_4_stage_4-10_after_partial_ru_v087.json"
NEW = "story/story_chapter_4_stage_4-10_after_partial_ru_v088.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter410AfterPartialV088(unittest.TestCase):
    def test_contiguous_and_previous_preserved(self):
        old, new = load(OLD), load(NEW)
        self.assertEqual(new["source_file"], REL)
        self.assertEqual(set(new["dialogues"]), {str(i) for i in range(1, 87)})
        self.assertEqual({k: new["dialogues"][k] for k in old["dialogues"]}, old["dialogues"])
        self.assertEqual((new["progress"]["named_ru_lines"], new["progress"]["remaining_text_entries"]), (86, 71))
        self.assertEqual((new["progress"]["source_lines_translated_through"], new["progress"]["first_untranslated_named_source_line"], new["progress"]["next_named_ordinal"]), (192, 198, 87))
        self.assertFalse(new["progress"]["complete"])
        for s in new["dialogues"].values():
            self.assertTrue(isinstance(s, str) and s.strip())
            self.assertFalse(any(c in s for c in "\r\n\t"))

    def test_source_alignment_and_cn_details(self):
        p, a = load(NEW), load("reports/CHAPTER_4_STAGE_4-10_AFTER_SOURCE_AUDIT_v088.json")
        self.assertEqual((p["source"]["cn_git_blob_sha1"], p["source"]["en_git_blob_sha1"]), ("190af39edc748f963b26cb1ef510c63ea7c3f851", "d160f1b33b0ea43597526e8966b854623d6b0e1e"))
        self.assertEqual((a["alignment"]["cn_named"], a["alignment"]["en_named"], a["alignment"]["cn_unnamed"], a["alignment"]["en_unnamed"]), (156, 156, 1, 1))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (210, 210))
        self.assertTrue(a["alignment"]["cn_en_named_source_line_positions_equal"])
        self.assertTrue(a["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertIn("верят в меня", p["dialogues"]["66"])
        self.assertIn("её отрядом", p["dialogues"]["71"])

    def test_index_manifest_qa(self):
        m, q = load("chronology/CHRONOLOGY_MANIFEST_v088.json"), load("reports/QA_MAIN_STORY_v088.json")
        t = m["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (79, 4713))
        self.assertEqual((t["main_story_chapter_4_partial_named_ru_lines"], t["main_story_named_ru_lines_including_partial"]), (86, 4799))
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 87))
        self.assertEqual((q["new_text_entries"], q["partial_scene_text_entries"], q["source_text_entries_remaining"]), (46, 86, 71))
        self.assertFalse(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v088.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-10_end.txt\tpartial_first_draft_86_of_157\t86\t0\t86", idx)

    def test_complete_selection_unchanged(self):
        selection = load("story/story_main_selection_ru_v086.json")
        self.assertEqual(len(selection["files"]), 79)
        self.assertNotIn(REL, selection["files"])
        self.assertEqual(sum(f["dialogue_count"] for f in selection["files"].values()), 4729)

if __name__ == "__main__":
    unittest.main()
