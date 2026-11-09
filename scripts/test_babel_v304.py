# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6AfterV304(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_after_ru_v304.json")
        self.previous = load("events/babel_bb6_after_partial_ru_v303.json")
        self.audit = load("reports/BABEL_BB6_AFTER_SOURCE_AUDIT_v304.json")
        self.qa = load("reports/QA_BABEL_v304.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v304.json")
        self.index = (ROOT / "events/BABEL_INDEX_v304.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_scene_complete_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.04")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (178,178,0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertIsNone(p["next_text_source_line"])
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1,179)))

    def test_previous_120_entries_preserved(self):
        self.assertEqual(len(self.previous["dialogues"]), 120)
        self.assertEqual(self.doc["dialogues"][:120], self.previous["dialogues"])

    def test_final_segment_positions_and_kinds(self):
        expected = [337,338,339,342,353,358,367,368,369,374,376,377,378,379,380,384,385,388,389,395,396,406,407,409,410,412,414,416,427,428,429,431,432,433,434,436,437,439,441,442,444,446,448,449,450,453,455,457,462,464,466,468,470,472,480,481,482,486]
        new = self.doc["dialogues"][120:]
        self.assertEqual(len(new), 58)
        self.assertEqual([x["ordinal"] for x in new], list(range(121,179)))
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = {}
        for item in self.doc["dialogues"]:
            kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(c) <= 0x9fff for c in item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
        self.assertEqual(kinds, {"named":132,"narration":23,"subtitle":20,"sticker":3})
        self.assertEqual([x["kind"] for x in new].count("named"), 39)
        self.assertEqual([x["kind"] for x in new].count("narration"), 9)
        self.assertEqual([x["kind"] for x in new].count("subtitle"), 9)
        self.assertEqual([x["kind"] for x in new].count("sticker"), 1)
        self.assertEqual(new[6]["speaker_cn"], "特蕾西娅")
        self.assertEqual(new[19]["speaker_cn"], "凯尔希")
        self.assertEqual(new[45]["speaker_cn"], "博士")

    def test_color_markup_and_lore_term(self):
        by_ordinal = {x["ordinal"]:x for x in self.doc["dialogues"]}
        for n in (126,175,176,177,178):
            self.assertTrue(by_ordinal[n]["text_ru"].startswith("<color=#000000>"))
            self.assertTrue(by_ordinal[n]["text_ru"].endswith("</color>"))
        self.assertIn("Сивилайт Этерна", by_ordinal[157]["text_ru"])
        self.assertIn("Короля Сарказов", by_ordinal[156]["text_ru"])
        self.assertEqual(by_ordinal[178]["kind"], "sticker")

    def test_source_hashes_alignment_and_completion_flags(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "56a05581ddc4364646998f6169cce72797f6834d")
        self.assertEqual(s["en_git_blob_sha1"], "0b839585231d08e1980894b6b1d98a9861c23759")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (492,493))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (178,178))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (314,314))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertTrue(a["cn_en_control_command_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_tag_sequence_match"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_subtitle_markup_alignment"])
        self.assertEqual(a["segment_ordinals"], [121,178])
        self.assertEqual(a["segment_new_text_positions"], 58)
        self.assertTrue(a["previous_entries_preserved"])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_chronology_readme(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 58)
        self.assertEqual(self.audit["translated_segment"]["cumulative_text_positions"], 178)
        self.assertTrue(self.audit["alignment"]["scene_complete"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 58)
        self.assertEqual(self.qa["scene_translated_text_entries"], 178)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 0)
        self.assertTrue(self.qa["scene_complete"])
        self.assertTrue(self.qa["previous_120_positions_preserved"])
        self.assertEqual(self.qa["babel_completed_files"], 14)
        self.assertEqual(self.qa["babel_partial_files"], 0)
        self.assertEqual(self.qa["babel_not_started_files"], 9)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"], 3198)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3198)
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_07_beg.txt")
        self.assertEqual(self.manifest["next_scene"], "Babel BB-7 before battle")
        self.assertNotIn("partial_scene_next_text_ordinal", self.manifest)
        row = next(line for line in self.index.splitlines() if "level_act33side_06_end.txt" in line)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_06_end.txt","first_draft_complete","132","0","23","3","20","178"])
        self.assertIn("178/178", self.readme)
        self.assertIn("14 из 23", self.readme)
        self.assertIn("level_act33side_07_beg.txt", self.readme)

if __name__ == "__main__":
    unittest.main()
