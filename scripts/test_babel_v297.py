# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6V297(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_before_partial_ru_v297.json")
        self.old = load("events/babel_bb6_before_partial_ru_v296.json")
        self.audit = load("reports/BABEL_BB6_BEFORE_SOURCE_AUDIT_v297.json")
        self.qa = load("reports/QA_BABEL_v297.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v297.json")
        self.index = (ROOT / "events/BABEL_INDEX_v297.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.review = (ROOT / "docs/CN_EN_RU_TERMINOLOGY_REVIEW.tsv").read_text(encoding="utf-8")

    def test_progress_and_ordinals(self):
        d, p = self.doc, self.doc["progress"]
        self.assertEqual(d["version"], "v2.97")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (175, 258, 83))
        self.assertFalse(p["complete"])
        self.assertEqual((p["last_source_line"], p["next_source_line"], p["next_text_ordinal"], p["next_text_source_line"]), (553, 554, 176, 556))
        self.assertEqual([x["ordinal"] for x in d["dialogues"]], list(range(1, 176)))

    def test_previous_144_positions_preserved(self):
        for old in self.old["dialogues"]:
            self.assertEqual(self.doc["dialogues"][old["ordinal"] - 1], old)

    def test_new_segment_positions_and_kinds(self):
        expected = [469,470,476,477,479,481,483,485,486,491,500,507,508,510,512,514,516,518,520,522,524,526,528,529,531,540,541,543,550,551,553]
        new = self.doc["dialogues"][144:]
        self.assertEqual(len(new), 31)
        self.assertEqual([x["source_line"] for x in new], expected)
        self.assertEqual([x["ordinal"] for x in new], list(range(145,176)))
        kinds = {}
        for x in self.doc["dialogues"]:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(c) <= 0x9fff for c in x["text_ru"]))
            self.assertNotIn("\\n", x["text_ru"])
            self.assertNotIn("\\r", x["text_ru"])
        self.assertEqual(kinds, {"named":148,"multiline":11,"narration":16})
        self.assertEqual(new[10]["speaker_cn"], "萨卡兹雇佣兵")
        self.assertEqual(new[10]["text_ru"], "Эй, стой! Не подходи к Заражённым. Джули сама с ними разберётся.")
        self.assertEqual(new[24]["speaker_cn"], "？？？")

    def test_source_alignment_and_hashes(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual((s["cn_git_blob_sha1"], s["en_git_blob_sha1"]), ("0fa57f8b2c4647c06bce0ba73008798d340a781c", "47a63283cb5d1c42e205f6bcebbf1e9cc134ac03"))
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (770,771))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (258,258))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (512,512))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertEqual(a["segment_new_text_positions"], 31)
        self.assertEqual(a["next_ordinal"], 176)
        self.assertEqual(a["next_text_source_line"], 556)
        self.assertTrue(a["previous_144_entries_preserved"])

    def test_audit_qa_index_chronology_readme_and_terms(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 31)
        self.assertTrue(self.audit["translated_segment"]["previous_144_preserved"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 31)
        self.assertEqual(self.qa["scene_ru_text_entries"], 175)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 83)
        self.assertTrue(self.qa["previous_144_entries_unchanged"])
        self.assertIn("level_act33side_06_beg.txt\\tpartial_first_draft\\t148\\t11\\t16\\t0\\t0\\t175", self.index)
        self.assertEqual(self.manifest["partial_scene_next_text_ordinal"], 176)
        self.assertEqual(self.manifest["partial_scene_next_source_line"], 556)
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 175)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 2937)
        self.assertIn("BB-6 до боя: 175/258", self.readme)
        self.assertIn("BB-6 до боя: 144/258", self.readme)
        self.assertIn("Julie / 尤莉叶", self.terms)
        self.assertIn("Suppressant / 抑制剂", self.terms)
        self.assertIn("尤莉叶\\tJulie\\tДжули", self.review)

if __name__ == "__main__":
    unittest.main()
