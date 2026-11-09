# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7BeforeV305(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_before_partial_ru_v305.json")
        self.audit = load("reports/BABEL_BB7_BEFORE_SOURCE_AUDIT_v305.json")
        self.qa = load("reports/QA_BABEL_v305.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v305.json")
        self.index = (ROOT / "events/BABEL_INDEX_v305.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.05")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (40, 222, 182))
        self.assertFalse(p["complete"])
        self.assertEqual(p["next_text_ordinal"], 41)
        self.assertEqual(p["next_text_source_line"], 114)
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 41)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], [13,14,15,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,62,63,68,69,78,85,94,101])

    def test_kinds_and_speakers(self):
        kinds = {}
        for item in self.doc["dialogues"]:
            kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
        self.assertEqual(kinds, {"named":32, "subtitle":8})
        self.assertTrue(all(x["speaker_cn"] == "博士" for x in self.doc["dialogues"][:32]))
        self.assertTrue(all("speaker_cn" not in x for x in self.doc["dialogues"][32:]))

    def test_markup_is_balanced_and_preserved(self):
        by_ordinal = {x["ordinal"]: x for x in self.doc["dialogues"]}
        for n in (2,35,36,38,40):
            s = by_ordinal[n]["text_ru"]
            self.assertEqual(s.count("<color="), 1)
            self.assertEqual(s.count("</color>"), 1)
        self.assertIn("0018_admin", by_ordinal[2]["text_ru"])
        self.assertIn("Ассимилированной Вселенной", by_ordinal[19]["text_ru"])
        self.assertIn("Талоса-II", by_ordinal[7]["text_ru"])

    def test_source_alignment_and_hashes(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "605fede5533907ce926d038129da2abb2af57af7")
        self.assertEqual(s["en_git_blob_sha1"], "63c0f520b4f0de80ea34b4dd0afbbc4cb2df9f5b")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (434,434))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (222,222))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (212,212))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertTrue(a["cn_en_control_command_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_tag_sequence_match"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertEqual(a["documented_full_scene_speaker_label_difference"]["ordinal"], 79)
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_readme_and_qa(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 40)
        self.assertEqual(self.audit["translated_segment"]["next_text_ordinal"], 41)
        self.assertEqual(self.qa["scene_translated_text_entries"], 40)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 182)
        self.assertEqual(self.qa["babel_completed_files"], 14)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 8)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3238)
        self.assertEqual(self.manifest["version"], "v3.05")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_07_beg.txt")
        self.assertEqual(self.manifest["next_scene"], "Babel BB-7 before battle")
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 40)
        row = next(line for line in self.index.splitlines() if "level_act33side_07_beg.txt" in line)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_07_beg.txt","partial_first_draft","32","0","0","0","8","40"])
        self.assertIn("40/222", self.readme)
        self.assertIn("№41, CN строка 114", self.readme)

if __name__ == "__main__":
    unittest.main()
