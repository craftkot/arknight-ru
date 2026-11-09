# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6AfterV303(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_after_partial_ru_v303.json")
        self.previous = load("events/babel_bb6_after_partial_ru_v302.json")
        self.audit = load("reports/BABEL_BB6_AFTER_SOURCE_AUDIT_v303.json")
        self.qa = load("reports/QA_BABEL_v303.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v303.json")
        self.index = (ROOT / "events/BABEL_INDEX_v303.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.review = (ROOT / "docs/CN_EN_RU_TERMINOLOGY_REVIEW.tsv").read_text(encoding="utf-8")

    def test_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.03")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (120, 178, 58))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (121, 337))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 121)))

    def test_previous_80_entries_preserved(self):
        self.assertEqual(len(self.previous["dialogues"]), 80)
        self.assertEqual(self.doc["dialogues"][:80], self.previous["dialogues"])

    def test_new_segment_positions_and_kinds(self):
        expected = [219,220,229,235,246,248,250,252,254,255,256,258,260,262,266,268,269,271,273,275,277,279,280,282,283,285,286,288,290,292,293,296,297,298,308,311,328,329,332,336]
        new = self.doc["dialogues"][80:]
        self.assertEqual(len(new), 40)
        self.assertEqual([x["ordinal"] for x in new], list(range(81, 121)))
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = {}
        for item in self.doc["dialogues"]:
            kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(c) <= 0x9fff for c in item["text_ru"]))
            self.assertNotIn(chr(10), item["text_ru"])
            self.assertNotIn(chr(13), item["text_ru"])
        self.assertEqual(kinds, {"named":93,"narration":14,"subtitle":11,"sticker":2})
        self.assertEqual([x["kind"] for x in new].count("named"), 28)
        self.assertEqual([x["kind"] for x in new].count("narration"), 3)
        self.assertEqual([x["kind"] for x in new].count("subtitle"), 7)
        self.assertEqual([x["kind"] for x in new].count("sticker"), 2)
        self.assertEqual(new[4]["speaker_cn"], "特蕾西娅")
        self.assertEqual(new[5]["speaker_cn"], "凯尔希")
        self.assertEqual(new[38]["speaker_cn"], "特蕾西娅")
        self.assertEqual(new[0]["text_ru"], "Давай снова отправимся посмотреть другие уголки этой земли.")
        self.assertIn("Эйс", new[16]["text_ru"])
        self.assertIn("Бабелю", new[20]["text_ru"])

    def test_markup_and_lore_term(self):
        by_ordinal = {x["ordinal"]:x for x in self.doc["dialogues"]}
        for n in (84,115,116):
            self.assertTrue(by_ordinal[n]["text_ru"].startswith("<color=#000000>"))
            self.assertTrue(by_ordinal[n]["text_ru"].endswith("</color>"))
        self.assertEqual(by_ordinal[114]["text_ru"], "«Сивилайт Этерна».")
        self.assertEqual(by_ordinal[115]["kind"], "sticker")
        self.assertEqual(by_ordinal[116]["kind"], "sticker")

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
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_subtitle_markup_alignment"])
        self.assertEqual(a["segment_ordinals"], [81,120])
        self.assertEqual(a["segment_new_text_positions"], 40)
        self.assertTrue(a["previous_entries_preserved"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_chronology_readme_and_terms(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 40)
        self.assertEqual(self.audit["translated_segment"]["cumulative_text_positions"], 120)
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 120)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 58)
        self.assertEqual(self.qa["babel_completed_files"], 13)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 9)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3140)
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_06_end.txt")
        self.assertEqual(self.manifest["partial_scene_next_text_ordinal"], 121)
        self.assertEqual(self.manifest["partial_scene_next_source_line"], 337)
        row = next(line for line in self.index.splitlines() if "level_act33side_06_end.txt" in line)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_06_end.txt","partial_first_draft","93","0","14","2","11","120"])
        self.assertIn("120/178", self.readme)
        self.assertIn("Терезия", self.terms)
        self.assertIn("Эйс", self.terms)
        self.assertIn("Civilight Eterna", self.review)
        self.assertIn("Терезия", self.review)

if __name__ == "__main__":
    unittest.main()
