# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

TRANSLATION = load("story/story_chapter_6_stage_6-6_interlude_ru_v189.json")
AUDIT = load("reports/MAIN_6-6_INTERLUDE_SOURCE_AUDIT_v189.json")
QA = load("reports/QA_MAIN_STORY_v189.json")
MANIFEST = load("chronology/CHRONOLOGY_MANIFEST_v349.json")
SELECTION = load("story/story_main_selection_ru_v189.json")
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v189.tsv").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

EXPECTED_FINAL_SOURCE_LINES = [198,199,200,204,208,209,210,211,212,213,214,221,223,224,226,228,229,230,231,232,234,236,238,240,241,247,252,254,256,258,260,262,263,265,267,269,271,275,281,283,285,287,288,290,292,294,296,298,300,302,303,308,309]

class TestMainStory66InterludeV189(unittest.TestCase):
    def test_full_progress_and_continuous_ordinals(self):
        self.assertEqual(TRANSLATION["version"], "v1.89")
        self.assertIn("COMPLETE_FIRST_DRAFT", TRANSLATION["status"])
        p, rows = TRANSLATION["progress"], TRANSLATION["dialogues"]
        self.assertEqual((p["translated"], p["total"], p["remaining"], p["complete"]), (203, 203, 0, True))
        self.assertEqual((p["named_translated"], p["named_total"]), (174, 174))
        self.assertEqual((p["unnamed_translated"], p["unnamed_total"]), (29, 29))
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 204)))
        self.assertEqual([x["source_line"] for x in rows[-53:]], EXPECTED_FINAL_SOURCE_LINES)
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 174)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 29)
        self.assertIsNone(p["next_ordinal"])
        self.assertIsNone(p["next_source_line"])

    def test_translation_payload_and_names(self):
        rows = TRANSLATION["dialogues"]
        payload = "\n".join(x["text_ru"] for x in rows)
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", payload))
        self.assertTrue(all(x["text_ru"].strip() for x in rows))
        self.assertEqual(rows[150]["text_ru"], "Кто я? Это неважно.")
        self.assertEqual(rows[153]["speaker_cn"], "塔露拉")
        self.assertEqual(rows[156]["text_ru"], "Талула верила в меня. Елена, Булдроккас'ти, Людмила — все они верили в меня.")
        self.assertEqual(rows[182]["text_ru"], "Помоги ему. Мефисто нуждается в твоей помощи. Ему нужно, чтобы ты помог ему почувствовать свою значимость. Он доверяет только тебе и мне.")
        self.assertEqual(rows[-1]["text_ru"], "Мой идеал — ……")
        self.assertEqual(TRANSLATION["decision_options_ru"], [])
        self.assertIn("Eno / 伊诺 — Эно", TERMS)
        self.assertIn("Sasha / 萨沙 — Саша", TERMS)
        self.assertIn("Mephisto / 梅菲斯特 — Мефисто", TERMS)
        self.assertIn("Faust / 浮士德 — Фауст", TERMS)
        self.assertIn("Talulah / 塔露拉 — Талула", TERMS)

    def test_source_hashes_and_structure(self):
        s, a = TRANSLATION["source"], TRANSLATION["source_alignment"]
        self.assertEqual(s["cn_git_blob_sha1"], "026bf7f38a9e0794661a54635a137df90ff4fba0")
        self.assertEqual(s["en_git_blob_sha1"], "9eefd6f8b7e7a7956d7a5e4d9464004cd6ad9676")
        self.assertEqual((a["cn_text_positions"], a["en_text_positions"]), (203, 203))
        self.assertEqual((a["cn_named_positions"], a["en_named_positions"]), (174, 174))
        self.assertEqual((a["cn_unnamed_positions"], a["en_unnamed_positions"]), (29, 29))
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (109, 109))
        self.assertTrue(a["named_text_line_numbers_match"])
        self.assertTrue(a["unnamed_text_line_numbers_match"])
        self.assertTrue(a["speaker_label_positions_match"])
        self.assertTrue(a["command_line_numbers_match"])
        self.assertEqual(a["translated_range"]["ordinal_end"], 203)
        self.assertEqual(a["translated_range"]["command_lines_in_range"], 109)
        self.assertEqual(a["untranslated_positions"], 0)
        self.assertEqual(AUDIT["alignment"]["untranslated_positions"], 0)
        chunks = AUDIT["alignment"]["translated_chunks"]
        self.assertEqual([(x["ordinal_start"], x["ordinal_end"]) for x in chunks], [(1, 100), (101, 150), (151, 203)])

    def test_index_selection_manifest_and_next_scene(self):
        rows = [x for x in INDEX.splitlines() if x.startswith("level_st_06-01.txt")]
        self.assertEqual(len(rows), 1)
        self.assertIn("first_draft_complete\t174\t29\t203", rows[0])
        self.assertEqual(MANIFEST["version"], "v3.49")
        self.assertEqual(MANIFEST["next_file"], "obt/main/level_st_06-02.txt")
        self.assertEqual((MANIFEST["next_text_ordinal"], MANIFEST["next_text_source_line"]), (1, 6))
        self.assertEqual(MANIFEST["next_source"]["text_positions"], 269)
        self.assertEqual(MANIFEST["next_source"]["cn_git_blob_sha1"], "ffa8947a78abc196f2ebfcb90ae2283ee136c953")
        self.assertEqual(MANIFEST["next_source"]["en_git_blob_sha1"], "79204a97fedbc6e1950440f86a618c8d6efa37ba")
        t = MANIFEST["translation_integrity"]
        self.assertEqual((t["main_story_files"], t["main_story_partial_files"], t["main_story_partial_text_entries"]), (121, 0, 0))
        self.assertEqual((t["main_story_selection_files"], t["main_story_selection_text_entries"], t["main_story_selection_vs_historical_manifest_delta"]), (121, 9313, 1))
        self.assertEqual((t["main_story_chapter_6_files"], t["main_story_chapter_6_partial_files"], t["main_story_chapter_6_complete_text_entries"]), (24, 0, 3069))
        self.assertEqual(SELECTION["summary"]["complete_files"], 121)
        self.assertEqual(SELECTION["summary"]["total_dialogue_entries"], 9313)
        self.assertEqual(SELECTION["files"]["obt/main/level_st_06-01.txt"]["dialogue_count"], 203)
        self.assertEqual((QA["completed_story_files"], QA["completed_story_text_entries"], QA["partial_scene_files"]), (121, 9314, 0))
        self.assertEqual(QA["next_scene"]["source_file"], "obt/main/level_st_06-02.txt")
        self.assertFalse(QA["editorial_review"])
        self.assertFalse(QA["in_game_test"])
        self.assertIn("203/203", README)
        self.assertIn("No Light Without Fire", README)

if __name__ == "__main__":
    unittest.main()
