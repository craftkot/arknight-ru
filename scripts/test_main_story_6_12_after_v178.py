import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = "obt/main/level_main_06-12_end.txt"
TRANSLATION = json.loads((ROOT / "story/story_chapter_6_stage_6-12_after_ru_v178.json").read_text(encoding="utf-8"))
AUDIT = json.loads((ROOT / "reports/MAIN_6-12_AFTER_SOURCE_AUDIT_v178.json").read_text(encoding="utf-8"))
QA = json.loads((ROOT / "reports/QA_MAIN_STORY_v178.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "chronology/CHRONOLOGY_MANIFEST_v338.json").read_text(encoding="utf-8"))
SELECTION = json.loads((ROOT / "story/story_main_selection_ru_v178.json").read_text(encoding="utf-8"))
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v178.tsv").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")

class TestMainStory612AfterV178(unittest.TestCase):
    def test_complete_first_draft(self):
        self.assertEqual(TRANSLATION["progress"]["translated"], 163)
        self.assertEqual(TRANSLATION["progress"]["total"], 163)
        self.assertEqual(TRANSLATION["progress"]["remaining"], 0)
        self.assertTrue(TRANSLATION["progress"]["complete"])
        self.assertEqual(len(TRANSLATION["dialogues"]), 163)

    def test_ordinals_and_source_lines(self):
        rows = TRANSLATION["dialogues"]
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 164)))
        lines = [x["source_line"] for x in rows]
        self.assertEqual(lines, sorted(set(lines)))
        self.assertEqual(lines[0], 6)
        self.assertEqual(lines[-1], 312)
        self.assertTrue(all(x["kind"] == "named" for x in rows))

    def test_cn_en_source_alignment(self):
        self.assertEqual(AUDIT["cn_git_blob_sha1"], TRANSLATION["source"]["cn_git_blob_sha1"])
        self.assertEqual(AUDIT["en_git_blob_sha1"], TRANSLATION["source"]["en_git_blob_sha1"])
        self.assertEqual(AUDIT["cn_text_positions"], 163)
        self.assertEqual(AUDIT["en_text_positions"], 163)
        self.assertEqual(AUDIT["command_lines_cn"], 153)
        self.assertEqual(AUDIT["command_lines_en"], 153)
        self.assertTrue(AUDIT["commands_match_cn_en"])
        self.assertTrue(AUDIT["text_line_numbers_match"])
        self.assertTrue(AUDIT["speaker_label_positions_match"])

    def test_decision_and_predicate_integrity(self):
        decisions = TRANSLATION["decision_options_ru"]
        self.assertEqual(len(decisions), 6)
        self.assertEqual(sum(len(x["options_ru"]) for x in decisions), 12)
        self.assertEqual([x["source_line"] for x in decisions], [181, 189, 194, 199, 204, 213])
        self.assertEqual(AUDIT["predicate_branches"], 6)
        self.assertTrue(AUDIT["decision_values_and_predicate_references_match"])

    def test_placeholders_and_no_untranslated_cjk(self):
        text = "\\n".join(x["text_ru"] for x in TRANSLATION["dialogues"])
        text += "\\n" + "\\n".join(y for d in TRANSLATION["decision_options_ru"] for y in d["options_ru"])
        self.assertEqual(text.count("{@nickname}"), 2)
        self.assertIsNone(re.search(r"[\\u3400-\\u9fff]", text))
        self.assertFalse(any(not x["text_ru"].strip() for x in TRANSLATION["dialogues"]))

    def test_selection_contains_scene_and_counts(self):
        item = SELECTION["files"][SCENE]
        self.assertEqual(item["dialogue_count"], 163)
        self.assertEqual(item["named_dialogue_count"], 163)
        self.assertEqual(item["unnamed_dialogue_count"], 0)
        self.assertEqual(len(item["dialogues"]), 163)
        self.assertEqual(sum(len(x) for x in item["decisions"].values()), 12)
        self.assertEqual(SELECTION["summary"]["complete_files"], 117)
        self.assertEqual(SELECTION["summary"]["total_dialogue_entries"], 8558)

    def test_chapter_index_and_chronology(self):
        rows = [line for line in INDEX.splitlines() if line.startswith("level_main_06-12_end.txt\\t")]
        self.assertEqual(len(rows), 1)
        self.assertIn("first_draft_complete\\t163\\t0\\t163", rows[0])
        self.assertEqual(MANIFEST["version"], "v3.38")
        self.assertEqual(MANIFEST["next_file"], "obt/main/level_main_06-13_beg.txt")
        self.assertEqual(MANIFEST["translation_integrity"]["main_story_files"], 117)
        self.assertEqual(MANIFEST["translation_integrity"]["main_story_selection_text_entries"], 8558)

    def test_qa_totals_and_next_scene(self):
        self.assertEqual(QA["completed_story_files"], 117)
        self.assertEqual(QA["completed_story_text_entries"], 8559)
        self.assertEqual(QA["chapter_6_complete_files"], 20)
        self.assertEqual(QA["chapter_6_complete_text_entries"], 2314)
        self.assertEqual(QA["next_scene"]["source_file"], "obt/main/level_main_06-13_beg.txt")
        self.assertEqual(QA["next_scene"]["total"], 41)
        self.assertEqual(QA["next_scene"]["remaining"], 41)

    def test_glossary_additions(self):
        for term in ("Найн", "Тайхэ", "Цензор", "чёрные дождевики", "Императорская гвардия"):
            self.assertIn(term, TERMS)

if __name__ == "__main__":
    unittest.main()
