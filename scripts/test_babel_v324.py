# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8AfterV324(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_after_partial_ru_v324.json")
        self.previous = load("events/babel_bb8_after_partial_ru_v323.json")
        self.audit = load("reports/BABEL_BB8_AFTER_SOURCE_AUDIT_v324.json")
        self.qa = load("reports/QA_BABEL_v324.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v324.json")
        self.index = (ROOT / "events/BABEL_INDEX_v324.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_ordinals_source_lines_and_previous_prefix(self):
        expected = [592,593,595,597,599,601,603,610,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,667,668,676,677,678,679,690,695,696,702,703,707,708]
        self.assertEqual(self.doc["version"], "v3.24")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 201)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"][160:200]], expected)
        self.assertEqual(self.doc["dialogues"][:160], self.previous["dialogues"])
        self.assertTrue(self.doc["previous_entries_preserved"])
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (200, 241, 41))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (201, 712))

    def test_new_fragment_kind_counts(self):
        new = self.doc["dialogues"][160:200]
        kinds = {k: sum(x["kind"] == k for x in new) for k in ("named", "multiline", "narration", "sticker", "subtitle", "decision")}
        self.assertEqual(kinds, {"named": 6, "multiline": 0, "narration": 2, "sticker": 27, "subtitle": 0, "decision": 5})
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named": 108, "multiline": 2, "narration": 22, "sticker": 51, "subtitle": 12, "decision": 5})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"], {"named": 33, "multiline": 0, "narration": 4, "sticker": 4, "subtitle": 0, "decision": 0})

    def test_russian_text_invariants(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertNotRegex(entry["text_ru"], r"[\u3400-\u9fff]")
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_decisions_speakers_and_markup(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual([by[i]["kind"] for i in range(163, 168)], ["decision"] * 5)
        self.assertEqual(by[161]["speaker_cn"], "预言家")
        self.assertEqual(by[162]["speaker_cn"], "预言家")
        self.assertEqual(by[168]["speaker_cn"], "博士")
        self.assertEqual(by[188]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[189]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[194]["speaker_cn"], "博士")
        self.assertTrue(all(by[i]["kind"] == "sticker" and by[i]["text_ru"] == "……" for i in range(169, 188)))
        self.assertIn("<color=#FF4200>", by[190]["text_ru"])
        self.assertIn("</color>", by[190]["text_ru"])
        self.assertIn("<color=#FF4200>", by[191]["text_ru"])
        self.assertTrue(by[191]["text_ru"].startswith("\\n\\n"))
        self.assertTrue(by[192]["text_ru"].startswith("\\n\\n"))
        self.assertTrue(by[193]["text_ru"].startswith("\\n\\n"))
        for i in range(197, 201):
            self.assertTrue(by[i]["text_ru"].startswith("<i>"))
            self.assertTrue(by[i]["text_ru"].endswith("</i>"))

    def test_cn_primary_choices(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertIn("интересов своего народа", by[197]["text_ru"])
        self.assertIn("миражи", by[200]["text_ru"])
        self.assertIn("самостоятельно", by[161]["text_ru"])
        self.assertIn("Обратный отсчёт завершён", by[193]["text_ru"])
        self.assertFalse(self.doc["editorial_review"])
        self.assertFalse(self.doc["in_game_test"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "502baa017ba32f5d3359d2caeedd2adafc72cd2a")
        self.assertEqual(s["en_git_blob_sha1"], "f5b13d3e11d4be6c3d4412eff082ae606fe586b4")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (790, 791))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (241, 241))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (549, 549))
        for key in ("cn_en_text_positions_match", "cn_en_text_type_sequence_match", "cn_en_source_line_positions_match", "cn_en_speaker_tag_positions_align", "cn_en_nontext_control_commands_match_exactly"):
            self.assertTrue(a[key])
        self.assertEqual(a["segment_ordinals"], [161, 200])
        self.assertEqual(a["segment_source_lines"], [592,593,595,597,599,601,603,610,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,667,668,676,677,678,679,690,695,696,702,703,707,708])
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_manifest_and_readme(self):
        self.assertEqual(self.audit["segment"]["ordinals"], [161, 200])
        self.assertEqual(self.audit["segment"]["text_positions"], 40)
        self.assertEqual(self.audit["segment"]["kind_counts"], {"named": 6, "multiline": 0, "narration": 2, "sticker": 27, "subtitle": 0, "decision": 5})
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 200)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 41)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3969)
        self.assertEqual((self.qa["next_text_ordinal"], self.qa["next_text_source_line"]), (201, 712))
        rows = self.index.splitlines()
        header = rows[0].split(chr(9))
        self.assertEqual(header[-1], "decision_ru_lines")
        row = next(x for x in rows if "level_act33side_08_end.txt" in x).split(chr(9))
        self.assertEqual(row[2:9], ["partial_first_draft", "108", "2", "22", "51", "12", "200"])
        self.assertEqual(row[-1], "5")
        self.assertEqual(self.manifest["version"], "v3.24")
        self.assertEqual(self.manifest["next_text_ordinal"], 201)
        self.assertEqual(self.manifest["next_text_source_line"], 712)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3969)
        self.assertIn("v3.24", self.readme)
        self.assertIn("BABEL_INDEX_v324.tsv", self.readme)

if __name__ == "__main__":
    unittest.main()
