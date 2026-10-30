# coding: utf-8
"""v0.62: guard the explicitly partial CN-primary 3-7 opening against false completion."""
import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = "obt/main/level_main_03-07_beg.txt"
FILE = "story/story_chapter_3_stage_3-7_before_partial_ru_v062.json"
CN = "5d3bf7deb9bc1a286ee7f8b8f4817f6893a0eed3"
EN = "f682ae658542d594d0bcc474c0201e86d9a22ec7"

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter3Stage37OpeningV062(unittest.TestCase):
    def test_partial_source_pinned(self):
        doc = read(FILE)
        self.assertEqual(doc["version"], "v0.62")
        self.assertEqual(set(doc["files"]), {REL})
        record = doc["files"][REL]
        self.assertEqual((record["source_dialogue_count"], record["translated_dialogue_count"]), (55, 20))
        self.assertEqual((record["translated_ordinals_start"], record["translated_ordinals_end"]), (1, 20))
        self.assertEqual((record["source_line_start"], record["source_line_end"]), (6, 46))
        self.assertEqual(set(record["dialogues"]), set(map(str, range(1, 21))))
        self.assertEqual((record["cn_git_blob_sha1"], record["en_git_blob_sha1"]), (CN, EN))
        for text in record["dialogues"].values():
            self.assertTrue(isinstance(text, str) and text.strip())
            self.assertNotRegex(text, r"[\r\n\t]")
            self.assertNotRegex(text, r"\{@[a-zA-Z_]+\}|<[^>]+>")
        self.assertIn("наобум", record["dialogues"]["8"])
        self.assertIn("камешками", record["dialogues"]["18"])

    def test_index_keeps_partial_separate(self):
        with (ROOT / "story/CHAPTER_3_INDEX_v062.tsv").open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
        self.assertEqual(len(rows), 13)
        self.assertEqual(rows[-1]["source_filename"], "level_main_03-07_beg.txt")
        self.assertEqual((rows[-1]["ru_status"], rows[-1]["dialogues_ru_count"]), ("partial_first_draft", "20"))
        self.assertEqual((rows[-1]["cn_git_blob_sha1"], rows[-1]["en_git_blob_sha1"]), (CN, EN))
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows[:-1]), 882)
        complete = read("story/story_main_selection_ru_v061.json")
        self.assertEqual(len(complete["files"]), 56)
        self.assertEqual(sum(x["dialogue_count"] for x in complete["files"].values()), 3259)
        self.assertNotIn(REL, complete["files"])

    def test_manifest_qa_audit_do_not_claim_completion(self):
        manifest = read("chronology/CHRONOLOGY_MANIFEST_v062.json")
        integrity = manifest["translation_integrity"]
        self.assertEqual((integrity["main_story_files"], integrity["main_story_named_ru_lines"]), (56, 3259))
        self.assertEqual((integrity["main_story_chapter_3_files"], integrity["main_story_chapter_3_named_ru_lines"]), (12, 882))
        self.assertEqual(integrity["main_story_chapter_3_partial_named_ru_lines"], 20)
        self.assertEqual(manifest["next_file"], REL)
        qa = read("reports/QA_MAIN_STORY_v062.json")
        self.assertEqual((qa["new_named_ru_partial"], qa["source_named_remaining"]), (20, 35))
        self.assertFalse(qa["included_in_complete_story_selection"])
        self.assertFalse(qa["in_game_test"])
        audit = read("reports/CHAPTER_3_STAGE_3-7_BEFORE_SOURCE_AUDIT_v062.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (55, 55))
        self.assertTrue(audit["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"], CN)
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"], EN)

if __name__ == "__main__":
    unittest.main()
