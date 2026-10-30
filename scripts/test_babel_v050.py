# coding: utf-8
"""Babel BB-ST-1 v0.50 full first-draft and subtitle regression suite."""
import json
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT/path).read_text("utf-8"))

class BabelV050(unittest.TestCase):
    def setUp(self):
        self.doc=load("events/babel_st01_ru_v050.json")
        self.prior=load("events/babel_st01_opening_partial_ru_v049.json")

    def test_all_text_categories_and_contiguous_ordinals(self):
        d=self.doc;p=d["progress"];s=d["source"]
        self.assertEqual(d["version"],"v0.50")
        self.assertTrue(p["complete"])
        self.assertIn("NOT_GAME_TESTED",d["status"])
        self.assertEqual(p["source_lines_translated_through"],452)
        self.assertIsNone(p["next_source_line"])
        self.assertEqual((p["named_ru_lines"],p["plain_ru_lines"],p["sticker_ru_lines"],p["subtitle_ru_lines"]),(89,38,14,17))
        self.assertEqual((p["total_ru_text_entries"],p["source_total_text_entries"]),(158,158))
        for k,count in (("dialogues",89),("plain_dialogues",38),("sticker_texts",14),("subtitle_texts",17)):
            t=d[k]
            self.assertEqual(set(t),set(map(str,range(1,count+1))))
            for v in t.values():
                x=v if isinstance(v,str) else v["ru"]
                self.assertTrue(isinstance(x,str) and x.strip())
                self.assertFalse(any(c in x for c in "\t\r\n"))
        self.assertEqual((s["cn_git_blob_sha1"],s["en_git_blob_sha1"]),("b892ff9507ab142d39a0ea18876444c3269ec055","359381b0e52bae2a7811211ba908aeee0288b5f1"))
        self.assertEqual((s["cn_line_count"],s["en_line_count"]),(452,453))
        self.assertEqual((s["cn_subtitle_text_total"],s["en_subtitle_text_total"]),(17,17))

    def test_v049_preserved_no_retranslation(self):
        for k in ("dialogues","plain_dialogues","sticker_texts"):
            for ordinal,value in self.prior[k].items():
                self.assertEqual(self.doc[k][ordinal],value)
        self.assertEqual(self.prior["progress"]["source_lines_translated_through"],194)
        self.assertEqual(self.doc["segment_v050"]["source_line_start"],195)
        self.assertEqual(self.doc["segment_v050"]["source_line_end"],452)
        self.assertEqual((self.doc["segment_v050"]["new_named_ru_lines"],self.doc["segment_v050"]["new_plain_ru_lines"],self.doc["segment_v050"]["new_subtitle_ru_lines"]),(55,9,17))

    def test_original_positions_and_subtitle_only_text(self):
        s=self.doc["segment_v050"]
        self.assertEqual(len(s["named_source_lines"]),55)
        self.assertEqual(len(s["plain_source_lines"]),9)
        self.assertEqual(len(s["subtitle_source_lines"]),17)
        self.assertEqual(s["subtitle_source_lines"],[293,328,363,391,392,410,417,418,425,431,438,439,440,441,442,443,444])
        for num,position in enumerate(s["subtitle_source_lines"],start=1):
            obj=self.doc["subtitle_texts"][str(num)]
            self.assertEqual(obj["source_line"],position)
            self.assertIsInstance(obj["ru"],str)
            self.assertTrue(obj["ru"].strip())
        all_positions=s["named_source_lines"]+s["plain_source_lines"]+s["subtitle_source_lines"]
        self.assertEqual(len(all_positions),len(set(all_positions)))
        self.assertTrue(all(pos>=195 for pos in all_positions))
        self.assertIn("Жюли",self.doc["dialogues"]["50"])
        self.assertIn("Терезия",self.doc["dialogues"]["80"])
        self.assertIn("Кальцит",self.doc["subtitle_texts"]["1"]["ru"])

    def test_index_manifest_audit_readme(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v050.json")
        a=load("reports/BABEL_ST01_SOURCE_AUDIT_v050.json")
        q=load("reports/QA_BABEL_v050.json")
        idx=(ROOT/"events/BABEL_INDEX_v050.tsv").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        self.assertEqual(m["next_file"],"activities/act33side/level_act33side_01_beg.txt")
        self.assertEqual(m["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(m["translation_integrity"]["babel_completed_ru_text_entries"],158)
        self.assertIn("level_act33side_st01.txt\tfirst_draft_complete\t89\t38\t14",idx)
        self.assertEqual((q["new_named_ru_lines"],q["new_plain_ru_lines"],q["new_subtitle_ru_lines"]),(55,9,17))
        self.assertEqual(q["new_total_ru_text_entries"],81)
        self.assertEqual(q["full_scene_ru_text_entries"],158)
        self.assertTrue(q["prior_77_entries_unchanged"])
        self.assertTrue(a["alignment"]["all_text_kinds_and_source_positions_identical"])
        self.assertFalse(a["alignment"]["semantic_alignment_confirmed"])
        self.assertEqual(a["sources"]["cn"]["git_blob_sha1"],self.doc["source"]["cn_git_blob_sha1"])
        self.assertEqual(a["sources"]["en"]["git_blob_sha1"],self.doc["source"]["en_git_blob_sha1"])
        self.assertIn("events/babel_st01_ru_v050.json",readme)

if __name__=="__main__":
    unittest.main()
