# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7AfterV311(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_after_partial_ru_v311.json")
        self.audit = load("reports/BABEL_BB7_AFTER_SOURCE_AUDIT_v311.json")
        self.qa = load("reports/QA_BABEL_v311.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v311.json")
        self.index = (ROOT / "events/BABEL_INDEX_v311.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.11")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (40, 149, 109))
        self.assertFalse(p["complete"])
        self.assertEqual(p["next_text_ordinal"], 41)
        self.assertEqual(p["next_text_source_line"], 125)
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 41)))

    def test_source_line_map_and_kinds(self):
        expected = [11,12,23,25,27,29,31,32,34,36,38,40,42,43,45,47,49,50,52,53,54,55,57,59,61,62,64,65,80,82,84,85,89,97,103,110,116,118,119,121]
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], expected)
        kinds = [x["kind"] for x in self.doc["dialogues"]]
        self.assertEqual((kinds.count("named"), kinds.count("narration"), kinds.count("multiline"), kinds.count("subtitle"), kinds.count("sticker")), (37, 3, 0, 0, 0))
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named": 37, "multiline": 0, "narration": 3, "subtitle": 0, "sticker": 0})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"], {"named": 88, "multiline": 0, "narration": 21, "subtitle": 0, "sticker": 0})

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
        self.assertEqual(by[3]["speaker_cn"], "曼弗雷德")
        self.assertEqual(by[4]["speaker_cn"], "特雷西斯")
        self.assertEqual(by[30]["speaker_cn"], "军事委员会卫士")
        self.assertEqual(by[37]["speaker_cn"], "阿斯卡纶")
        self.assertIn("разобщённость", by[21]["text_ru"])
        self.assertIn("«слава»", by[22]["text_ru"])
        self.assertFalse(by[11]["text_ru"].startswith("Понимаю"))

    def test_source_hashes_and_alignment(self):
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "684c483e02f057552465a48707968e1566b74e6a")
        self.assertEqual(s["en_git_blob_sha1"], "4f340479e37a5ef752b0341fe7aefb3a16d8f817")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (384, 384))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (149, 149))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (235, 235))
        self.assertIn("The 235 command lines match exactly.", s["version_difference"])
        self.assertTrue(s["en_extra_terminal_newline"])
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_lines_match_exactly"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_and_readme(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_07_end.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side", "level_act33side_07_end.txt", "partial_first_draft", "37", "0", "3", "0", "0", "40"])
        self.assertEqual(self.qa["scene_translated_text_entries"], 40)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 109)
        self.assertEqual(self.qa["babel_completed_files"], 15)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 7)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3460)
        self.assertEqual(self.manifest["version"], "v3.11")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_07_end.txt")
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 40)
        self.assertEqual(self.manifest["translation_integrity"]["babel_not_started_files"], 7)
        self.assertIn("40/149", self.readme)
        self.assertIn("BB-7 после боя", self.readme)
        self.assertIn("Ascalon / 阿斯卡纶", self.terms)
        self.assertIn("Cavendish / 卡文迪许", self.terms)

    def test_audit_differences_and_next_boundary(self):
        meaning = self.audit["documented_meaning_differences"]
        self.assertEqual([x["ordinal"] for x in meaning], [8, 11, 21])
        self.assertEqual([x["ordinal"] for x in self.audit["documented_markup_differences"]], [22])
        self.assertEqual(self.audit["segment"]["next_ordinal"], 41)
        self.assertEqual(self.audit["segment"]["next_source_line"], 125)

if __name__ == "__main__":
    unittest.main()
