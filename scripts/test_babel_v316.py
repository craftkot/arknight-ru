# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8BeforeV316(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_before_partial_ru_v316.json")
        self.previous = load("events/babel_bb8_before_partial_ru_v315.json")
        self.audit = load("reports/BABEL_BB8_BEFORE_SOURCE_AUDIT_v316.json")
        self.qa = load("reports/QA_BABEL_v316.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v316.json")
        self.index = (ROOT / "events/BABEL_INDEX_v316.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_progress_and_prefix_preservation(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.16")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (80, 200, 120))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (81, 204))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 81)))
        self.assertEqual(self.doc["dialogues"][:40], self.previous["dialogues"])
        self.assertEqual(p["translated_kind_counts"], {"named": 61, "multiline": 0, "narration": 19, "subtitle": 0, "sticker": 0})
        self.assertEqual(p["remaining_kind_counts"], {"named": 97, "multiline": 2, "narration": 21, "subtitle": 0, "sticker": 0})

    def test_new_segment_line_map_and_kinds(self):
        expected = [90,92,93,95,97,98,100,102,104,106,107,109,112,113,114,115,116,127,128,133,134,136,160,162,163,165,167,169,171,173,175,177,179,181,196,197,200,201,202,203]
        segment = self.doc["dialogues"][40:]
        self.assertEqual([x["source_line"] for x in segment], expected)
        kinds = [x["kind"] for x in segment]
        self.assertEqual((kinds.count("named"), kinds.count("narration"), kinds.count("multiline")), (28,12,0))
        self.assertEqual(self.doc["source_alignment"]["segment_ordinals"], [41,80])
        self.assertEqual(self.doc["source_alignment"]["segment_source_lines"], expected)

    def test_russian_text_is_clean(self):
        for x in self.doc["dialogues"]:
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]", x["text_ru"]))
            self.assertNotIn(chr(10), x["text_ru"])
            self.assertNotIn(chr(13), x["text_ru"])
            self.assertEqual(x["text_ru"].count("«"), x["text_ru"].count("»"))

    def test_speakers_and_cn_primary_wording(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[41]["speaker_cn"], "阿斯卡纶")
        self.assertEqual(by[42]["speaker_cn"], "尤莉叶")
        self.assertEqual(by[63]["speaker_cn"], "？？？")
        self.assertEqual(by[68]["speaker_cn"], "神秘的刺客")
        self.assertIn("Королём Сарказов", by[49]["text_ru"])
        self.assertIn("сородич", by[71]["text_ru"])
        self.assertIn("Рынка шрамов", by[80]["text_ru"])
        self.assertIn("перестала узнавать собственную тень", by[57]["text_ru"])
        self.assertIn("Всех перебила", by[69]["text_ru"])
        self.assertIn("иллюстрированном сборнике историй", by[80]["text_ru"])
        self.assertIn("Scar Market / 疤痕商场", self.terms)

    def test_source_hashes_and_full_scene_alignment(self):
        s = self.doc["source"]
        a = self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "61daf6c0beeecfb442fd84a7dad26ea1110dac5b")
        self.assertEqual(s["en_git_blob_sha1"], "cbf456ffc623a5865f193132fb076857ec2e6c1a")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (594,594))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (200,200))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (394,394))
        self.assertTrue(s["en_extra_terminal_newline"])
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertFalse(a["cn_en_control_command_lines_match_exactly"])
        self.assertEqual(a["cn_en_control_command_difference_count"], 2)
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_and_readme(self):
        row = next(x for x in self.index.splitlines() if "level_act33side_08_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_08_beg.txt","partial_first_draft","61","0","19","0","0","80"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 80)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 120)
        self.assertEqual(self.qa["scene_remaining_named"], 97)
        self.assertEqual(self.qa["scene_remaining_multiline"], 2)
        self.assertEqual(self.qa["babel_completed_files"], 16)
        self.assertEqual(self.qa["babel_partial_files"], 1)
        self.assertEqual(self.qa["babel_not_started_files"], 6)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3649)
        self.assertEqual(self.manifest["version"], "v3.16")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_08_beg.txt")
        self.assertEqual((self.manifest["next_text_ordinal"], self.manifest["next_text_source_line"]), (81,204))
        self.assertIn("80/200", self.readme)
        self.assertIn("№81, CN строка 204", self.readme)
        self.assertIn("149/149", self.readme)

    def test_audit_differences_and_multiline_line_fix(self):
        self.assertEqual([x["ordinal"] for x in self.audit["documented_meaning_differences"]], [19,21,27,39,57,61,65,69,71,77,80])
        self.assertEqual([x["source_line"] for x in self.audit["documented_control_command_differences"]], [435,459])
        self.assertEqual([x["source_line"] for x in self.audit["documented_multiline_text_differences"]], [477,480])
        self.assertEqual(self.audit["segment"]["ordinals"], [41,80])
        self.assertEqual(self.audit["segment"]["next_ordinal"], 81)
        self.assertEqual(self.audit["segment"]["next_source_line"], 204)
        self.assertIn("physical source lines 477 and 480", " ".join(self.audit["notes"]))
        self.assertNotIn("physical source lines 313 and 316", " ".join(self.audit["notes"]))

if __name__ == "__main__":
    unittest.main()
