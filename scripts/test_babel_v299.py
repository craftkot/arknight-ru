# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6V299(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_before_partial_ru_v299.json")
        self.old = load("events/babel_bb6_before_partial_ru_v298.json")
        self.audit = load("reports/BABEL_BB6_BEFORE_SOURCE_AUDIT_v299.json")
        self.qa = load("reports/QA_BABEL_v299.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v299.json")
        self.index = (ROOT / "events/BABEL_INDEX_v299.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_progress_and_ordinals(self):
        p = self.doc["progress"]
        self.assertEqual(self.doc["version"], "v2.99")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (228, 258, 30))
        self.assertFalse(p["complete"])
        self.assertEqual((p["last_source_line"], p["next_source_line"], p["next_text_ordinal"], p["next_text_source_line"]), (693, 694, 229, 695))
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 229)))

    def test_previous_198_positions_preserved(self):
        for old in self.old["dialogues"]:
            self.assertEqual(self.doc["dialogues"][old["ordinal"] - 1], old)

    def test_new_segment_positions_and_kinds(self):
        expected = [601,603,605,607,608,610,611,613,615,626,636,637,639,641,643,655,662,663,664,665,666,678,679,683,685,687,689,691,692,693]
        new = self.doc["dialogues"][198:]
        self.assertEqual(len(new), 30)
        self.assertEqual([x["source_line"] for x in new], expected)
        self.assertEqual([x["ordinal"] for x in new], list(range(199,229)))
        kinds = {}
        for x in self.doc["dialogues"]:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(c) <= 0x9fff for c in x["text_ru"]))
            self.assertNotIn(chr(10), x["text_ru"])
            self.assertNotIn(chr(13), x["text_ru"])
        self.assertEqual(kinds, {"named":186,"multiline":11,"narration":31})
        self.assertEqual(new[0]["speaker_cn"], "博士")
        self.assertEqual(new[16]["kind"], "narration")
        self.assertEqual(new[21]["speaker_cn"], "凯尔希")
        self.assertEqual(new[-1]["speaker_cn"], "凯尔希")
        self.assertIn("Король Бабеля", new[17]["text_ru"])

    def test_source_alignment_and_hashes(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual((s["cn_git_blob_sha1"], s["en_git_blob_sha1"]), ("0fa57f8b2c4647c06bce0ba73008798d340a781c", "47a63283cb5d1c42e205f6bcebbf1e9cc134ac03"))
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (770,771))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (258,258))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (512,512))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertTrue(a["segment_cn_en_line_alignment"])
        self.assertTrue(a["segment_cn_en_speaker_tags_align"])
        self.assertEqual(a["segment_new_text_positions"], 30)
        self.assertEqual(a["next_ordinal"], 229)
        self.assertEqual(a["next_text_source_line"], 695)
        self.assertTrue(a["previous_198_entries_preserved"])

    def test_audit_qa_index_chronology_readme(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 30)
        self.assertTrue(self.audit["translated_segment"]["previous_198_preserved"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 30)
        self.assertEqual(self.qa["scene_ru_text_entries"], 228)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 30)
        self.assertTrue(self.qa["previous_198_entries_unchanged"])
        row = next(line for line in self.index.splitlines() if "level_act33side_06_beg.txt" in line)
        self.assertEqual(row.split(chr(9))[:9], ["act33side","level_act33side_06_beg.txt","partial_first_draft","186","11","31","0","0","228"])
        self.assertEqual(self.manifest["partial_scene_next_text_ordinal"], 229)
        self.assertEqual(self.manifest["partial_scene_next_source_line"], 695)
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 228)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 2990)
        self.assertIn("BB-6 до боя: 228/258", self.readme)
        self.assertIn("№229", self.readme)
        self.assertIn("CN строка 695", self.readme)

if __name__ == "__main__":
    unittest.main()
