# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8BeforeV315(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_before_partial_ru_v315.json")
        self.audit = load("reports/BABEL_BB8_BEFORE_SOURCE_AUDIT_v315.json")
        self.qa = load("reports/QA_BABEL_v315.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v315.json")
        self.index = (ROOT / "events/BABEL_INDEX_v315.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_partial_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v3.15")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual((p["translated_text_positions"],p["total_source_text_positions"],p["remaining_text_positions"]),(40,200,160))
        self.assertFalse(p["complete"])
        self.assertEqual(p["next_text_ordinal"],41)
        self.assertEqual(p["next_text_source_line"],90)
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]],list(range(1,41)))
        self.assertEqual(p["translated_kind_counts"],{"named":33,"multiline":0,"narration":7,"subtitle":0,"sticker":0})
        self.assertEqual(p["remaining_kind_counts"],{"named":125,"multiline":2,"narration":33,"subtitle":0,"sticker":0})

    def test_source_line_map_and_kinds(self):
        expected=[13,14,19,24,26,28,30,31,33,35,36,38,40,41,43,45,46,47,49,51,53,55,57,59,61,63,65,66,68,70,71,73,77,79,80,81,82,83,86,88]
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]],expected)
        kinds=[x["kind"] for x in self.doc["dialogues"]]
        self.assertEqual((kinds.count("named"),kinds.count("narration"),kinds.count("multiline")),(33,7,0))

    def test_russian_text_is_clean(self):
        for x in self.doc["dialogues"]:
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]",x["text_ru"]))
            self.assertNotIn(chr(10),x["text_ru"])
            self.assertNotIn(chr(13),x["text_ru"])
            self.assertEqual(x["text_ru"].count("«"),x["text_ru"].count("»"))

    def test_speakers_and_cn_primary_choices(self):
        by={x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[3]["speaker_cn"],"尤莉叶")
        self.assertEqual(by[4]["speaker_cn"],"阿斯卡纶")
        self.assertEqual(by[39]["speaker_cn"],"尤莉叶")
        self.assertIn("захватить Каздель",by[19]["text_ru"])
        self.assertIn("почти не встречала Фелинов",by[21]["text_ru"])
        self.assertIn("не хочу, чтобы вы встречались",by[27]["text_ru"])
        self.assertIn("меня провожаешь именно ты",by[39]["text_ru"])

    def test_source_hashes_and_full_scene_alignment(self):
        s=self.doc["source"];a=self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"],"61daf6c0beeecfb442fd84a7dad26ea1110dac5b")
        self.assertEqual(s["en_git_blob_sha1"],"cbf456ffc623a5865f193132fb076857ec2e6c1a")
        self.assertEqual((s["cn_line_count"],s["en_line_count"]),(594,594))
        self.assertEqual((s["cn_text_total"],s["en_text_total"]),(200,200))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]),(394,394))
        self.assertTrue(s["en_extra_terminal_newline"])
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_speaker_tags_align"])
        self.assertFalse(a["cn_en_control_command_lines_match_exactly"])
        self.assertEqual(a["cn_en_control_command_difference_count"],2)
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_and_readme(self):
        row=next(x for x in self.index.splitlines() if "level_act33side_08_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9],["act33side","level_act33side_08_beg.txt","partial_first_draft","33","0","7","0","0","40"])
        self.assertEqual(self.qa["scene_translated_text_entries"],40)
        self.assertEqual(self.qa["scene_remaining_text_entries"],160)
        self.assertEqual(self.qa["babel_completed_files"],16)
        self.assertEqual(self.qa["babel_partial_files"],1)
        self.assertEqual(self.qa["babel_not_started_files"],6)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"],3609)
        self.assertEqual(self.manifest["version"],"v3.15")
        self.assertEqual(self.manifest["next_file"],"activities/act33side/level_act33side_08_beg.txt")
        self.assertEqual(self.manifest["next_text_ordinal"],41)
        self.assertEqual(self.manifest["next_text_source_line"],90)
        self.assertIn("40/200",self.readme)
        self.assertIn("№41, CN строка 90",self.readme)
        self.assertIn("149/149",self.readme)

    def test_audit_source_differences(self):
        self.assertEqual([x["ordinal"] for x in self.audit["documented_meaning_differences"]],[19,21,27,39])
        self.assertEqual([x["source_line"] for x in self.audit["documented_control_command_differences"]],[435,459])
        self.assertEqual([x["source_line"] for x in self.audit["documented_multiline_text_differences"]],[477,480])
        self.assertEqual(self.audit["segment"]["ordinals"],[1,40])
        self.assertEqual(self.audit["segment"]["next_ordinal"],41)
        self.assertEqual(self.audit["segment"]["next_source_line"],90)
        self.assertEqual(self.audit["source_totals"]["cn_control_commands"],394)

if __name__ == "__main__":
    unittest.main()
