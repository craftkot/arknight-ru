# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB7BeforeV310(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb7_before_ru_v310.json")
        self.previous = load("events/babel_bb7_before_partial_ru_v309.json")
        self.audit = load("reports/BABEL_BB7_BEFORE_SOURCE_AUDIT_v310.json")
        self.qa = load("reports/QA_BABEL_v310.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v310.json")
        self.index = (ROOT / "events/BABEL_INDEX_v310.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_complete_progress_and_ordinals(self):
        p=self.doc["progress"]
        self.assertEqual(self.doc["version"],"v3.10")
        self.assertEqual(self.doc["status"],"first_draft_complete")
        self.assertEqual((p["translated_text_positions"],p["total_source_text_positions"],p["remaining_text_positions"]),(222,222,0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertIsNone(p["next_text_source_line"])
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]],list(range(1,223)))
        self.assertEqual(len(self.doc["dialogues"]),222)

    def test_previous_200_entries_are_preserved(self):
        self.assertEqual(self.doc["dialogues"][:200],self.previous["dialogues"])

    def test_final_segment_lines_and_kinds(self):
        expected=[390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,417,418,423,424,425,426]
        new=self.doc["dialogues"][200:]
        self.assertEqual([x["ordinal"] for x in new],list(range(201,223)))
        self.assertEqual([x["source_line"] for x in new],expected)
        kinds=[x["kind"] for x in new]
        self.assertEqual((kinds.count("named"),kinds.count("multiline"),kinds.count("narration"),kinds.count("subtitle"),kinds.count("sticker")),(16,0,6,0,0))
        self.assertEqual(self.doc["progress"]["translated_kind_counts"],{"named":186,"multiline":2,"narration":26,"subtitle":8,"sticker":0})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"],{"named":0,"multiline":0,"narration":0,"subtitle":0,"sticker":0})

    def test_russian_text_placeholders_and_markup(self):
        for item in self.doc["dialogues"]:
            self.assertTrue(item["text_ru"].strip())
            self.assertFalse(re.search(r"[\u3400-\u9fff]",item["text_ru"]))
            self.assertNotIn(chr(10),item["text_ru"])
            self.assertNotIn(chr(13),item["text_ru"])
            self.assertEqual(item["text_ru"].count("<i>"),item["text_ru"].count("</i>"))
            self.assertEqual(item["text_ru"].count("<color="),item["text_ru"].count("</color>"))
        by={x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertIn("{@nickname}",by[211]["text_ru"])
        self.assertIn("{@nickname}",by[214]["text_ru"])
        self.assertIn("«героями»",by[221]["text_ru"])

    def test_cn_primary_meaning_and_speakers(self):
        by={x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[202]["speaker_cn"],"博士")
        self.assertEqual(by[203]["speaker_cn"],"特雷西斯")
        self.assertEqual(by[212]["speaker_cn"],"特雷西斯")
        self.assertEqual(by[213]["speaker_cn"],"博士")
        self.assertEqual(by[216]["speaker_cn"],"特雷西斯")
        self.assertIn("судьбой сарказов",by[216]["text_ru"])
        self.assertIn("свести потери к минимуму",by[209]["text_ru"])
        self.assertIn("судить тебя за твои грехи",by[215]["text_ru"])

    def test_source_alignment_and_documented_differences(self):
        s=self.doc["source"];a=self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"],"605fede5533907ce926d038129da2abb2af57af7")
        self.assertEqual(s["en_git_blob_sha1"],"63c0f520b4f0de80ea34b4dd0afbbc4cb2df9f5b")
        self.assertEqual((s["cn_line_count"],s["en_line_count"]),(434,434))
        self.assertEqual((s["cn_text_total"],s["en_text_total"]),(222,222))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]),(212,212))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_control_command_lines_match_exactly"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_text_type_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertFalse(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["segment_cn_en_markup_alignment_except_documented_difference"])
        markup={x["ordinal"]:x for x in a["documented_source_markup_differences"]}
        meaning={x["ordinal"]:x for x in a["documented_source_meaning_differences"]}
        self.assertEqual(markup[221]["source_line"],425)
        self.assertEqual(meaning[215]["source_line"],404)
        self.assertEqual(meaning[216]["source_line"],405)
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_index_manifest_qa_readme(self):
        row=next(x for x in self.index.splitlines() if "level_act33side_07_beg.txt" in x)
        self.assertEqual(row.split(chr(9))[:9],["act33side","level_act33side_07_beg.txt","first_draft_complete","186","2","26","0","8","222"])
        self.assertEqual(self.qa["scene_translated_text_entries"],222)
        self.assertEqual(self.qa["scene_remaining_text_entries"],0)
        self.assertEqual(self.qa["babel_completed_files"],15)
        self.assertEqual(self.qa["babel_partial_files"],0)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"],3420)
        self.assertEqual(self.manifest["version"],"v3.10")
        self.assertEqual(self.manifest["next_file"],"activities/act33side/level_act33side_07_end.txt")
        self.assertEqual(self.manifest["next_scene"],"Babel BB-7 after battle")
        self.assertEqual(self.manifest["translation_integrity"]["babel_completed_ru_text_entries"],3420)
        self.assertIn("222/222",self.readme)
        self.assertIn("BB-7 после боя",self.readme)

if __name__ == "__main__":
    unittest.main()
