# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7BeforeV306(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_before_partial_ru_v306.json")
        self.audit = load("reports/BABEL_BB7_BEFORE_SOURCE_AUDIT_v306.json")
        self.qa = load("reports/QA_BABEL_v306.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v306.json")
        self.index = (ROOT / "events/BABEL_INDEX_v306.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.06")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (80, 222, 142))
        self.assertFalse(p["complete"])
        self.assertEqual(p["next_text_ordinal"], 81)
        self.assertEqual(p["next_text_source_line"], 218)
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 81)))
        self.assertEqual(len(self.doc["dialogues"]), 80)

    def test_new_segment_source_lines_and_kinds(self):
        expected = [114,115,116,117,118,119,136,138,140,141,143,145,147,149,151,152,153,154,155,156,159,163,164,167,171,173,175,177,178,185,186,188,190,191,193,194,200,207,213,216]
        new = self.doc["dialogues"][40:]
        self.assertEqual([x["ordinal"] for x in new], list(range(41,81)))
        self.assertEqual([x["source_line"] for x in new], expected)
        self.assertTrue(all(x["kind"] == "named" for x in new))
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named":72,"multiline":0,"narration":0,"subtitle":8,"sticker":0})

    def test_text_is_russian_and_has_no_embedded_newlines(self):
        for item in self.doc["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
        self.assertIn("<i>человеком</i>", self.doc["dialogues"][41]["text_ru"])

    def test_speaker_tags_and_documented_source_differences(self):
        by_ordinal = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by_ordinal[41]["speaker_cn"], "普瑞赛斯")
        self.assertEqual(by_ordinal[47]["speaker_cn"], "Scout")
        self.assertEqual(by_ordinal[51]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by_ordinal[61]["speaker_cn"], "凯尔希")
        self.assertEqual(by_ordinal[78]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by_ordinal[79]["speaker_cn"], "伊内丝&W")
        self.assertEqual(self.audit["alignment"]["documented_speaker_tag_difference"]["ordinal"], 79)
        self.assertEqual(self.audit["alignment"]["documented_markup_difference"]["ordinal"], 42)
        self.assertFalse(self.audit["alignment"]["segment_cn_en_speaker_tags_align"])
        self.assertTrue(self.audit["alignment"]["segment_cn_en_speaker_tags_align_except_documented_difference"])
        self.assertFalse(self.audit["alignment"]["segment_cn_en_markup_alignment"])
        self.assertTrue(self.audit["alignment"]["segment_cn_en_markup_alignment_except_documented_difference"])

    def test_markup_and_source_invariants(self):
        text = self.doc["dialogues"][41]["text_ru"]
        self.assertEqual(text.count("<i>"), 1)
        self.assertEqual(text.count("</i>"), 1)
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "605fede5533907ce926d038129da2abb2af57af7")
        self.assertEqual(s["en_git_blob_sha1"], "63c0f520b4f0de80ea34b4dd0afbbc4cb2df9f5b")
        self.assertEqual((s["cn_line_count"],s["en_line_count"]), (434,434))
        self.assertEqual((s["cn_text_total"],s["en_text_total"]), (222,222))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]), (212,212))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_lines_match_exactly"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_readme_and_glossary(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_07_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_07_beg.txt","partial_first_draft","72","0","0","0","8","80"])
        self.assertEqual(self.qa["scene_translated_text_entries"], 80)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 142)
        self.assertEqual(self.qa["new_named_ru"], 40)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3278)
        self.assertEqual(self.qa["next_text_ordinal"], 81)
        self.assertEqual(self.qa["next_text_source_line"], 218)
        self.assertEqual(self.manifest["version"], "v3.06")
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 80)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3278)
        self.assertIn("80/222", self.readme)
        self.assertIn("№81, CN строка 218", self.readme)
        self.assertIn("нахцереры", self.terms)
        self.assertIn("Дук'араэль", self.terms)
        self.assertIn("Розовый берег", self.terms)

if __name__ == "__main__":
    unittest.main()
