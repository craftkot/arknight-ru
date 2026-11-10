# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8AfterV321(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_after_partial_ru_v321.json")
        self.audit = load("reports/BABEL_BB8_AFTER_SOURCE_AUDIT_v321.json")
        self.qa = load("reports/QA_BABEL_v321.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v321.json")
        self.index = (ROOT / "events/BABEL_INDEX_v321.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_cumulative_ordinals_and_source_lines(self):
        expected = [12,15,16,17,18,19,20,21,33,34,35,36,40,42,44,45,47,48,50,51,52,54,59,60,62,63,94,95,105,112,113,114,130,132,134,135,137,140,141,144,
                    158,159,163,176,178,196,198,217,218,219,220,224,226,228,229,230,231,233,243,244,250,271,279,280,286,292,293,298,299,300,309,310,316,317,319,321,322,326,327,328]
        self.assertEqual(self.doc["version"], "v3.21")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 81)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], expected)
        self.assertTrue(self.doc["previous_entries_preserved"])
        self.assertEqual(self.doc["progress"]["translated_text_positions"], 80)
        self.assertEqual(self.doc["progress"]["remaining_text_positions"], 161)
        self.assertFalse(self.doc["progress"]["complete"])
        self.assertEqual((self.doc["progress"]["next_text_ordinal"], self.doc["progress"]["next_text_source_line"]), (81, 329))

    def test_new_fragment_kind_counts(self):
        new = [x for x in self.doc["dialogues"] if 41 <= x["ordinal"] <= 80]
        kinds = {k: sum(x["kind"] == k for x in new) for k in ("named","narration","sticker","multiline","subtitle","decision")}
        self.assertEqual(kinds, {"named":27,"narration":7,"sticker":6,"multiline":0,"subtitle":0,"decision":0})
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named":56,"multiline":0,"narration":18,"sticker":6,"subtitle":0,"decision":0})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"], {"named":85,"multiline":2,"narration":8,"sticker":49,"subtitle":12,"decision":5})

    def test_russian_text_invariants(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertNotRegex(entry["text_ru"], r"[\u3400-\u9fff]")
            self.assertNotIn("\\n", entry["text_ru"])
            self.assertNotIn("\\r", entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_speaker_slots_and_cn_primary_decisions(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[41]["speaker_cn"], "巴别塔刺客")
        self.assertEqual(by[46]["speaker_cn"], "曼弗雷德")
        self.assertEqual(by[52]["speaker_cn"], "特雷西斯")
        self.assertEqual(by[61]["speaker_cn"], "Logos")
        self.assertEqual(by[65]["speaker_cn"], "凯尔希")
        self.assertEqual(by[66]["speaker_cn"], "Ace")
        self.assertEqual(by[62]["speaker_cn"], "慌乱的王庭军")
        self.assertIn("офицер охраны генерала", by[46]["text_ru"])
        self.assertIn("поодиночке", by[67]["text_ru"])
        self.assertIn("агентам внутри города", by[65]["text_ru"])
        self.assertIn("словно сговорившись", by[79]["text_ru"])
        self.assertIn("палачи", by[58]["text_ru"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "502baa017ba32f5d3359d2caeedd2adafc72cd2a")
        self.assertEqual(s["en_git_blob_sha1"], "f5b13d3e11d4be6c3d4412eff082ae606fe586b4")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (790, 791))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (241, 241))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (549, 549))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_source_line_positions_match"])
        self.assertTrue(a["cn_en_speaker_tag_positions_align"])
        self.assertTrue(a["cn_en_nontext_control_commands_match_exactly"])
        self.assertEqual(a["segment_ordinals"], [1, 80])
        self.assertEqual(a["segment_source_lines"], [x["source_line"] for x in self.doc["dialogues"]])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_manifest_and_documentation(self):
        self.assertEqual(self.audit["segment"]["ordinals"], [41, 80])
        self.assertEqual(self.audit["segment"]["text_positions"], 40)
        self.assertEqual(self.audit["segment"]["kind_counts"], {"named":27,"narration":7,"multiline":0,"sticker":6,"subtitle":0,"decision":0})
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 80)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 161)
        self.assertEqual(self.qa["babel_partial_ru_text_entries"], 80)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3849)
        self.assertEqual(self.qa["next_text_ordinal"], 81)
        self.assertEqual(self.qa["next_text_source_line"], 329)
        row = next(x for x in self.index.splitlines() if "level_act33side_08_end.txt" in x)
        self.assertEqual(row.split(chr(9))[:11], ["act33side","level_act33side_08_end.txt","partial_first_draft","56","0","18","6","0","80","502baa017ba32f5d3359d2caeedd2adafc72cd2a","f5b13d3e11d4be6c3d4412eff082ae606fe586b4"])
        self.assertEqual(self.manifest["version"], "v3.21")
        self.assertEqual(self.manifest["next_text_ordinal"], 81)
        self.assertEqual(self.manifest["next_text_source_line"], 329)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3849)
        self.assertIn("BB-8 после боя", self.readme)
        self.assertIn("v3.21", self.readme)
        self.assertIn("ассасин Бабеля", self.terms)
        self.assertFalse(self.audit["scene_complete"])
        self.assertFalse(self.audit["game_behavior_verified"])

if __name__ == "__main__":
    unittest.main()
