# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

EXPECTED_LINES = [12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,37,38,39,40,41,42,43,44,45,46,56,57,58,60,61,62,65,66,67,69,82,83,84,86,87,88,90,91,95,97,98,99,102,104,105,107,116,117,118,119,120,121,123,124,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,168,170,171,172,174,175,177,179,180,181,182,183,184,185,186,188,190,191,200,201,202,206,210,214,215,219,223,224,225,229,233,235,236,252,255,256,257,258,259,260,261,262,270,273,274,275,279,280,281,284,285,286,287,291,294,298,302,303,304,305,309,312,313,321,324,325,326,327,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,356,360,362,364,366,368,370,372,373,382,390,392,394,396,397,405,409,410,412,415,416,419,427,428,429,430,431,432,440,445,446,448,450,451,453,455,456,457,458,460,462,463,464,466,468,469,471,473,484,485,486,487,488,489,498,500,502,503,505,506,508,509,511,512,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,541,542,543,544,545,546,547,548,551]

class BabelBB10AfterV329(unittest.TestCase):
    def setUp(self):
        self.doc=load("events/babel_bb10_after_ru_v329.json")
        self.audit=load("reports/BABEL_BB10_AFTER_SOURCE_AUDIT_v329.json")
        self.qa=load("reports/QA_BABEL_v329.json")
        self.manifest=load("chronology/CHRONOLOGY_MANIFEST_v329.json")
        self.index=(ROOT/"events/BABEL_INDEX_v329.tsv").read_text(encoding="utf-8")
        self.readme=(ROOT/"README.md").read_text(encoding="utf-8")
        self.terms=(ROOT/"docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.previous=load("events/babel_bb10_before_ru_v328.json")

    def test_ordinals_and_source_lines(self):
        self.assertEqual(self.doc["version"],"v3.29")
        self.assertEqual(self.doc["status"],"first_draft_complete")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]],list(range(1,253)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]],EXPECTED_LINES)
        p=self.doc["progress"]
        self.assertEqual((p["translated_text_positions"],p["total_source_text_positions"],p["remaining_text_positions"]),(252,252,0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertEqual(self.doc["source_file"],"activities/act33side/level_act33side_10_end.txt")

    def test_kinds_and_control_only_sticker(self):
        kinds={k:sum(x["kind"]==k for x in self.doc["dialogues"]) for k in ("named","multiline","narration","sticker","subtitle","decision")}
        self.assertEqual(kinds,{"named":191,"multiline":2,"narration":40,"sticker":1,"subtitle":18,"decision":0})
        st=self.audit["structural_comparison"]["nontext_sticker_command_without_text_payload"]
        self.assertEqual(st["source_line"],552)
        self.assertTrue(st["preserved_as_control"])

    def test_speakers_and_multiline(self):
        by={x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[4]["speaker_cn"],"特蕾西娅")
        self.assertEqual(by[36]["speaker_cn"],"凯尔希")
        self.assertEqual(by[56]["speaker_cn"],"“阿米娅”")
        self.assertEqual(by[140]["speaker_cn"],"阿斯卡纶")
        self.assertEqual(by[164]["speaker_cn"],"Ace")
        self.assertEqual(by[173]["speaker_cn"],"孽茨雷")
        self.assertEqual(by[174]["speaker_cn"],"杜卡雷")
        self.assertEqual(by[179]["speaker_cn"],"W")
        self.assertEqual(by[205]["kind"],"multiline")
        self.assertEqual(by[206]["kind"],"multiline")
        self.assertEqual(by[252]["kind"],"sticker")

    def test_russian_and_cn_semantics(self):
        by={x["ordinal"]:x for x in self.doc["dialogues"]}
        for e in self.doc["dialogues"]:
            self.assertTrue(e["text_ru"].strip())
            self.assertFalse(any(0x3400<=ord(ch)<=0x9fff for ch in e["text_ru"]))
            self.assertNotIn(chr(10),e["text_ru"])
            self.assertNotIn(chr(13),e["text_ru"])
        self.assertIn("убила",by[75]["text_ru"])
        self.assertIn("спасла",by[75]["text_ru"])
        self.assertIn("сохранение цивилизации",by[90]["text_ru"])
        self.assertIn("десять тысяч лет",by[127]["text_ru"])
        self.assertIn("возродятся в огне",by[133]["text_ru"])
        self.assertIn("до падения Казделя",by[186]["text_ru"])
        self.assertIn("Печи душ",by[187]["text_ru"])
        self.assertEqual(by[252]["text_ru"],"Мы всегда будем равны.")

    def test_source_hashes_and_alignment(self):
        s,a=self.doc["source"],self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"],"1d8756b3595f75c6e641592afed3d6b84b744085")
        self.assertEqual(s["en_git_blob_sha1"],"50ee3958ac9d053b0707cf39edb00d1d831686d7")
        self.assertEqual((s["cn_line_count"],s["en_line_count"]),(556,557))
        self.assertEqual((s["cn_text_total"],s["en_text_total"]),(252,252))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]),(304,304))
        self.assertTrue(s["en_extra_terminal_newline"])
        for k in ("cn_en_text_positions_match","cn_en_text_type_sequence_match","cn_en_source_line_positions_match","cn_en_speaker_tag_positions_align","cn_en_nontext_control_commands_match_exactly"):
            self.assertTrue(a[k])
        self.assertEqual(a["cn_en_normalized_structural_difference_count"],0)
        self.assertEqual(a["segment_ordinals"],[1,252])
        self.assertEqual(a["segment_source_lines"],EXPECTED_LINES)
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"],[])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_qa_manifest_index_readme_glossary_and_previous(self):
        self.assertEqual(self.qa["new_total_ru_text_entries"],252)
        self.assertEqual(self.qa["babel_completed_files"],22)
        self.assertEqual(self.qa["babel_not_started_files"],1)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"],4511)
        self.assertEqual(self.qa["next_file"],"activities/act33side/level_act33side_st03.txt")
        self.assertEqual(self.manifest["version"],"v3.29")
        self.assertEqual(self.manifest["next_file"],"activities/act33side/level_act33side_st03.txt")
        ti=self.manifest["translation_integrity"]
        self.assertEqual(ti["babel_completed_files"],22)
        self.assertEqual(ti["babel_completed_ru_text_entries"],4511)
        row=next(x for x in self.index.splitlines() if "level_act33side_10_end.txt" in x).split(chr(9))
        self.assertEqual(row[2:9],["first_draft_complete","191","2","40","1","18","252"])
        self.assertEqual(row[9:11],["1d8756b3595f75c6e641592afed3d6b84b744085","50ee3958ac9d053b0707cf39edb00d1d831686d7"])
        self.assertIn("v3.29",self.readme)
        self.assertIn("4 511",self.readme)
        self.assertIn("BB-ST-3",self.readme)
        self.assertIn("Pith / 术髓 — Пит",self.terms)
        self.assertIn("Soul Furnace / 魂灵熔炉 — Печь душ",self.terms)
        self.assertEqual(len(self.previous["dialogues"]),56)
        self.assertTrue(self.audit["scene_complete"])

if __name__=="__main__":
    unittest.main()
