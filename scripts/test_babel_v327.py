# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

EXPECTED_LINES = [11,12,13,16,17,18,20,21,23,24,25,27,28,29,33,35,36,37,39,41,43,45,47,56,57,58,67,68,69,70,71,72,73,77,78,81,82,83,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,145,146,150,152,153,155,157,159,160,161,166,167,169]

class BabelBB9AfterV327(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb9_after_ru_v327.json")
        self.audit = load("reports/BABEL_BB9_AFTER_SOURCE_AUDIT_v327.json")
        self.qa = load("reports/QA_BABEL_v327.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v327.json")
        self.index = (ROOT / "events/BABEL_INDEX_v327.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_ordinals_and_source_lines(self):
        self.assertEqual(self.doc["version"], "v3.27")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 88)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], EXPECTED_LINES)
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (87, 87, 0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertEqual(self.doc["source_file"], "activities/act33side/level_act33side_09_end.txt")

    def test_kind_counts_and_speakers(self):
        kinds = {k: sum(x["kind"] == k for x in self.doc["dialogues"]) for k in ("named", "multiline", "narration", "sticker", "subtitle", "decision")}
        self.assertEqual(kinds, {"named": 53, "multiline": 0, "narration": 34, "sticker": 0, "subtitle": 0, "decision": 0})
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[19]["speaker_cn"], "阿米娅")
        self.assertEqual(by[20]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[77]["speaker_cn"], "博士")
        self.assertEqual(by[81]["speaker_cn"], "博士")
        self.assertEqual(by[87]["speaker_cn"], "特蕾西娅")

    def test_russian_text_invariants(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertFalse(any(chr(0x3400) <= ch <= chr(0x9fff) for ch in entry["text_ru"]))
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_cn_primary_choices_and_markup(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertIn("Пустыне Отчаяния", by[4]["text_ru"])
        self.assertIn("тряпичного человечка", by[13]["text_ru"])
        self.assertIn("ряски", by[13]["text_ru"])
        self.assertIn("права доступа", by[50]["text_ru"])
        self.assertIn("запечатала большую часть её областей", by[51]["text_ru"])
        self.assertIn("тайну сохранения жизни", by[66]["text_ru"])
        self.assertEqual(by[69]["text_ru"], "Вздох…")
        self.assertIn("Корона отделилась от неё", by[79]["text_ru"])
        self.assertEqual(by[87]["text_ru"], "Значит, вот твой ответ, Доктор…")
        self.assertFalse(self.doc["editorial_review"])
        self.assertFalse(self.doc["in_game_test"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "c460e2a6c30a8ec4ce306ccbb8eed3f37899eec2")
        self.assertEqual(s["en_git_blob_sha1"], "006b4ed34bf39a9bd32539c5cf779b707dbc87c7")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (176, 177))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (87, 87))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (89, 89))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_source_line_positions_match"])
        self.assertTrue(a["cn_en_speaker_tag_positions_align"])
        self.assertTrue(a["cn_en_nontext_control_commands_match_exactly"])
        self.assertEqual(a["segment_ordinals"], [1, 87])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_qa_manifest_index_readme_and_terms(self):
        self.assertEqual(self.qa["version"], "v3.27")
        self.assertEqual(self.qa["new_total_ru_text_entries"], 87)
        self.assertEqual(self.qa["scene_translated_text_entries"], 87)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 0)
        self.assertEqual(self.qa["babel_completed_files"], 20)
        self.assertEqual(self.qa["babel_not_started_files"], 3)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"], 4203)
        self.assertEqual(self.qa["next_file"], "activities/act33side/level_act33side_10_beg.txt")
        self.assertEqual(self.manifest["version"], "v3.27")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_10_beg.txt")
        integrity = self.manifest["translation_integrity"]
        self.assertEqual(integrity["babel_completed_files"], 20)
        self.assertEqual(integrity["babel_not_started_files"], 3)
        self.assertEqual(integrity["babel_completed_ru_text_entries"], 4203)
        row = next(x for x in self.index.splitlines() if "level_act33side_09_end.txt" in x).split(chr(9))
        self.assertEqual(row[2:9], ["first_draft_complete", "53", "0", "34", "0", "0", "87"])
        self.assertEqual(row[9:11], [self.doc["source"]["cn_git_blob_sha1"], self.doc["source"]["en_git_blob_sha1"]])
        self.assertIn("v3.27", self.readme)
        self.assertIn("BB-10 до боя", self.readme)
        self.assertIn("Little puppet / 小布人", self.terms)
        self.assertTrue(self.audit["scene_complete"])
        self.assertEqual(self.audit["segment"]["ordinals"], [1, 87])

if __name__ == "__main__":
    unittest.main()
