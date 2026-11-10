# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7BeforeV309(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_before_partial_ru_v309.json")
        self.previous = load("events/babel_bb7_before_partial_ru_v308.json")
        self.audit = load("reports/BABEL_BB7_BEFORE_SOURCE_AUDIT_v309.json")
        self.qa = load("reports/QA_BABEL_v309.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v309.json")
        self.index = (ROOT / "events/BABEL_INDEX_v309.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.09")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (200, 222, 22))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (201, 390))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 201)))
        self.assertEqual(len(self.doc["dialogues"]), 200)

    def test_previous_160_entries_are_preserved(self):
        self.assertEqual(self.doc["dialogues"][:160], self.previous["dialogues"])

    def test_new_segment_lines_and_kinds(self):
        expected = [347,348,349,350,351,352,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389]
        new = self.doc["dialogues"][160:]
        self.assertEqual([x["ordinal"] for x in new], list(range(161, 201)))
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = [x["kind"] for x in new]
        self.assertEqual((kinds.count("named"), kinds.count("multiline"), kinds.count("narration"), kinds.count("subtitle"), kinds.count("sticker")), (37,0,3,0,0))
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named":170,"multiline":2,"narration":20,"subtitle":8,"sticker":0})

    def test_russian_text_placeholders_and_markup(self):
        for item in self.doc["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
            self.assertEqual(item["text_ru"].count("<i>"), item["text_ru"].count("</i>"))
            self.assertEqual(item["text_ru"].count("<color="), item["text_ru"].count("</color>"))
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertIn("{@nickname}", by[198]["text_ru"])
        self.assertIn("<i>Шарда</i>", by[179]["text_ru"])

    def test_cn_primary_meaning_choices_and_speakers(self):
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[161]["speaker_cn"], "博士")
        self.assertEqual(by[163]["speaker_cn"], "特雷西斯")
        self.assertEqual(by[179]["speaker_cn"], "博士")
        self.assertEqual(by[185]["speaker_cn"], "特雷西斯")
        self.assertEqual(by[190]["speaker_cn"], "特雷西斯")
        self.assertIn("сдавшихся и дезертиров", by[185]["text_ru"])
        self.assertIn("последняя надежда", by[190]["text_ru"])
        self.assertIn("перестанет принадлежать сарказам", by[197]["text_ru"])
        self.assertFalse(by[190]["text_ru"].endswith("?"))

    def test_source_alignment_and_documented_differences(self):
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
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertFalse(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["segment_cn_en_markup_alignment_except_documented_difference"])
        markup = {x["ordinal"]:x for x in a["documented_source_markup_differences"]}
        meaning = {x["ordinal"]:x for x in a["documented_source_meaning_differences"]}
        self.assertEqual(markup[179]["source_line"], 368)
        self.assertEqual(meaning[185]["source_line"], 374)
        self.assertEqual(meaning[190]["source_line"], 379)
        self.assertEqual(meaning[197]["source_line"], 386)
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_readme_and_terms(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_07_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_07_beg.txt","partial_first_draft","170","2","20","0","8","200"])
        self.assertEqual(self.qa["scene_translated_text_entries"], 200)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 22)
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3398)
        self.assertEqual((self.qa["next_text_ordinal"],self.qa["next_text_source_line"]), (201,390))
        self.assertEqual(self.manifest["version"], "v3.09")
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 200)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3398)
        self.assertIn("200/222", self.readme)
        self.assertIn("№201, CN строка 390", self.readme)
        self.assertIn("Шард", self.terms)
        self.assertIn("Конфессарии", self.terms)
        self.assertIn("Лондиниум", self.terms)

if __name__ == "__main__":
    unittest.main()
