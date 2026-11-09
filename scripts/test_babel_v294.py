# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB6V294(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb6_before_partial_ru_v294.json")
        self.old = load("events/babel_bb6_before_partial_ru_v293.json")
        self.audit = load("reports/BABEL_BB6_BEFORE_SOURCE_AUDIT_v294.json")
        self.qa = load("reports/QA_BABEL_v294.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v294.json")
        self.index = (ROOT / "events/BABEL_INDEX_v294.tsv").read_text(encoding="utf-8")

    def test_progress_and_ordinals(self):
        d, p = self.doc, self.doc["progress"]
        self.assertEqual(d["version"], "v2.94")
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (87, 258, 171))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"], p["next_text_source_line"]), (88, 263))
        self.assertEqual(p["last_source_line"], 253)
        self.assertEqual([x["ordinal"] for x in d["dialogues"]], list(range(1, 88)))

    def test_previous_57_positions_preserved(self):
        for old in self.old["dialogues"]:
            self.assertEqual(self.doc["dialogues"][old["ordinal"] - 1], old)

    def test_new_segment_source_positions_and_kinds(self):
        expected = [166,168,169,170,191,192,193,196,197,217,218,221,222,223,230,232,234,235,237,239,240,241,243,245,246,248,250,251,252,253]
        new = self.doc["dialogues"][57:]
        self.assertEqual(len(new), 30)
        self.assertEqual([x["source_line"] for x in new], expected)
        kinds = {}
        for x in self.doc["dialogues"]:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
            self.assertTrue(x["text_ru"].strip())
            self.assertFalse(any(0x4e00 <= ord(c) <= 0x9fff for c in x["text_ru"]))
            self.assertNotIn("\n", x["text_ru"])
            self.assertNotIn("\r", x["text_ru"])
        self.assertEqual(kinds, {"named":66,"multiline":9,"narration":12})
        self.assertEqual(self.doc["dialogues"][69]["source_tag_attributes"], {"end": True})

    def test_source_alignment_and_blob_hashes(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual((s["cn_git_blob_sha1"], s["en_git_blob_sha1"]), ("0fa57f8b2c4647c06bce0ba73008798d340a781c", "47a63283cb5d1c42e205f6bcebbf1e9cc134ac03"))
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (770,771))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (258,258))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (512,512))
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_control_command_positions_match"])
        self.assertFalse(a["cn_en_exact_control_command_text_match"])
        self.assertEqual([x["source_line"] for x in a["cn_en_exact_control_command_differences"]], [372,374])
        self.assertEqual(a["decision_count"], 0)

    def test_index_qa_and_chronology(self):
        self.assertIn("level_act33side_06_beg.txt\tpartial_first_draft\t66\t9\t12\t0\t0\t87", self.index)
        self.assertEqual(self.qa["new_total_ru_text_entries"], 30)
        self.assertTrue(self.qa["previous_57_entries_unchanged"])
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_06_beg.txt")
        self.assertEqual(self.manifest["partial_scene_next_text_ordinal"], 88)
        self.assertEqual(self.manifest["partial_scene_next_source_line"], 263)
        self.assertEqual(self.manifest["active_translation_track"], "terra_chronology_event_order")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("BB-6 до боя:", readme)

if __name__ == "__main__":
    unittest.main()
