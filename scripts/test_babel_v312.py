# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7AfterV312(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_after_partial_ru_v312.json")
        self.previous = load("events/babel_bb7_after_partial_ru_v311.json")
        self.audit = load("reports/BABEL_BB7_AFTER_SOURCE_AUDIT_v312.json")
        self.qa = load("reports/QA_BABEL_v312.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v312.json")
        self.index = (ROOT / "events/BABEL_INDEX_v312.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.12")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (80, 149, 69))
        self.assertFalse(p["complete"])
        self.assertEqual(p["next_text_ordinal"], 81)
        self.assertEqual(p["next_text_source_line"], 214)
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 81)))

    def test_new_segment_source_line_map_and_kinds(self):
        expected = [125,126,127,129,131,134,135,139,141,143,145,147,149,151,152,154,156,158,160,161,162,164,166,176,185,186,187,188,189,191,192,193,195,196,198,199,200,201,202,211]
        new = self.doc["dialogues"][40:]
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = [x["kind"] for x in new]
        self.assertEqual((kinds.count("named"), kinds.count("narration"), kinds.count("multiline"), kinds.count("subtitle"), kinds.count("sticker")), (33, 7, 0, 0, 0))
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named": 70, "multiline": 0, "narration": 10, "subtitle": 0, "sticker": 0})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"], {"named": 55, "multiline": 0, "narration": 14, "subtitle": 0, "sticker": 0})

    def test_previous_40_entries_preserved(self):
        self.assertEqual(self.doc["dialogues"][:40], self.previous["dialogues"])
        self.assertTrue(self.doc["source_alignment"]["previous_entries_preserved"])

    def test_russian_text_is_clean_and_markup_balanced(self):
        for item in self.doc["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
            self.assertEqual(item["text_ru"].count("«"), item["text_ru"].count("»"))
            self.assertEqual(item["text_ru"].count("<i>"), item["text_ru"].count("</i>"))
            self.assertEqual(item["text_ru"].count("<color="), item["text_ru"].count("</color>"))

    def test_speakers_and_cn_primary_decisions(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[41]["speaker_cn"], "曼弗雷德")
        self.assertEqual(by[44]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by[68]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by[73]["speaker_cn"], "曼弗雷德")
        self.assertIn("С целой стены посыпались книги", by[61]["text_ru"])
        self.assertNotIn("судьбы", by[76]["text_ru"].lower())
        self.assertIn("в плавильную печь", by[68]["text_ru"])

    def test_source_hashes_and_alignment(self):
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "684c483e02f057552465a48707968e1566b74e6a")
        self.assertEqual(s["en_git_blob_sha1"], "4f340479e37a5ef752b0341fe7aefb3a16d8f817")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (384, 384))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (149, 149))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (235, 235))
        self.assertTrue(s["en_extra_terminal_newline"])
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_lines_match_exactly"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_and_readme(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_07_end.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side", "level_act33side_07_end.txt", "partial_first_draft", "70", "0", "10", "0", "0", "80"])
        self.assertEqual(self.qa["scene_translated_text_entries"], 80)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 69)
        self.assertEqual(self.qa["babel_completed_files"], 15)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 7)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3500)
        self.assertEqual(self.manifest["version"], "v3.12")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_07_end.txt")
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 80)
        self.assertEqual(self.manifest["translation_integrity"]["babel_not_started_files"], 7)
        self.assertIn("80/149", self.readme)
        self.assertIn("BB-7 после боя", self.readme)

    def test_audit_differences_and_next_boundary(self):
        meaning = self.audit["documented_meaning_differences"]
        self.assertEqual([x["ordinal"] for x in meaning], [8, 11, 21, 61, 76])
        self.assertEqual([x["ordinal"] for x in self.audit["documented_markup_differences"]], [22])
        self.assertEqual(self.audit["segment"]["next_ordinal"], 81)
        self.assertEqual(self.audit["segment"]["next_source_line"], 214)
        self.assertEqual(self.audit["source_totals"]["cn_control_commands"], 235)

if __name__ == "__main__":
    unittest.main()
