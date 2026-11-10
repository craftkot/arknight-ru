# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7AfterV314(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_after_ru_v314.json")
        self.previous = load("events/babel_bb7_after_partial_ru_v313.json")
        self.audit = load("reports/BABEL_BB7_AFTER_SOURCE_AUDIT_v314.json")
        self.qa = load("reports/QA_BABEL_v314.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v314.json")
        self.index = (ROOT / "events/BABEL_INDEX_v314.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_scene_is_complete_first_draft(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.14")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (149, 149, 0))
        self.assertTrue(p["complete"])
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 150)))
        self.assertEqual(p["translated_kind_counts"], {"named": 125, "multiline": 0, "narration": 24, "subtitle": 0, "sticker": 0})
        self.assertEqual(p["remaining_kind_counts"], {"named": 0, "multiline": 0, "narration": 0, "subtitle": 0, "sticker": 0})

    def test_final_segment_source_line_map_and_kinds(self):
        expected = [312,313,315,316,318,319,320,322,324,326,328,337,338,339,340,351,353,354,355,357,362,363,364,366,367,373,375,376,377]
        new = self.doc["dialogues"][120:]
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = [x["kind"] for x in new]
        self.assertEqual((kinds.count("named"), kinds.count("narration"), kinds.count("multiline"), kinds.count("subtitle"), kinds.count("sticker")), (21,8,0,0,0))

    def test_previous_120_entries_preserved(self):
        self.assertEqual(self.doc["dialogues"][:120], self.previous["dialogues"])
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

    def test_speakers_and_final_story_content(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[121]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[123]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by[137]["speaker_cn"], "维多利亚士兵")
        self.assertEqual(by[141]["speaker_cn"], "特雷西斯")
        self.assertIn("убеждения многих людей", by[121]["text_ru"])
        self.assertIn("нежелание расставаться", by[135]["text_ru"])
        self.assertIn("порохового дыма", by[147]["text_ru"])
        self.assertIn("тёмная туча", by[149]["text_ru"])

    def test_source_hashes_and_alignment(self):
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "684c483e02f057552465a48707968e1566b74e6a")
        self.assertEqual(s["en_git_blob_sha1"], "4f340479e37a5ef752b0341fe7aefb3a16d8f817")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (384,384))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (149,149))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (235,235))
        self.assertTrue(s["en_extra_terminal_newline"])
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_lines_match_exactly"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_and_readme(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_07_end.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_07_end.txt","first_draft_complete","125","0","24","0","0","149"])
        self.assertEqual(self.qa["scene_translated_text_entries"],149)
        self.assertEqual(self.qa["scene_remaining_text_entries"],0)
        self.assertEqual(self.qa["babel_completed_files"],16)
        self.assertEqual(self.qa["babel_partial_files"],0)
        self.assertEqual(self.qa["babel_not_started_files"],7)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"],3569)
        self.assertEqual(self.manifest["version"],"v3.14")
        self.assertEqual(self.manifest["next_file"],"activities/act33side/level_act33side_08_beg.txt")
        self.assertEqual(self.manifest["translation_integrity"]["babel_completed_files"],16)
        self.assertEqual(self.manifest["translation_integrity"]["babel_completed_ru_text_entries"],3569)
        self.assertIn("149/149",self.readme)
        self.assertIn("BB-8 до боя",self.readme)
        self.assertIn("120/149",self.readme)

    def test_audit_differences_and_next_scene(self):
        meaning = self.audit["documented_meaning_differences"]
        self.assertEqual([x["ordinal"] for x in meaning],[8,11,21,61,76,100,110,120,121])
        self.assertEqual([x["ordinal"] for x in self.audit["documented_markup_differences"]],[22])
        self.assertEqual(self.audit["segment"]["ordinals"],[121,149])
        self.assertIsNone(self.audit["segment"]["next_ordinal"])
        self.assertEqual(self.audit["source_totals"]["cn_control_commands"],235)
        self.assertTrue(self.audit["scene_complete"])
        self.assertFalse(self.audit["game_behavior_verified"])

if __name__ == "__main__":
    unittest.main()
