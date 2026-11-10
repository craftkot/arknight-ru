# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8BeforeV319(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_before_ru_v319.json")
        self.previous = load("events/babel_bb8_before_partial_ru_v318.json")
        self.audit = load("reports/BABEL_BB8_BEFORE_SOURCE_AUDIT_v319.json")
        self.qa = load("reports/QA_BABEL_v319.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v319.json")
        self.index = (ROOT / "events/BABEL_INDEX_v319.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_complete_progress_and_prefix_preservation(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.19")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (200, 200, 0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertIsNone(p["next_text_source_line"])
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 201)))
        self.assertEqual(self.doc["dialogues"][:160], self.previous["dialogues"])
        self.assertEqual(p["translated_kind_counts"], {"named":158,"multiline":2,"narration":40,"subtitle":0,"sticker":0})
        self.assertEqual(p["remaining_kind_counts"], {"named":0,"multiline":0,"narration":0,"subtitle":0,"sticker":0})

    def test_final_segment_line_map_and_kinds(self):
        expected = [467,468,469,471,477,480,486,495,496,497,498,499,500,501,502,504,506,532,534,535,536,546,547,550,552,554,555,556,559,560,561,579,580,581,582,583,584,585,586,587]
        segment = self.doc["dialogues"][160:]
        self.assertEqual([x["source_line"] for x in segment], expected)
        kinds = [x["kind"] for x in segment]
        self.assertEqual((kinds.count("named"),kinds.count("narration"),kinds.count("multiline")), (27,11,2))
        self.assertEqual(self.doc["source_alignment"]["segment_ordinals"], [161,200])
        self.assertEqual(self.doc["source_alignment"]["segment_source_lines"], expected)
        self.assertEqual((segment[4]["ordinal"],segment[4]["kind"],segment[4]["speaker_cn"]), (165,"multiline","奥达"))
        self.assertEqual((segment[5]["ordinal"],segment[5]["kind"],segment[5]["speaker_cn"]), (166,"multiline","奥达"))

    def test_russian_text_is_clean(self):
        for x in self.doc["dialogues"]:
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", x["text_ru"]))
            self.assertNotIn(chr(10), x["text_ru"])
            self.assertNotIn(chr(13), x["text_ru"])
            self.assertEqual(x["text_ru"].count("«"), x["text_ru"].count("»"))

    def test_speakers_and_cn_primary_decisions(self):
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[161]["speaker_cn"], "“疤眼”")
        self.assertEqual(by[165]["speaker_cn"], "奥达")
        self.assertEqual(by[167]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by[181]["text_ru"], "«Скарай»… ты способен увидеть пустоту?")
        self.assertIn("наркоман", by[188]["text_ru"])
        self.assertIn("«Скарай»", by[188]["text_ru"])
        self.assertIn("сумеречная дымка", by[182]["text_ru"])
        self.assertNotIn("густой", by[182]["text_ru"])
        self.assertEqual(by[196]["text_ru"], "Теперь ты видишь смерть?")
        self.assertIn("Ш-ш-ш", by[165]["text_ru"])
        self.assertIn("Ш-ш-ш", by[166]["text_ru"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "61daf6c0beeecfb442fd84a7dad26ea1110dac5b")
        self.assertEqual(s["en_git_blob_sha1"], "cbf456ffc623a5865f193132fb076857ec2e6c1a")
        self.assertEqual((s["cn_line_count"],s["en_line_count"],s["cn_text_total"],s["en_text_total"]), (594,594,200,200))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]), (394,394))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertFalse(a["cn_en_control_command_lines_match_exactly"])
        self.assertEqual(a["cn_en_control_command_difference_count"], 2)
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertFalse(a["segment_cn_en_multiline_payloads_match"])
        self.assertEqual(a["segment_cn_en_multiline_payload_difference_source_lines"], [477,480])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_records_differences(self):
        self.assertEqual(self.audit["segment"]["ordinals"], [161,200])
        self.assertEqual(self.audit["segment"]["text_positions"], 40)
        self.assertEqual([x["ordinal"] for x in self.audit["documented_multiline_text_differences"]], [165,166])
        self.assertEqual([x["source_line"] for x in self.audit["documented_control_command_differences"]], [435,459])
        self.assertEqual([x["ordinal"] for x in self.audit["documented_punctuation_differences"]], [181,188])
        self.assertIn(182,[x["ordinal"] for x in self.audit["documented_meaning_differences"]])
        self.assertIn(196,[x["ordinal"] for x in self.audit["documented_meaning_differences"]])
        self.assertTrue(self.audit["scene_complete"])
        self.assertFalse(self.audit["game_behavior_verified"])

    def test_index_manifest_qa_readme_and_glossary(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_08_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_08_beg.txt","first_draft_complete","158","2","40","0","0","200"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 200)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 0)
        self.assertEqual(self.qa["babel_completed_files"], 17)
        self.assertEqual(self.qa["babel_partial_files"], 0)
        self.assertEqual(self.qa["babel_not_started_files"], 6)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"], 3769)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3769)
        self.assertEqual(self.manifest["version"], "v3.19")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_08_end.txt")
        self.assertEqual((self.manifest["next_text_ordinal"],self.manifest["next_text_source_line"]), (1,15))
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3769)
        self.assertIn("BB-8 после боя", self.readme)
        self.assertIn("Скарай", self.terms)

if __name__ == "__main__":
    unittest.main()
