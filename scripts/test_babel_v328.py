# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

EXPECTED_LINES = [11,12,13,16,17,19,23,24,25,27,29,30,31,33,35,37,38,40,42,43,44,46,48,49,51,53,55,56,57,59,61,63,64,66,68,72,73,74,77,78,79,80,81,105,106,107,108,116,117,118,119,120,132,140,141,144]

class BabelBB10BeforeV328(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb10_before_ru_v328.json")
        self.audit = load("reports/BABEL_BB10_BEFORE_SOURCE_AUDIT_v328.json")
        self.qa = load("reports/QA_BABEL_v328.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v328.json")
        self.index = (ROOT / "events/BABEL_INDEX_v328.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_complete_ordinals_and_source_lines(self):
        self.assertEqual(self.doc["version"], "v3.28")
        self.assertEqual(self.doc["status"], "first_draft_complete")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1, 57)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], EXPECTED_LINES)
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"], p["total_source_text_positions"], p["remaining_text_positions"]), (56, 56, 0))
        self.assertTrue(p["complete"])
        self.assertIsNone(p["next_text_ordinal"])
        self.assertEqual(self.doc["source_file"], "activities/act33side/level_act33side_10_beg.txt")

    def test_kinds_speakers_and_subtitle(self):
        kinds = {k: sum(x["kind"] == k for x in self.doc["dialogues"]) for k in ("named", "multiline", "narration", "sticker", "subtitle", "decision")}
        self.assertEqual(kinds, {"named": 39, "multiline": 0, "narration": 16, "sticker": 0, "subtitle": 1, "decision": 0})
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertEqual(by[4]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[8]["speaker_cn"], "博士")
        self.assertEqual(by[56]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[53]["kind"], "subtitle")
        self.assertIn("<color=#000000>", by[53]["text_ru"])
        self.assertIn("</color>", by[53]["text_ru"])

    def test_speaker_metadata_and_unique_source_lines(self):
        lines = [x["source_line"] for x in self.doc["dialogues"]]
        self.assertEqual(len(lines), len(set(lines)))
        self.assertEqual(lines, sorted(lines))
        for entry in self.doc["dialogues"]:
            if entry["kind"] == "named":
                self.assertTrue(entry.get("speaker_cn"))
            else:
                self.assertNotIn("speaker_cn", entry)

    def test_russian_text_and_placeholders(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertFalse(any(0x3400 <= ord(ch) <= 0x9fff for ch in entry["text_ru"]))
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
        self.assertEqual(self.doc["dialogues"][33]["text_ru"].count("{@nickname}"), 1)
        self.assertEqual(self.doc["dialogues"][42]["text_ru"].count("{@nickname}"), 1)

    def test_cn_primary_semantic_resolutions(self):
        by = {x["ordinal"]: x for x in self.doc["dialogues"]}
        self.assertIn("бесчисленных жизней", by[8]["text_ru"])
        self.assertIn("десяти тысяч лет", by[8]["text_ru"])
        self.assertIn("замысел ориджиниума", by[9]["text_ru"])
        self.assertIn("Король Сарказов", by[12]["text_ru"])
        self.assertIn("не погибли", by[16]["text_ru"])
        self.assertIn("застывший ориджиниум", by[28]["text_ru"])
        self.assertIn("одну загадку", by[54]["text_ru"])
        self.assertEqual(len(self.doc["semantic_differences"]), 7)
        self.assertFalse(self.doc["editorial_review"])
        self.assertFalse(self.doc["in_game_test"])
        self.assertFalse(self.doc["game_behavior_verified"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "e3564145cb5548b9c4654692d27458cf64eb231f")
        self.assertEqual(s["en_git_blob_sha1"], "6385255d6d3d911024ee8800c882cf2bb3781be7")
        self.assertEqual((s["cn_line_count"], s["en_line_count"]), (156, 157))
        self.assertEqual((s["cn_text_total"], s["en_text_total"]), (56, 56))
        self.assertEqual((s["cn_control_command_total"], s["en_control_command_total"]), (100, 100))
        self.assertTrue(s["en_extra_terminal_newline"])
        self.assertTrue(a["cn_en_text_positions_match"])
        self.assertTrue(a["cn_en_text_type_sequence_match"])
        self.assertTrue(a["cn_en_source_line_positions_match"])
        self.assertTrue(a["cn_en_speaker_tag_positions_align"])
        self.assertTrue(a["cn_en_nontext_control_commands_match_exactly"])
        self.assertEqual(a["segment_ordinals"], [1, 56])
        self.assertEqual(a["segment_source_lines"], EXPECTED_LINES)
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertTrue(a["segment_cn_en_markup_alignment"])
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertTrue(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_qa_manifest_index_readme_and_previous_scene(self):
        self.assertEqual(self.qa["version"], "v3.28")
        self.assertEqual(self.qa["new_total_ru_text_entries"], 56)
        self.assertEqual(self.qa["babel_completed_files"], 21)
        self.assertEqual(self.qa["babel_not_started_files"], 2)
        self.assertEqual(self.qa["babel_completed_ru_text_entries"], 4259)
        self.assertEqual(self.qa["next_file"], "activities/act33side/level_act33side_10_end.txt")
        self.assertEqual(self.manifest["version"], "v3.28")
        self.assertEqual(self.manifest["next_file"], "activities/act33side/level_act33side_10_end.txt")
        self.assertEqual(self.manifest["translation_integrity"]["babel_completed_files"], 21)
        self.assertEqual(self.manifest["translation_integrity"]["babel_completed_ru_text_entries"], 4259)
        row = next(x for x in self.index.splitlines() if "level_act33side_10_beg.txt" in x).split(chr(9))
        self.assertEqual(row[2:9], ["first_draft_complete", "39", "0", "16", "0", "1", "56"])
        self.assertEqual(row[9:11], ["e3564145cb5548b9c4654692d27458cf64eb231f", "6385255d6d3d911024ee8800c882cf2bb3781be7"])
        self.assertIn("v3.28", self.readme)
        self.assertIn("BB-10 после боя", self.readme)
        prior = load("events/babel_bb9_before_ru_v326.json")
        prior_after = load("events/babel_bb9_after_ru_v327.json")
        self.assertEqual(len(prior["dialogues"]), 106)
        self.assertEqual(len(prior_after["dialogues"]), 87)
        self.assertTrue(self.audit["scene_complete"])
        self.assertEqual(self.audit["segment"]["ordinals"], [1, 56])

if __name__ == "__main__":
    unittest.main()
