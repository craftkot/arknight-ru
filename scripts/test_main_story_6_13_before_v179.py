import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = "obt/main/level_main_06-13_beg.txt"
TRANSLATION = json.loads((ROOT / "story/story_chapter_6_stage_6-13_before_ru_v179.json").read_text(encoding="utf-8"))
AUDIT = json.loads((ROOT / "reports/MAIN_6-13_BEFORE_SOURCE_AUDIT_v179.json").read_text(encoding="utf-8"))
QA = json.loads((ROOT / "reports/QA_MAIN_STORY_v179.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "chronology/CHRONOLOGY_MANIFEST_v339.json").read_text(encoding="utf-8"))
SELECTION = json.loads((ROOT / "story/story_main_selection_ru_v179.json").read_text(encoding="utf-8"))
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v179.tsv").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

class TestMainStory613BeforeV179(unittest.TestCase):
    def test_complete_first_draft(self):
        self.assertEqual(TRANSLATION["progress"]["translated"], 41)
        self.assertEqual(TRANSLATION["progress"]["total"], 41)
        self.assertEqual(TRANSLATION["progress"]["remaining"], 0)
        self.assertTrue(TRANSLATION["progress"]["complete"])
        self.assertEqual(len(TRANSLATION["dialogues"]), 41)

    def test_ordinals_and_source_lines(self):
        rows = TRANSLATION["dialogues"]
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 42)))
        self.assertEqual([x["source_line"] for x in rows], AUDIT["translated_source_lines"])
        self.assertEqual(rows[0]["source_line"], 12)
        self.assertEqual(rows[-1]["source_line"], 84)
        self.assertTrue(all(x["kind"] == "named" for x in rows))
        self.assertEqual(len({x["source_line"] for x in rows}), 41)

    def test_cn_en_source_alignment(self):
        self.assertEqual(AUDIT["cn_git_blob_sha1"], TRANSLATION["source"]["cn_git_blob_sha1"])
        self.assertEqual(AUDIT["en_git_blob_sha1"], TRANSLATION["source"]["en_git_blob_sha1"])
        self.assertEqual(AUDIT["cn_text_positions"], 41)
        self.assertEqual(AUDIT["en_text_positions"], 41)
        self.assertTrue(AUDIT["text_line_numbers_match"])
        self.assertTrue(AUDIT["speaker_label_positions_match"])
        self.assertEqual(AUDIT["command_lines_cn"], 44)
        self.assertEqual(AUDIT["command_lines_en"], 44)
        self.assertTrue(AUDIT["commands_match_cn_en"])
        self.assertTrue(AUDIT["command_line_numbers_match"])

    def test_command_inventory(self):
        self.assertEqual(AUDIT["command_counts"], {
            "HEADER": 1, "Dialog": 2, "Character": 32, "Background": 1,
            "PlayMusic": 1, "Delay": 2, "playsound": 3, "Blocker": 2
        })
        self.assertEqual(AUDIT["decision_commands"], 0)
        self.assertEqual(AUDIT["predicate_branches"], 0)

    def test_payload_integrity(self):
        text = "\n".join(x["text_ru"] for x in TRANSLATION["dialogues"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", text))
        self.assertFalse(any(not x["text_ru"].strip() for x in TRANSLATION["dialogues"]))
        self.assertEqual(text.count("{@nickname}"), 0)
        self.assertEqual(AUDIT["untranslated_cjk_in_ru"], 0)
        self.assertEqual(AUDIT["empty_ru_entries"], 0)
        self.assertEqual(AUDIT["placeholder_count_ru"], 0)

    def test_header_and_glossary(self):
        self.assertEqual(TRANSLATION["header_title_ru"], "Этап 1 (до боя)")
        self.assertIn("Reunion Caster / 整合运动术师 — маг Воссоединения", TERMS)
        self.assertIn("Yeti Squadron / 雪怪小队 — Отряд йети", TERMS)
        self.assertIn("FrostNova / 霜星 — ФростНова", TERMS)

    def test_selection_and_index(self):
        item = SELECTION["files"][SCENE]
        self.assertEqual(item["dialogue_count"], 41)
        self.assertEqual(item["named_dialogue_count"], 41)
        self.assertEqual(item["unnamed_dialogue_count"], 0)
        self.assertEqual(len(item["dialogues"]), 41)
        self.assertEqual(SELECTION["summary"]["complete_files"], 118)
        self.assertEqual(SELECTION["summary"]["total_dialogue_entries"], 8599)
        rows = [x for x in INDEX.splitlines() if x.startswith("level_main_06-13_beg.txt\t")]
        self.assertEqual(len(rows), 1)
        self.assertIn("first_draft_complete\t41\t0\t41", rows[0])

    def test_manifest_and_next_scene(self):
        self.assertEqual(MANIFEST["version"], "v3.39")
        self.assertEqual(MANIFEST["next_file"], "obt/main/level_main_06-13_end.txt")
        self.assertEqual(MANIFEST["translation_integrity"]["main_story_files"], 118)
        self.assertEqual(MANIFEST["translation_integrity"]["main_story_named_ru_lines"], 8494)
        self.assertEqual(MANIFEST["translation_integrity"]["main_story_chapter_6_files"], 21)
        self.assertEqual(MANIFEST["translation_integrity"]["main_story_chapter_6_complete_text_entries"], 2355)
        self.assertEqual(MANIFEST["next_source"]["text_positions"], 177)
        self.assertEqual(MANIFEST["next_source"]["command_lines"], 183)

    def test_qa_totals_and_no_partial_scenes(self):
        self.assertEqual(QA["completed_story_files"], 118)
        self.assertEqual(QA["completed_story_named_ru"], 8494)
        self.assertEqual(QA["completed_story_text_entries"], 8600)
        self.assertEqual(QA["chapter_6_complete_files"], 21)
        self.assertEqual(QA["chapter_6_complete_text_entries"], 2355)
        self.assertEqual(QA["partial_scene_files"], 0)
        self.assertEqual(QA["next_scene"]["source_file"], "obt/main/level_main_06-13_end.txt")
        self.assertEqual(QA["next_scene"]["remaining"], 177)

    def test_readme_status(self):
        self.assertIn("v3.40", README)
        self.assertIn("level_main_06-13_beg.txt", README)
        self.assertIn("level_main_06-13_end.txt", README)
        self.assertIn("level_main_06-14_beg.txt", README)
        self.assertIn("182/182", README)
        self.assertIn("level_main_06-14_beg.txt", README)
        self.assertIn("182/182", README)
        self.assertIn("Это полный первый черновик", README)

if __name__ == "__main__":
    unittest.main()
