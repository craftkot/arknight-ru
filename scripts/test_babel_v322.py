# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8AfterV322(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_after_partial_ru_v322.json")
        self.previous = load("events/babel_bb8_after_partial_ru_v321.json")
        self.audit = load("reports/BABEL_BB8_AFTER_SOURCE_AUDIT_v322.json")
        self.qa = load("reports/QA_BABEL_v322.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v322.json")
        self.index = (ROOT / "events/BABEL_INDEX_v322.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_cumulative_ordinals_lines_and_prefix(self):
        expected = [12,15,16,17,18,19,20,21,33,34,35,36,40,42,44,45,47,48,50,51,52,54,59,60,62,63,94,95,105,112,113,114,130,132,134,135,137,140,141,144,
                    158,159,163,176,178,196,198,217,218,219,220,224,226,228,229,230,231,233,243,244,250,271,279,280,286,292,293,298,299,300,309,310,316,317,319,321,322,326,327,328,
                    329,341,342,343,345,347,348,349,351,353,355,357,358,362,364,365,367,369,370,371,373,374,386,387,393,399,401,403,405,420,421,427,432,434,435,437,457,458,459,460]
        self.assertEqual(self.doc["version"], "v3.22")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 121)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], expected)
        self.assertEqual(self.doc["dialogues"][:80], self.previous["dialogues"])
        self.assertTrue(self.doc["previous_entries_preserved"])
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"],p["total_source_text_positions"],p["remaining_text_positions"]), (120,241,121))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"],p["next_text_source_line"]), (121,461))

    def test_new_fragment_kind_counts(self):
        new = [x for x in self.doc["dialogues"] if 81 <= x["ordinal"] <= 120]
        kinds = {k:sum(x["kind"]==k for x in new) for k in ("named","narration","multiline","sticker","subtitle","decision")}
        self.assertEqual(kinds, {"named":32,"narration":2,"multiline":2,"sticker":4,"subtitle":0,"decision":0})
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named":88,"multiline":2,"narration":20,"sticker":10,"subtitle":0,"decision":0})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"], {"named":53,"multiline":0,"narration":6,"sticker":45,"subtitle":12,"decision":5})

    def test_russian_text_invariants(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertNotRegex(entry["text_ru"], r"[\u3400-\u9fff]")
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_speakers_multiline_and_sticker_payloads(self):
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[82]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[95]["kind"], "multiline")
        self.assertEqual(by[96]["kind"], "multiline")
        self.assertEqual(by[96]["text_ru"], "И ещё… необычные враги.")
        self.assertEqual(by[105]["speaker_cn"], "凯尔希")
        self.assertEqual(by[106]["speaker_cn"], "可露希尔")
        self.assertEqual(by[113]["speaker_cn"], "Logos")
        self.assertEqual(by[103]["text_ru"], "Обратный отсчёт")
        self.assertEqual(by[104]["text_ru"], "22 мин 48 с")
        self.assertEqual(by[110]["text_ru"], "Обратный отсчёт")
        self.assertEqual(by[111]["text_ru"], "12 мин 57 с")

    def test_cn_primary_meaning_choices(self):
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertIn("Мантры", by[83]["text_ru"])
        self.assertIn("центральных районах Казделя", by[88]["text_ru"])
        self.assertIn("никакие расчёты и уловки", by[99]["text_ru"])
        self.assertIn("погребальная песнь", by[114]["text_ru"])
        self.assertIn("уязвимой общности", by[118]["text_ru"])
        self.assertIn("Ориджиниумом", by[119]["text_ru"])
        self.assertFalse(self.doc["editorial_review"])
        self.assertFalse(self.doc["in_game_test"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "502baa017ba32f5d3359d2caeedd2adafc72cd2a")
        self.assertEqual(s["en_git_blob_sha1"], "f5b13d3e11d4be6c3d4412eff082ae606fe586b4")
        self.assertEqual((s["cn_line_count"],s["en_line_count"]), (790,791))
        self.assertEqual((s["cn_text_total"],s["en_text_total"]), (241,241))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]), (549,549))
        for key in ("cn_en_text_positions_match","cn_en_text_type_sequence_match","cn_en_source_line_positions_match",
                    "cn_en_speaker_tag_positions_align","cn_en_nontext_control_commands_match_exactly"):
            self.assertTrue(a[key])
        self.assertEqual(a["segment_ordinals"], [81,120])
        self.assertEqual(a["segment_source_lines"], [x["source_line"] for x in self.doc["dialogues"][80:120]])
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_manifest_readme_and_terms(self):
        self.assertEqual(self.audit["segment"]["ordinals"], [81,120])
        self.assertEqual(self.audit["segment"]["text_positions"], 40)
        self.assertEqual(self.audit["segment"]["kind_counts"], {"named":32,"multiline":2,"narration":2,"sticker":4,"subtitle":0,"decision":0})
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 120)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 121)
        self.assertEqual(self.qa["babel_partial_ru_text_entries"], 120)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3889)
        self.assertEqual(self.qa["next_text_ordinal"], 121)
        self.assertEqual(self.qa["next_text_source_line"], 461)
        row = next(x for x in self.index.splitlines() if "level_act33side_08_end.txt" in x)
        self.assertEqual(row.split(chr(9))[:11], ["act33side","level_act33side_08_end.txt","partial_first_draft","88","2","20","10","0","120",
                                                   "502baa017ba32f5d3359d2caeedd2adafc72cd2a","f5b13d3e11d4be6c3d4412eff082ae606fe586b4"])
        self.assertEqual(self.manifest["version"], "v3.22")
        self.assertEqual(self.manifest["next_text_ordinal"], 121)
        self.assertEqual(self.manifest["next_text_source_line"], 461)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3889)
        self.assertIn("v3.22", self.readme)
        self.assertIn("events/BABEL_INDEX_v322.tsv", self.readme)
        self.assertIn("Mantra — Мантра", self.terms)

if __name__ == "__main__":
    unittest.main()
