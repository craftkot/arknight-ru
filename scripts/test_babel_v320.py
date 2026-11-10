# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8AfterV320(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_after_partial_ru_v320.json")
        self.audit = load("reports/BABEL_BB8_AFTER_SOURCE_AUDIT_v320.json")
        self.qa = load("reports/QA_BABEL_v320.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v320.json")
        self.index = (ROOT / "events/BABEL_INDEX_v320.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.20")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (40, 241, 201))
        self.assertFalse(p["complete"])
        self.assertEqual(p["next_text_ordinal"], 41)
        self.assertEqual(p["next_text_source_line"], 158)
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 41)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], [12,15,16,17,18,19,20,21,33,34,35,36,40,42,44,45,47,48,50,51,52,54,59,60,62,63,94,95,105,112,113,114,130,132,134,135,137,140,141,144])
        self.assertEqual(p["translated_kind_counts"], {"named":29,"multiline":0,"narration":11,"sticker":0,"subtitle":0,"decision":0})
        self.assertEqual(p["remaining_kind_counts"], {"named":112,"multiline":2,"narration":15,"sticker":55,"subtitle":12,"decision":5})

    def test_translation_text_is_clean(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(ch) <= 0x9fff for ch in entry["text_ru"]))
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_speakers_and_cn_primary_choices(self):
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[2]["speaker_cn"], "“疤眼”")
        self.assertEqual(by[14]["speaker_cn"], "萨卡兹雇佣兵")
        self.assertEqual(by[33]["speaker_cn"], "特雷西斯")
        self.assertEqual(by[34]["speaker_cn"], "曼弗雷德")
        self.assertEqual(by[40]["speaker_cn"], "弃名死士")
        self.assertIn("Королевский двор циклопов", by[7]["text_ru"])
        self.assertIn("позаботиться о собственном положении", by[20]["text_ru"])
        self.assertIn("сородичей", by[31]["text_ru"])
        self.assertIn("Древний сарказский язык", by[37]["text_ru"])

    def test_source_hashes_and_structure(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "502baa017ba32f5d3359d2caeedd2adafc72cd2a")
        self.assertEqual(s["en_git_blob_sha1"], "f5b13d3e11d4be6c3d4412eff082ae606fe586b4")
        self.assertEqual((s["cn_line_count"],s["en_line_count"]), (790,791))
        self.assertEqual((s["cn_text_total"],s["en_text_total"]), (241,241))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]), (549,549))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_source_line_positions_match"])
        self.assertTrue(a["cn_en_nontext_control_commands_match_exactly"])
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_and_qa(self):
        self.assertEqual(self.audit["segment"]["ordinals"], [1,40])
        self.assertEqual(self.audit["segment"]["text_positions"], 40)
        self.assertEqual(self.audit["segment"]["kind_counts"], {"named":29,"narration":11,"multiline":0,"sticker":0,"subtitle":0,"decision":0})
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 40)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 201)
        self.assertEqual(self.qa["babel_completed_files"], 17)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 5)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3809)
        self.assertFalse(self.audit["scene_complete"])
        self.assertFalse(self.audit["game_behavior_verified"])

    def test_index_manifest_readme_and_glossary(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_08_end.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_08_end.txt","partial_first_draft","29","0","11","0","0","40"])
        self.assertEqual(self.manifest["version"], "v3.20")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_08_end.txt")
        self.assertEqual((self.manifest["next_text_ordinal"],self.manifest["next_text_source_line"]), (41,158))
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3809)
        self.assertIn("BB-8 после боя", self.readme)
        self.assertIn("弃名死士", self.terms)
        self.assertIn("смертник, отрёкшийся от имени", self.terms)

if __name__ == "__main__":
    unittest.main()
