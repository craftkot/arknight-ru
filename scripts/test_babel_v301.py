# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6AfterV301(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_after_partial_ru_v301.json")
        self.audit = load("reports/BABEL_BB6_AFTER_SOURCE_AUDIT_v301.json")
        self.qa = load("reports/QA_BABEL_v301.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v301.json")
        self.index = (ROOT / "events/BABEL_INDEX_v301.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.review = (ROOT / "docs/CN_EN_RU_TERMINOLOGY_REVIEW.tsv").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.01")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (40, 178, 138))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (41, 129))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 41)))
        expected = [11,12,13,16,26,35,44,56,61,62,63,64,66,67,68,72,73,81,82,85,87,89,91,93,95,97,98,99,100,102,104,105,106,107,108,116,123,125,126,128]
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], expected)

    def test_kinds_and_translation_invariants(self):
        kinds = {}
        for item in self.doc["dialogues"]:
            kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(c) <= 0x9fff for c in item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
        self.assertEqual(kinds, {"named": 30, "narration": 9, "subtitle": 1})
        subtitle = self.doc["dialogues"][35]["text_ru"]
        self.assertTrue(subtitle.startswith("<color=#000000>"))
        self.assertTrue(subtitle.endswith("</color>"))
        self.assertIn("Жрица", self.doc["dialogues"][3]["text_ru"])
        self.assertIn("орипатии", self.doc["dialogues"][26]["text_ru"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "56a05581ddc4364646998f6169cce72797f6834d")
        self.assertEqual(s["en_git_blob_sha1"], "0b839585231d08e1980894b6b1d98a9861c23759")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (492, 493))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (178, 178))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (314, 314))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertTrue(a["cn_en_control_command_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_tag_sequence_match"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_subtitle_markup_alignment"])
        self.assertFalse(a["game_behavior_verified"])
        self.assertFalse(a["scene_complete"])

    def test_audit_qa_index_chronology_readme_and_terms(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 40)
        self.assertEqual(self.audit["full_scene_counts"]["text_positions"], 178)
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 138)
        self.assertEqual(self.qa["babel_completed_files"], 13)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 9)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3060)
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_06_end.txt")
        self.assertEqual(self.manifest["partial_scene_next_text_ordinal"], 41)
        self.assertEqual(self.manifest["partial_scene_next_source_line"], 129)
        row = next(line for line in self.index.splitlines() if "level_act33side_06_end.txt" in line)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_06_end.txt","partial_first_draft","30","0","9","0","1","40"])
        self.assertIn("40/178", self.readme)
        self.assertIn("Priestess — Жрица", self.terms)
        self.assertIn("普瑞赛斯\tPriestess\tЖрица", self.review)

if __name__ == "__main__":
    unittest.main()
