# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6AfterV302(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_after_partial_ru_v302.json")
        self.old = load("events/babel_bb6_after_partial_ru_v301.json")
        self.audit = load("reports/BABEL_BB6_AFTER_SOURCE_AUDIT_v302.json")
        self.qa = load("reports/QA_BABEL_v302.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v302.json")
        self.index = (ROOT / "events/BABEL_INDEX_v302.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.review = (ROOT / "docs/CN_EN_RU_TERMINOLOGY_REVIEW.tsv").read_text(encoding="utf-8")

    def test_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.02")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (80, 178, 98))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (81, 219))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 81)))

    def test_previous_entries_preserved_except_documented_correction(self):
        self.assertEqual(len(self.old["dialogues"]), 40)
        for i, old in enumerate(self.old["dialogues"]):
            expected = dict(old)
            if i == 39:
                expected["text_ru"] = "С момента твоего путешествия в Рим Биллитон и до гражданской войны сарказов ты ни на миг не позволял себе расслабиться."
            self.assertEqual(self.doc["dialogues"][i], expected)
        self.assertEqual(self.doc["dialogues"][39]["source_line"], 128)

    def test_new_segment_source_positions_and_kinds(self):
        expected = [129,131,132,134,135,147,148,150,156,158,160,162,164,166,168,170,172,173,174,176,178,180,182,183,184,186,187,189,190,192,194,196,198,200,202,204,206,216,217,218]
        new = self.doc["dialogues"][40:]
        self.assertEqual(len(new), 40)
        self.assertEqual([x["ordinal"] for x in new], list(range(41,81)))
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = {}
        for item in self.doc["dialogues"]:
            kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(c) <= 0x9fff for c in item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
        self.assertEqual(kinds, {"named":65,"narration":11,"subtitle":4})
        self.assertEqual([x["kind"] for x in new].count("named"), 35)
        self.assertEqual([x["kind"] for x in new].count("narration"), 2)
        self.assertEqual([x["kind"] for x in new].count("subtitle"), 3)
        self.assertEqual(new[0]["speaker_cn"], "凯尔希")
        self.assertEqual(new[5]["kind"], "narration")
        self.assertEqual(new[7]["speaker_cn"], "博士")
        self.assertEqual(new[-3]["kind"], "subtitle")
        self.assertEqual(new[-1]["kind"], "subtitle")

    def test_source_hashes_and_alignment(self):
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
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_subtitle_markup_alignment"])
        self.assertEqual(a["segment_ordinals"], [41,80])
        self.assertEqual(a["segment_new_text_positions"], 40)
        self.assertTrue(a["previous_entries_preserved_except_documented_terminology_correction"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_chronology_readme_and_terms(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 40)
        self.assertEqual(self.audit["translated_segment"]["cumulative_text_positions"], 80)
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 80)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 98)
        self.assertEqual(self.qa["babel_completed_files"], 13)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 9)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3100)
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_06_end.txt")
        self.assertEqual(self.manifest["partial_scene_next_text_ordinal"], 81)
        self.assertEqual(self.manifest["partial_scene_next_source_line"], 219)
        row = next(line for line in self.index.splitlines() if "level_act33side_06_end.txt" in line)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_06_end.txt","partial_first_draft","65","0","11","0","4","80"])
        self.assertIn("80/178", self.readme)
        for term in ["Клоужер","Ручейный зверь","Вьючный зверь","Рим Биллитон","Каздель","Катастрофа"]:
            self.assertIn(term, self.terms)
            self.assertIn(term, self.review)
        self.assertIn("Рим Биллитон", self.doc["dialogues"][39]["text_ru"])

if __name__ == "__main__":
    unittest.main()
