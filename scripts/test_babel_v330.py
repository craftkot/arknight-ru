# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

EXPECTED_LINES = [11,12,13,14,15,16,17,18,19,20,21,22,23,24,28,47,49,51,53,54,56,60,64,65,66,69,71,72,75,77,79,84,85,86,88,94,95,98,100,107,111,112,113,116,119,128,129,141,142,143,155,156,157,165,166,167,168,169,170,171,172,173,174,175,176,177,178,189,190,191,202,204,209,210,211,213,214,226,227,228,229,230,231,232,233,238,239,240,241,248,249,250,251,252,253,254,255,267,269,274,275,277,278,280,281,282,284,286,288,289,291,293,298,299,301,303,304,306,310,325,326,327]

class BabelST03V330(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_st03_ru_v330.json")
        self.audit = load("reports/BABEL_ST03_SOURCE_AUDIT_v330.json")
        self.qa = load("reports/QA_BABEL_v330.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v330.json")
        self.index = (ROOT / "events/BABEL_INDEX_v330.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.previous = load("events/babel_bb10_after_ru_v329.json")

    def test_ordinals_lines_and_progress(self):
        self.assertEqual(self.doc["version"], "v3.30")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 123)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], EXPECTED_LINES)
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (122, 122, 0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertEqual(self.doc["source_file"], "activities/act33side/level_act33side_st03.txt")

    def test_kind_counts_and_speaker_positions(self):
        kinds = {k: sum(x["kind"] == k for x in self.doc["dialogues"]) for k in ("named", "multiline", "narration", "sticker", "subtitle", "decision")}
        self.assertEqual(kinds, {"named": 85, "multiline": 0, "narration": 37, "sticker": 0, "subtitle": 0, "decision": 0})
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        for ordinal, speaker in {16:"凯尔希", 27:"Scout", 36:"可露希尔", 38:"Logos", 41:"阿米娅", 51:"博士", 68:"特蕾西娅", 73:"通讯声", 75:"？？？", 104:"预言家", 119:"特蕾西娅"}.items():
            self.assertEqual(by[ordinal]["speaker_cn"], speaker)

    def test_russian_payloads_and_runtime_markup(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(ch) <= 0x9fff for ch in entry["text_ru"]))
            self.assertNotIn("\\n", entry["text_ru"])
            self.assertNotIn("\\r", entry["text_ru"])
        self.assertEqual(by[52]["text_ru"].count("<color=#FF4200>"), 2)
        self.assertEqual(by[52]["text_ru"].count("</color>"), 2)
        self.assertIn("0091_admin", by[52]["text_ru"])
        self.assertEqual(by[119]["text_ru"], "…{@nickname}.")
        self.assertIn("открытый замысел", by[104]["text_ru"])
        self.assertIn("невозможно избежать", by[104]["text_ru"])
        self.assertIn("Амией", by[86]["text_ru"])

    def test_source_hashes_and_structural_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "945b9cbe8b92f6517423fb3c774db8fd1dd806e6")
        self.assertEqual(s["en_git_blob_sha1"], "324a425d6d345a1a594ee3ba87dad6c5321eee8a")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (336, 337))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (122, 122))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (214, 214))
        self.assertTrue(s["en_extra_terminal_newline"])
        for key in ("cn_en_text_positions_match", "cn_en_text_type_sequence_match", "cn_en_source_line_positions_match", "cn_en_speaker_tag_positions_align", "cn_en_nontext_control_commands_match_exactly"):
            self.assertTrue(a[key])
        self.assertEqual(a["cn_en_normalized_structural_difference_count"], 0)
        self.assertEqual(a["segment_ordinals"], [1, 122])
        self.assertEqual(a["segment_source_lines"], EXPECTED_LINES)
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_qa_manifest_index_and_next_scene(self):
        self.assertEqual(self.qa["new_total_ru_text_entries"], 122)
        self.assertEqual(self.qa["babel_completed_files"], 23)
        self.assertEqual(self.qa["babel_not_started_files"], 0)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"], 4633)
        self.assertEqual(self.qa["next_file"], "obt/main/level_main_06-08_beg.txt")
        self.assertEqual(self.manifest["version"], "v3.30")
        self.assertEqual(self.manifest["next_file"], "obt/main/level_main_06-08_beg.txt")
        ti = self.manifest["translation_integrity"]
        self.assertEqual(ti["babel_completed_files"], 23)
        self.assertEqual(ti["babel_completed_named_ru_lines"], 3625)
        self.assertEqual(ti["babel_completed_plain_ru_lines"], 748)
        self.assertEqual(ti["babel_completed_ru_text_entries"], 4633)
        row = next(x for x in self.index.splitlines() if "level_act33side_st03.txt" in x).split(chr(9))
        self.assertEqual(row[2:9], ["first_draft_complete", "85", "0", "37", "0", "0", "122"])
        self.assertEqual(row[9:11], ["945b9cbe8b92f6517423fb3c774db8fd1dd806e6", "324a425d6d345a1a594ee3ba87dad6c5321eee8a"])
        self.assertIn("v3.30", self.readme)
        self.assertIn("BB-ST-3", self.readme)
        self.assertIn("6-8 до боя", self.readme)
        self.assertIn("阳谋", self.terms)

    def test_previous_babel_scene_remains_present(self):
        self.assertEqual(self.previous["version"], "v3.29")
        self.assertEqual(len(self.previous["dialogues"]), 252)
        self.assertTrue(self.previous["progress"]["complete"])
        self.assertTrue(self.audit["structural_comparison"]["nontext_control_commands_match_exactly"])

if __name__ == "__main__":
    unittest.main()
