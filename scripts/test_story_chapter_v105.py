# coding: utf-8
"""Regression tests for 5-9 after battle, v1.05 partial continuation."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_05-09_end.txt"
NEW = "story/story_chapter_5_stage_5-9_after_partial_ru_v105.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter59AfterPartialV105(unittest.TestCase):
    def test_contiguous_progress(self):
        p = load(NEW)
        self.assertEqual(set(p["dialogues"]), {str(i) for i in range(1, 60)})
        self.assertFalse(p["progress"]["complete"])
        self.assertEqual((p["progress"]["total_ru_text_entries"], p["progress"]["remaining_text_entries"]), (59, 77))
        self.assertEqual((p["progress"]["source_lines_translated_through"], p["progress"]["first_untranslated_named_source_line"], p["progress"]["next_named_ordinal"]), (139, 144, 60))
        self.assertTrue(all(isinstance(v, str) and v.strip() and not any(ch in v for ch in "\r\n\t") for v in p["dialogues"].values()))

    def test_prior_translation_unchanged(self):
        previous = load("story/story_chapter_5_stage_5-9_after_partial_ru_v104.json")
        current = load(NEW)
        self.assertEqual({k: current["dialogues"][k] for k in previous["dialogues"]}, previous["dialogues"])
        self.assertEqual(current["source_file"], REL)
        self.assertEqual((current["source"]["cn_git_blob_sha1"], current["source"]["en_git_blob_sha1"]), ("ced45a6cd4fe5679c87cdd7ddae10fe051ef9465", "e02b0f41bbaf69d866c1ba86b73d5f361227b6fb"))

    def test_full_selection_excludes_partial(self):
        s = load("story/story_main_selection_ru_v103.json")
        self.assertEqual(len(s["files"]), 93)
        self.assertNotIn(REL, s["files"])
        self.assertEqual(sum(f["dialogue_count"] for f in s["files"].values()), 5604)

    def test_manifest_index_audit(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v105.json")
        q = load("reports/QA_MAIN_STORY_v105.json")
        a = load("reports/CHAPTER_5_STAGE_5-9_AFTER_SOURCE_AUDIT_v105.json")
        self.assertEqual((m["next_file"], m["next_named_ordinal"]), (REL, 60))
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"], 5663)
        self.assertEqual((q["new_text_entries"], q["partial_scene_text_entries"], q["source_text_entries_remaining"]), (39, 59, 77))
        self.assertEqual((a["alignment"]["cn_named"], a["alignment"]["en_named"]), (136, 136))
        self.assertTrue(a["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertIn("level_main_05-09_end.txt\tpartial_first_draft_59_of_136\t59\t0\t59", (ROOT / "story/CHAPTER_5_INDEX_v105.tsv").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
