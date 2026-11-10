# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

EXPECTED_LINES = [11,19,21,22,24,25,27,28,39,40,41,42,43,44,47,49,61,64,66,68,70,76,77,86,97,99,100,111,112,116,119,122,128,134,136,138,140,142,144,146,147,149,151,157,167,168,169,174,175,179,181,183,185,186,187,189,191,203,205,207,221,223,225,227,229,231,237,244,245,246,247,251,252,260,266,267,269,271,272,274,275,277,278,279,280,302,303,304,305,309,310,311,323,325,326,351,353,354,355,357,380,381,384,385,386,392]

class BabelBB9BeforeV326(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb9_before_ru_v326.json")
        self.audit = load("reports/BABEL_BB9_BEFORE_SOURCE_AUDIT_v326.json")
        self.qa = load("reports/QA_BABEL_v326.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v326.json")
        self.index = (ROOT / "events/BABEL_INDEX_v326.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_ordinals_and_source_lines(self):
        self.assertEqual(self.doc["version"], "v3.26")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 107)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], EXPECTED_LINES)
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (106, 106, 0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertEqual(self.doc["source_file"], "activities/act33side/level_act33side_09_beg.txt")

    def test_kind_counts_and_multiline_positions(self):
        kinds = {k: sum(x["kind"] == k for x in self.doc["dialogues"]) for k in ("named", "multiline", "narration", "sticker", "subtitle", "decision")}
        self.assertEqual(kinds, {"named": 84, "multiline": 2, "narration": 20, "sticker": 0, "subtitle": 0, "decision": 0})
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[31]["kind"], "multiline")
        self.assertEqual(by[31]["source_line"], 119)
        self.assertEqual(by[32]["kind"], "multiline")
        self.assertEqual(by[32]["source_line"], 122)
        self.assertEqual(by[32]["text_ru"], "Открылась!")

    def test_russian_text_invariants(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertNotRegex(entry["text_ru"], r"[\u3400-\u9fff]")
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_names_and_cn_primary_decisions(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[45]["speaker_cn"], "孽茨雷")
        self.assertEqual(by[48]["speaker_cn"], "杜卡雷")
        self.assertEqual(by[59]["speaker_cn"], "菈玛莲")
        self.assertIn("Илиша", by[79]["text_ru"])
        self.assertEqual(by[87]["text_ru"], "Вж-ж—")
        self.assertIn("Парового рыцаря", by[92]["text_ru"])
        self.assertIn("магами Шпилей", by[95]["text_ru"])
        self.assertIn("арбалетных болтов", by[98]["text_ru"])
        self.assertEqual(by[106]["text_ru"], "……")
        self.assertFalse(self.doc["editorial_review"])
        self.assertFalse(self.doc["in_game_test"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "20ed741c357f668e305da640a72c79e2d02648f3")
        self.assertEqual(s["en_git_blob_sha1"], "1e878c05b06853b0ac7ea49e22459a2906ea32f2")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (399, 400))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (106, 106))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (293, 293))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_source_line_positions_match"])
        self.assertTrue(a["cn_en_speaker_tag_positions_align"])
        self.assertTrue(a["cn_en_nontext_control_commands_match_exactly"])
        self.assertEqual(a["segment_ordinals"], [1, 106])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_qa_manifest_index_and_readme(self):
        self.assertEqual(self.qa["version"], "v3.26")
        self.assertEqual(self.qa["new_total_ru_text_entries"], 106)
        self.assertEqual(self.qa["scene_translated_text_entries"], 106)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 0)
        self.assertEqual(self.qa["babel_completed_files"], 19)
        self.assertEqual(self.qa["babel_partial_files"], 0)
        self.assertEqual(self.qa["babel_not_started_files"], 4)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 4116)
        self.assertEqual(self.qa["next_file"], "activities/act33side/level_act33side_09_end.txt")
        self.assertEqual(self.manifest["version"], "v3.26")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_09_end.txt")
        integrity = self.manifest["translation_integrity"]
        self.assertEqual(integrity["babel_completed_files"], 19)
        self.assertEqual(integrity["babel_partial_files"], 0)
        self.assertEqual(integrity["babel_not_started_files"], 4)
        self.assertEqual(integrity["babel_completed_ru_text_entries"], 4116)
        rows = self.index.splitlines()
        row = next(x for x in rows if "level_act33side_09_beg.txt" in x).split(chr(9))
        self.assertEqual(row[2:9], ["first_draft_complete", "84", "2", "20", "0", "0", "106"])
        self.assertEqual(row[9:11], [self.doc["source"]["cn_git_blob_sha1"], self.doc["source"]["en_git_blob_sha1"]])
        self.assertIn("v3.26", self.readme)
        self.assertIn("BB-9 после боя", self.readme)
        self.assertIn("Liens / 镰须 — Лиэнс", self.terms)
        self.assertTrue(self.audit["scene_complete"])
        self.assertEqual(self.audit["segment"]["ordinals"], [1, 106])

if __name__ == "__main__":
    unittest.main()
