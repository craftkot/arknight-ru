# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6V296(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_before_partial_ru_v296.json")
        self.old = load("events/babel_bb6_before_partial_ru_v295.json")
        self.audit = load("reports/BABEL_BB6_BEFORE_SOURCE_AUDIT_v296.json")
        self.qa = load("reports/QA_BABEL_v296.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v296.json")
        self.index = (ROOT / "events/BABEL_INDEX_v296.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_progress_and_ordinals(self):
        d, p = self.doc, self.doc["progress"]
        self.assertEqual(d["version"], "v2.96")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (144, 258, 114))
        self.assertFalse(p["complete"])
        self.assertEqual((p["last_source_line"], p["next_source_line"], p["next_text_ordinal"], p["next_text_source_line"]), (448, 449, 145, 469))
        self.assertEqual([x["ordinal"] for x in d["dialogues"]], list(range(1, 145)))

    def test_previous_114_positions_preserved(self):
        for old in self.old["dialogues"]:
            self.assertEqual(self.doc["dialogues"][old["ordinal"] - 1], old)

    def test_new_segment_positions_and_kinds(self):
        expected = [332,333,334,338,339,363,364,365,367,387,393,398,402,418,419,421,426,428,429,431,432,434,439,440,441,443,444,445,447,448]
        new = self.doc["dialogues"][114:]
        self.assertEqual(len(new), 30)
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = {}
        for x in self.doc["dialogues"]:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(any(0x4e00 <= ord(c) <= 0x9fff for c in x["text_ru"]))
            self.assertNotIn("\\n", x["text_ru"])
            self.assertNotIn("\\r", x["text_ru"])
        self.assertEqual(kinds, {"named":117,"multiline":11,"narration":16})
        self.assertEqual(new[21]["source_tag_attributes"], {"end": True})

    def test_source_alignment_and_content_difference(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual((s["cn_git_blob_sha1"], s["en_git_blob_sha1"]), ("0fa57f8b2c4647c06bce0ba73008798d340a781c", "47a63283cb5d1c42e205f6bcebbf1e9cc134ac03"))
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (770,771))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (258,258))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (512,512))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertFalse(a["cn_en_exact_control_command_text_match"])
        self.assertEqual([x["source_line"] for x in a["cn_en_exact_control_command_differences"]], [372,374])
        self.assertEqual(a["cn_en_content_differences"][0]["source_line"], 445)
        self.assertEqual(a["cn_en_content_differences"][0]["ru_rendering"], "«Дейл». Дом.")

    def test_audit_qa_index_and_chronology(self):
        self.assertEqual(self.audit["translated_segment"]["new_text_positions"], 30)
        self.assertTrue(self.audit["translated_segment"]["previous_114_preserved"])
        self.assertEqual(self.qa["new_total_ru_text_entries"], 30)
        self.assertEqual(self.qa["scene_ru_text_entries"], 144)
        self.assertTrue(self.qa["previous_114_entries_unchanged"])
        self.assertIn("level_act33side_06_beg.txt\\tpartial_first_draft\\t117\\t11\\t16\\t0\\t0\\t144", self.index)
        self.assertEqual(self.manifest["partial_scene_next_text_ordinal"], 145)
        self.assertEqual(self.manifest["partial_scene_next_source_line"], 469)
        self.assertEqual(self.manifest["translation_integrity"]["babel_partial_ru_text_entries"], 144)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 2906)
        self.assertIn("BB-6 до боя: 144/258", self.readme)
        self.assertIn("babel_bb6_before_partial_ru_v296.json", self.readme)

if __name__ == "__main__":
    unittest.main()
