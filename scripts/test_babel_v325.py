# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8AfterV325(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_after_ru_v325.json")
        self.previous = load("events/babel_bb8_after_partial_ru_v324.json")
        self.audit = load("reports/BABEL_BB8_AFTER_SOURCE_AUDIT_v325.json")
        self.qa = load("reports/QA_BABEL_v325.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v325.json")
        self.index = (ROOT / "events/BABEL_INDEX_v325.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_ordinals_source_lines_and_previous_prefix(self):
        expected = [712,713,718,719,720,721,722,723,731,732,738,739,745,747,748,749,750,759,760,761,762,763,764,765,766,767,768,769,770,771,772,773,774,775,776,777,778,779,780,781,782]
        self.assertEqual(self.doc["version"], "v3.25")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 242)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"][200:]], expected)
        self.assertEqual(self.doc["dialogues"][:200], self.previous["dialogues"])
        self.assertTrue(self.doc["previous_entries_preserved"])
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (241, 241, 0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertEqual(self.doc["source_file"], "activities/act33side/level_act33side_08_end.txt")

    def test_new_fragment_kind_counts(self):
        new = self.doc["dialogues"][200:]
        kinds = {k: sum(x["kind"] == k for x in new) for k in ("named", "multiline", "narration", "sticker", "subtitle", "decision")}
        self.assertEqual(kinds, {"named": 33, "multiline": 0, "narration": 4, "sticker": 4, "subtitle": 0, "decision": 0})
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named": 141, "multiline": 2, "narration": 26, "sticker": 55, "subtitle": 12, "decision": 5})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"], {"named": 0, "multiline": 0, "narration": 0, "sticker": 0, "subtitle": 0, "decision": 0})

    def test_russian_text_invariants(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertNotRegex(entry["text_ru"], r"[\u3400-\u9fff]")
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_speakers_markup_and_selected_cn_choices(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[203]["speaker_cn"], "特雷西斯")
        self.assertEqual(by[213]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[218]["speaker_cn"], "特雷西斯")
        self.assertEqual(by[219]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[241]["speaker_cn"], "特雷西斯")
        for i in (201, 202):
            self.assertEqual(by[i]["kind"], "sticker")
            self.assertTrue(by[i]["text_ru"].startswith("<i>"))
            self.assertTrue(by[i]["text_ru"].endswith("</i>"))
        self.assertEqual(by[209]["text_ru"], "1086 год")
        self.assertIn("Илишем", by[225]["text_ru"])
        self.assertIn("измученные", by[228]["text_ru"])
        self.assertIn("следующему поколению", by[235]["text_ru"])
        self.assertEqual(by[241]["text_ru"], "Как и ты.")
        self.assertFalse(self.doc["editorial_review"])
        self.assertFalse(self.doc["in_game_test"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "502baa017ba32f5d3359d2caeedd2adafc72cd2a")
        self.assertEqual(s["en_git_blob_sha1"], "f5b13d3e11d4be6c3d4412eff082ae606fe586b4")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (790, 791))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (241, 241))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_source_line_positions_match"])
        self.assertTrue(a["cn_en_speaker_tag_positions_align"])
        self.assertTrue(a["cn_en_nontext_control_commands_match_exactly"])
        self.assertEqual(a["segment_ordinals"], [201, 241])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tag_positions_align"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_qa_manifest_index_and_readme(self):
        self.assertEqual(self.qa["version"], "v3.25")
        self.assertEqual(self.qa["new_total_ru_text_entries"], 41)
        self.assertEqual(self.qa["scene_translated_text_entries"], 241)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 0)
        self.assertEqual(self.qa["babel_completed_files"], 18)
        self.assertEqual(self.qa["babel_partial_files"], 0)
        self.assertEqual(self.qa["babel_not_started_files"], 5)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 4010)
        self.assertEqual(self.qa["next_file"], "activities/act33side/level_act33side_09_beg.txt")
        self.assertEqual(self.manifest["version"], "v3.25")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_09_beg.txt")
        integrity = self.manifest["translation_integrity"]
        self.assertEqual(integrity["babel_completed_files"], 18)
        self.assertEqual(integrity["babel_partial_files"], 0)
        self.assertEqual(integrity["babel_completed_ru_text_entries"], 4010)
        rows = self.index.splitlines()
        row = next(x for x in rows if "level_act33side_08_end.txt" in x).split(chr(9))
        self.assertEqual(row[2:9], ["first_draft_complete", "141", "2", "26", "55", "12", "241"])
        self.assertEqual(row[-1], "5")
        self.assertIn("v3.25", self.readme)
        self.assertIn("BB-9 до боя", self.readme)
        self.assertIn("Yliš / 以勒什 — Илиш", self.terms)
        self.assertTrue(self.audit["scene_complete"])
        self.assertEqual(self.audit["segment"]["ordinals"], [201, 241])

if __name__ == "__main__":
    unittest.main()
