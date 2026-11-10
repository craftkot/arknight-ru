# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8BeforeV317(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_before_partial_ru_v317.json")
        self.previous = load("events/babel_bb8_before_partial_ru_v316.json")
        self.audit = load("reports/BABEL_BB8_BEFORE_SOURCE_AUDIT_v317.json")
        self.qa = load("reports/QA_BABEL_v317.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v317.json")
        self.index = (ROOT / "events/BABEL_INDEX_v317.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_progress_and_prefix_preservation(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.17")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (120, 200, 80))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (121, 330))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 121)))
        self.assertEqual(self.doc["dialogues"][:80], self.previous["dialogues"])
        self.assertEqual(p["translated_kind_counts"], {"named": 96, "multiline": 0, "narration": 24, "subtitle": 0, "sticker": 0})
        self.assertEqual(p["remaining_kind_counts"], {"named": 62, "multiline": 2, "narration": 16, "subtitle": 0, "sticker": 0})

    def test_new_segment_line_map_and_kinds(self):
        expected = [204,205,207,208,210,212,213,215,225,226,227,228,238,244,247,248,249,260,261,273,274,286,287,288,289,290,291,301,302,308,314,316,317,319,321,322,324,326,327,328]
        segment = self.doc["dialogues"][80:]
        self.assertEqual([x["source_line"] for x in segment], expected)
        kinds = [x["kind"] for x in segment]
        self.assertEqual((kinds.count("named"), kinds.count("narration"), kinds.count("multiline")), (35, 5, 0))
        self.assertEqual(self.doc["source_alignment"]["segment_ordinals"], [81, 120])
        self.assertEqual(self.doc["source_alignment"]["segment_source_lines"], expected)
        self.assertTrue(self.doc["source_alignment"]["segment_cn_en_control_commands_match_exactly"])

    def test_russian_text_is_clean(self):
        for x in self.doc["dialogues"]:
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", x["text_ru"]))
            self.assertNotIn(chr(10), x["text_ru"])
            self.assertNotIn(chr(13), x["text_ru"])
            self.assertEqual(x["text_ru"].count("«"), x["text_ru"].count("»"))

    def test_speakers_and_cn_primary_wording(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[83]["speaker_cn"], "尤莉叶")
        self.assertEqual(by[93]["speaker_cn"], "博士")
        self.assertEqual(by[94]["speaker_cn"], "凯尔希")
        self.assertEqual(by[111]["speaker_cn"], "特蕾西娅")
        self.assertIn("себя калечить", by[83]["text_ru"])
        self.assertIn("Короля Сарказов", by[84]["text_ru"])
        self.assertIn("зал совета", by[106]["text_ru"])
        self.assertIn("вместе с луной", by[106]["text_ru"])
        diff = {x["ordinal"]: x for x in self.audit["documented_meaning_differences"]}
        self.assertIn("pyramid", diff[89]["en"].lower())
        self.assertIn("Горнило", self.terms)

    def test_source_hashes_and_full_scene_alignment(self):
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "61daf6c0beeecfb442fd84a7dad26ea1110dac5b")
        self.assertEqual(s["en_git_blob_sha1"], "cbf456ffc623a5865f193132fb076857ec2e6c1a")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (594, 594))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (200, 200))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (394, 394))
        self.assertTrue(s["en_extra_terminal_newline"])
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertFalse(a["cn_en_control_command_lines_match_exactly"])
        self.assertEqual(a["cn_en_control_command_difference_count"], 2)
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_and_readme(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_08_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_08_beg.txt","partial_first_draft","96","0","24","0","0","120"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 120)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 80)
        self.assertEqual(self.qa["scene_remaining_named"], 62)
        self.assertEqual(self.qa["scene_remaining_multiline"], 2)
        self.assertEqual(self.qa["babel_completed_files"], 16)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 6)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3689)
        self.assertEqual(self.manifest["version"], "v3.17")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_08_beg.txt")
        self.assertEqual((self.manifest["next_text_ordinal"], self.manifest["next_text_source_line"]), (121, 330))
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3689)
        self.assertIn("120/200", self.readme)
        self.assertIn("№121, CN строка 330", self.readme)

    def test_audit_differences_and_multiline_positions(self):
        expected = [19,21,27,39,57,61,65,69,71,77,80,83,84,89,97,103,106]
        self.assertEqual([x["ordinal"] for x in self.audit["documented_meaning_differences"]], expected)
        self.assertEqual([x["source_line"] for x in self.audit["documented_control_command_differences"]], [435,459])
        self.assertEqual([x["source_line"] for x in self.audit["documented_multiline_text_differences"]], [477,480])
        self.assertEqual(self.audit["segment"]["ordinals"], [81,120])
        self.assertEqual(self.audit["segment"]["next_ordinal"], 121)
        self.assertEqual(self.audit["segment"]["next_source_line"], 330)
        self.assertFalse(self.audit["scene_complete"])
        self.assertFalse(self.audit["game_behavior_verified"])

if __name__ == "__main__":
    unittest.main()
