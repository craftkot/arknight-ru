# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6V300(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_before_ru_v300.json")
        self.old = load("events/babel_bb6_before_partial_ru_v299.json")
        self.audit = load("reports/BABEL_BB6_BEFORE_SOURCE_AUDIT_v300.json")
        self.qa = load("reports/QA_BABEL_v300.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v300.json")
        self.index = (ROOT / "events/BABEL_INDEX_v300.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.terminology = (ROOT / "docs/CN_EN_RU_TERMINOLOGY_REVIEW.tsv").read_text(encoding="utf-8")

    def test_scene_complete_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.00")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (258, 258, 0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 259)))

    def test_previous_228_entries_preserved(self):
        for old in self.old["dialogues"]:
            self.assertEqual(self.doc["dialogues"][old["ordinal"] - 1], old)

    def test_final_segment_source_positions_and_kinds(self):
        expected = [695,697,699,704,705,707,709,711,712,714,716,717,718,726,731,739,741,743,745,746,750,751,752,755,756,758,760,761,762,763]
        new = self.doc["dialogues"][228:]
        self.assertEqual(len(new), 30)
        self.assertEqual([x["source_line"] for x in new], expected)
        self.assertEqual([x["ordinal"] for x in new], list(range(229,259)))
        kinds = {}
        for x in self.doc["dialogues"]:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(c) <= 0x9fff for c in x["text_ru"]))
            self.assertNotIn(chr(10), x["text_ru"])
            self.assertNotIn(chr(13), x["text_ru"])
        self.assertEqual(kinds, {"named":209,"multiline":11,"narration":36,"subtitle":2})
        self.assertEqual(new[0]["speaker_cn"], "博士")
        self.assertEqual(new[1]["speaker_cn"], "凯尔希")
        self.assertEqual(new[3]["speaker_cn"], "特蕾西娅")
        self.assertEqual(new[13]["kind"], "subtitle")
        self.assertEqual(new[14]["kind"], "subtitle")
        self.assertEqual(new[-1]["speaker_cn"], "博士")

    def test_subtitle_markup_and_terminology(self):
        subtitle = self.doc["dialogues"][242]["text_ru"]
        self.assertIn("<color=#000000>", subtitle)
        self.assertTrue(subtitle.endswith("</color>"))
        self.assertIn("Сивилайт Этерна", self.doc["dialogues"][252]["text_ru"])
        self.assertIn("Civilight Eterna — Сивилайт Этерна", self.terms)
        self.assertIn("文明的存续\tCivilight Eterna\tСивилайт Этерна", self.terminology)
        self.assertIn("King of Sarkaz", self.terminology)

    def test_source_alignment_and_hashes(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual((s["cn_git_blob_sha1"], s["en_git_blob_sha1"]), ("0fa57f8b2c4647c06bce0ba73008798d340a781c", "47a63283cb5d1c42e205f6bcebbf1e9cc134ac03"))
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (770,771))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (258,258))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (512,512))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_subtitle_markup_preserved"])
        self.assertEqual(a["segment_new_text_positions"], 30)
        self.assertEqual(a["segment_new_named"], 23)
        self.assertEqual(a["segment_new_narration"], 5)
        self.assertEqual(a["segment_new_subtitle"], 2)
        self.assertTrue(a["previous_228_entries_preserved"])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_chronology_readme(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 30)
        self.assertTrue(self.audit["translated_segment"]["previous_228_preserved"])
        self.assertTrue(self.audit["translated_segment"]["scene_complete"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 30)
        self.assertEqual(self.qa["scene_ru_text_entries"], 258)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 0)
        self.assertEqual(self.qa["babel_completed_files"], 13)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"], 3020)
        self.assertEqual(self.qa["babel_partial_ru_text_entries"], 0)
        row = next(line for line in self.index.splitlines() if "level_act33side_06_beg.txt" in line)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_06_beg.txt","first_draft_complete","209","11","36","0","2","258"])
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_06_end.txt")
        self.assertEqual(self.manifest["translation_integrity"]["babel_completed_files"], 13)
        self.assertEqual(self.manifest["translation_integrity"]["babel_completed_ru_text_entries"], 3020)
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 0)
        self.assertIn("258/258", self.readme)
        self.assertIn("level_act33side_06_end.txt", self.readme)

if __name__ == "__main__":
    unittest.main()
