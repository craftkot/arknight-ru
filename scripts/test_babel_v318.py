# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8BeforeV318(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_before_partial_ru_v318.json")
        self.previous = load("events/babel_bb8_before_partial_ru_v317.json")
        self.audit = load("reports/BABEL_BB8_BEFORE_SOURCE_AUDIT_v318.json")
        self.qa = load("reports/QA_BABEL_v318.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v318.json")
        self.index = (ROOT / "events/BABEL_INDEX_v318.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_progress_and_prefix_preservation(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.18")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (160, 200, 40))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (161, 467))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 161)))
        self.assertEqual(self.doc["dialogues"][:120], self.previous["dialogues"])
        self.assertEqual(p["translated_kind_counts"], {"named": 131, "multiline": 0, "narration": 29, "subtitle": 0, "sticker": 0})
        self.assertEqual(p["remaining_kind_counts"], {"named": 27, "multiline": 2, "narration": 11, "subtitle": 0, "sticker": 0})

    def test_new_segment_line_map_and_kinds(self):
        expected = [330,332,334,335,337,339,340,342,343,345,347,349,350,352,354,356,366,369,375,377,378,380,382,384,387,389,400,401,403,417,424,425,427,429,430,431,432,462,463,465]
        segment = self.doc["dialogues"][120:]
        self.assertEqual([x["source_line"] for x in segment], expected)
        kinds = [x["kind"] for x in segment]
        self.assertEqual((kinds.count("named"), kinds.count("narration"), kinds.count("multiline")), (35, 5, 0))
        self.assertEqual(self.doc["source_alignment"]["segment_ordinals"], [121, 160])
        self.assertEqual(self.doc["source_alignment"]["segment_source_lines"], expected)

    def test_russian_text_is_clean(self):
        for x in self.doc["dialogues"]:
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", x["text_ru"]))
            self.assertNotIn(chr(10), x["text_ru"])
            self.assertNotIn(chr(13), x["text_ru"])
            self.assertEqual(x["text_ru"].count("«"), x["text_ru"].count("»"))

    def test_speakers_and_cn_primary_wording(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[122]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[123]["speaker_cn"], "博士")
        self.assertEqual(by[137]["kind"], "narration")
        self.assertEqual(by[138]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by[139]["speaker_cn"], "奥达")
        self.assertEqual(by[149]["speaker_cn"], "？？？")
        self.assertEqual(by[151]["speaker_cn"], "“疤眼”")
        self.assertIn("Короля Сарказов", by[123]["text_ru"])
        self.assertIn("слишком хитро", by[134]["text_ru"])
        self.assertIn("зацепки", by[145]["text_ru"])
        self.assertNotIn("как трус", by[153]["text_ru"])
        self.assertIn("Рынок шрамов", by[157]["text_ru"])

    def test_source_hashes_and_full_scene_alignment(self):
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "61daf6c0beeecfb442fd84a7dad26ea1110dac5b")
        self.assertEqual(s["en_git_blob_sha1"], "cbf456ffc623a5865f193132fb076857ec2e6c1a")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (594, 594))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (200, 200))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (394, 394))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertFalse(a["cn_en_control_command_lines_match_exactly"])
        self.assertEqual(a["cn_en_control_command_difference_count"], 2)
        self.assertFalse(a["segment_cn_en_control_commands_match_exactly"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [435, 459])
        self.assertFalse(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_differences_and_multiline_positions(self):
        self.assertEqual([x["ordinal"] for x in self.audit["documented_meaning_differences"]][-6:], [123,134,135,145,153,157])
        self.assertEqual(self.audit["documented_markup_differences"][-1]["ordinal"], 157)
        self.assertEqual([x["source_line"] for x in self.audit["documented_control_command_differences"]], [435,459])
        self.assertEqual(self.audit["segment"]["ordinals"], [121,160])
        self.assertEqual(self.audit["segment"]["next_ordinal"], 161)
        self.assertEqual(self.audit["segment"]["next_source_line"], 467)
        self.assertFalse(self.audit["segment"]["cn_en_control_commands_match_exactly"])
        self.assertFalse(self.audit["segment"]["cn_en_markup_alignment"])
        self.assertFalse(self.audit["scene_complete"])

    def test_index_manifest_qa_and_readme(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_08_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_08_beg.txt","partial_first_draft","131","0","29","0","0","160"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 160)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 40)
        self.assertEqual(self.qa["scene_remaining_named"], 27)
        self.assertEqual(self.qa["scene_remaining_multiline"], 2)
        self.assertEqual(self.qa["babel_completed_files"], 16)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 6)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3729)
        self.assertEqual(self.manifest["version"], "v3.18")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_08_beg.txt")
        self.assertEqual((self.manifest["next_text_ordinal"], self.manifest["next_text_source_line"]), (161,467))
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3729)
        self.assertIn("160/200", self.readme)
        self.assertIn("№161, CN строка 467", self.readme)

if __name__ == "__main__":
    unittest.main()
