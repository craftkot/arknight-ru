# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelBB8AfterV323(unittest.TestCase):
    def setUp(self):
        self.doc = load("events/babel_bb8_after_partial_ru_v323.json")
        self.previous = load("events/babel_bb8_after_partial_ru_v322.json")
        self.audit = load("reports/BABEL_BB8_AFTER_SOURCE_AUDIT_v323.json")
        self.qa = load("reports/QA_BABEL_v323.json")
        self.manifest = load("chronology/CHRONOLOGY_MANIFEST_v323.json")
        self.index = (ROOT / "events/BABEL_INDEX_v323.tsv").read_text(encoding="utf-8")
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

    def test_cumulative_ordinals_lines_and_prefix(self):
        expected = [461,462,463,468,472,473,474,479,490,491,492,493,502,509,518,525,526,541,542,546,547,549,557,558,559,562,563,564,565,566,567,573,575,577,579,587,588,589,590,591]
        self.assertEqual(self.doc["version"], "v3.23")
        self.assertEqual(self.doc["status"], "partial_first_draft")
        self.assertEqual([x["ordinal"] for x in self.doc["dialogues"]], list(range(1,161)))
        self.assertEqual([x["source_line"] for x in self.doc["dialogues"]], [
            12,15,16,17,18,19,20,21,33,34,35,36,40,42,44,45,47,48,50,51,52,54,59,60,62,63,94,95,105,112,113,114,130,132,134,135,137,140,141,144,
            158,159,163,176,178,196,198,217,218,219,220,224,226,228,229,230,231,233,243,244,250,271,279,280,286,292,293,298,299,300,309,310,316,317,319,321,322,326,327,328,
            329,341,342,343,345,347,348,349,351,353,355,357,358,362,364,365,367,369,370,371,373,374,386,387,393,399,401,403,405,420,421,427,432,434,435,437,457,458,459,460,
            461,462,463,468,472,473,474,479,490,491,492,493,502,509,518,525,526,541,542,546,547,549,557,558,559,562,563,564,565,566,567,573,575,577,579,587,588,589,590,591
        ])
        self.assertEqual(self.doc["dialogues"][:120], self.previous["dialogues"])
        self.assertTrue(self.doc["previous_entries_preserved"])
        p = self.doc["progress"]
        self.assertEqual((p["translated_text_positions"],p["total_source_text_positions"],p["remaining_text_positions"]), (160,241,81))
        self.assertFalse(p["complete"])
        self.assertEqual((p["next_text_ordinal"],p["next_text_source_line"]), (161,592))

    def test_new_fragment_kind_counts(self):
        new = [x for x in self.doc["dialogues"] if 121 <= x["ordinal"] <= 160]
        kinds = {k:sum(x["kind"]==k for x in new) for k in ("named","multiline","narration","sticker","subtitle","decision")}
        self.assertEqual(kinds, {"named":14,"multiline":0,"narration":0,"sticker":14,"subtitle":12,"decision":0})
        self.assertEqual(self.doc["progress"]["translated_kind_counts"], {"named":102,"multiline":2,"narration":20,"sticker":24,"subtitle":12,"decision":0})
        self.assertEqual(self.doc["progress"]["remaining_kind_counts"], {"named":39,"multiline":0,"narration":6,"sticker":31,"subtitle":0,"decision":5})

    def test_russian_text_invariants(self):
        for entry in self.doc["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertNotRegex(entry["text_ru"], r"[\u3400-\u9fff]")
            self.assertNotIn(chr(10), entry["text_ru"])
            self.assertNotIn(chr(13), entry["text_ru"])
            self.assertEqual(entry["text_ru"].count("«"), entry["text_ru"].count("»"))

    def test_speakers_markup_and_placeholders(self):
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertEqual(by[121]["speaker_cn"], "博士")
        self.assertEqual(by[138]["speaker_cn"], "特蕾西娅")
        self.assertEqual(by[156]["speaker_cn"], "预言家")
        self.assertIn("«сохранением цивилизации»", by[123]["text_ru"])
        self.assertIn("{@nickname}", by[126]["text_ru"])
        self.assertIn("<color=#FF4200>", by[127]["text_ru"])
        self.assertIn("<color=#000000>", by[130]["text_ru"])
        self.assertEqual(by[152]["text_ru"], "<color=#888888>???</color>")
        self.assertEqual(by[155]["kind"], "sticker")
        self.assertEqual(by[160]["speaker_cn"], "预言家")

    def test_cn_primary_meaning_choices(self):
        by = {x["ordinal"]:x for x in self.doc["dialogues"]}
        self.assertIn("кровавым пятном", by[121]["text_ru"])
        self.assertIn("десяти миллиардов", by[130]["text_ru"])
        self.assertIn("барьерного слоя", by[130]["text_ru"])
        self.assertIn("далеки от идеала", by[134]["text_ru"])
        self.assertIn("Он уже совсем близко", by[137]["text_ru"])
        self.assertIn("партитура", by[155]["text_ru"])
        self.assertIn("самовольных действий", by[159]["text_ru"])
        self.assertFalse(self.doc["editorial_review"])
        self.assertFalse(self.doc["in_game_test"])

    def test_source_hashes_and_alignment(self):
        s, a = self.doc["source"], self.doc["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "502baa017ba32f5d3359d2caeedd2adafc72cd2a")
        self.assertEqual(s["en_git_blob_sha1"], "f5b13d3e11d4be6c3d4412eff082ae606fe586b4")
        self.assertEqual((s["cn_line_count"],s["en_line_count"]), (790,791))
        self.assertEqual((s["cn_text_total"],s["en_text_total"]), (241,241))
        self.assertEqual((s["cn_control_command_total"],s["en_control_command_total"]), (549,549))
        for key in ("cn_en_text_positions_match","cn_en_text_type_sequence_match","cn_en_source_line_positions_match","cn_en_speaker_tag_positions_align","cn_en_nontext_control_commands_match_exactly"):
            self.assertTrue(a[key])
        self.assertEqual(a["segment_ordinals"], [121,160])
        self.assertEqual(a["segment_source_lines"], [x["source_line"] for x in self.doc["dialogues"][120:160]])
        self.assertTrue(a["segment_cn_en_control_commands_match_exactly"])
        self.assertEqual(a["segment_cn_en_control_command_difference_source_lines"], [])
        self.assertFalse(a["scene_complete"])
        self.assertFalse(a["game_behavior_verified"])

    def test_audit_qa_index_manifest_readme_and_terms(self):
        self.assertEqual(self.audit["segment"]["ordinals"], [121,160])
        self.assertEqual(self.audit["segment"]["text_positions"], 40)
        self.assertEqual(self.audit["segment"]["kind_counts"], {"named":14,"multiline":0,"narration":0,"sticker":14,"subtitle":12,"decision":0})
        self.assertEqual(self.qa["new_total_ru_text_entries"], 40)
        self.assertEqual(self.qa["scene_translated_text_entries"], 160)
        self.assertEqual(self.qa["scene_remaining_text_entries"], 81)
        self.assertEqual(self.qa["babel_partial_ru_text_entries"], 160)
        self.assertEqual(self.qa["babel_ru_text_entries_including_partial"], 3929)
        self.assertEqual(self.qa["next_text_ordinal"], 161)
        self.assertEqual(self.qa["next_text_source_line"], 592)
        row = next(x for x in self.index.splitlines() if "level_act33side_08_end.txt" in x)
        self.assertEqual(row.split(chr(9))[:11], ["act33side","level_act33side_08_end.txt","partial_first_draft","102","2","20","24","12","160","502baa017ba32f5d3359d2caeedd2adafc72cd2a","f5b13d3e11d4be6c3d4412eff082ae606fe586b4"])
        self.assertEqual(self.manifest["version"], "v3.23")
        self.assertEqual(self.manifest["next_text_ordinal"], 161)
        self.assertEqual(self.manifest["next_text_source_line"], 592)
        self.assertEqual(self.manifest["translation_integrity"]["babel_ru_text_entries_including_partial"], 3929)
        self.assertIn("v3.23", self.readme)
        self.assertIn("events/BABEL_INDEX_v323.tsv", self.readme)
        self.assertIn("Oracle / 预言家 — Оракул", self.terms)
        self.assertIn("文明的存续", self.terms)

if __name__ == "__main__":
    unittest.main()
