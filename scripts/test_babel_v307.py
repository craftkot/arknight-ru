# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7BeforeV307(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_before_partial_ru_v307.json")
        self.audit = load("reports/BABEL_BB7_BEFORE_SOURCE_AUDIT_v307.json")
        self.qa = load("reports/QA_BABEL_v307.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v307.json")
        self.index = (ROOT / "events/BABEL_INDEX_v307.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.07")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (120, 222, 102))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (121, 304))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 121)))
        self.assertEqual(len(self.doc["dialogues"]), 120)

    def test_new_segment_source_lines_and_kinds(self):
        expected = [218,219,221,222,224,226,228,230,232,234,236,242,244,247,249,251,252,253,259,261,262,269,270,271,280,281,282,285,286,287,288,289,290,291,292,293,300,301,302,303]
        new = self.doc["dialogues"][80:]
        self.assertEqual([x["ordinal"] for x in new], list(range(81, 121)))
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = [x["kind"] for x in new]
        self.assertEqual((kinds.count("named"), kinds.count("multiline"), kinds.count("narration"), kinds.count("subtitle"), kinds.count("sticker")), (29, 2, 9, 0, 0))
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named":101,"multiline":2,"narration":9,"subtitle":8,"sticker":0})

    def test_text_is_russian_and_markup_balanced(self):
        for item in self.doc["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
            self.assertEqual(item["text_ru"].count("<i>"), item["text_ru"].count("</i>"))
        self.assertIn("<i>Доктор</i>", self.doc["dialogues"][115]["text_ru"])
        self.assertIn("<i>героями</i>", self.doc["dialogues"][118]["text_ru"])

    def test_speakers_and_translation_choices(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[81]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by[83]["kind"], "multiline")
        self.assertEqual(by[84]["kind"], "multiline")
        self.assertEqual(by[108]["speaker_cn"], "？？？")
        self.assertEqual(by[117]["speaker_cn"], "特雷西斯")
        self.assertIn("Хёдерера", by[81]["text_ru"])
        self.assertIn("птицезверь", by[107]["text_ru"])
        self.assertEqual(self.audit["alignment"]["documented_meaning_difference"]["ordinal"], 127)
        self.assertIn("Военная комиссия — её враг", self.audit["alignment"]["documented_source_meaning_difference"]["ru"])

    def test_source_alignment_and_differences(self):
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "605fede5533907ce926d038129da2abb2af57af7")
        self.assertEqual(s["en_git_blob_sha1"], "63c0f520b4f0de80ea34b4dd0afbbc4cb2df9f5b")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (434, 434))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (222, 222))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (212, 212))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_lines_match_exactly"])
        self.assertTrue(a["en_extra_terminal_newline"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertFalse(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["segment_cn_en_markup_alignment_except_documented_difference"])
        self.assertEqual(a["documented_source_meaning_difference"]["ordinal"], 127)
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_readme_and_glossary(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_07_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_07_beg.txt","partial_first_draft","101","2","9","0","8","120"])
        self.assertEqual(self.qa["scene_translated_text_entries"], 120)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 102)
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3318)
        self.assertEqual((self.qa["next_text_ordinal"], self.qa["next_text_source_line"]), (121,304))
        self.assertEqual(self.manifest["version"], "v3.07")
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 120)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3318)
        self.assertIn("120/222", self.readme)
        self.assertIn("№121, CN строка 304", self.readme)
        self.assertIn("Хёдерер", self.terms)
        self.assertIn("Терезис", self.terms)
        self.assertIn("птицезверь", self.terms)

if __name__ == "__main__":
    unittest.main()
