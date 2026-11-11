import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = "obt/main/level_main_06-13_end.txt"
TRANSLATION = json.loads((ROOT / "story/story_chapter_6_stage_6-13_after_ru_v180.json").read_text(encoding="utf-8"))
AUDIT = json.loads((ROOT / "reports/MAIN_6-13_AFTER_SOURCE_AUDIT_v180.json").read_text(encoding="utf-8"))
QA = json.loads((ROOT / "reports/QA_MAIN_STORY_v180.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "chronology/CHRONOLOGY_MANIFEST_v340.json").read_text(encoding="utf-8"))
SELECTION = json.loads((ROOT / "story/story_main_selection_ru_v180.json").read_text(encoding="utf-8"))
INDEX = (ROOT / "story/CHAPTER_6_INDEX_v180.tsv").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")


class TestMainStory613AfterV180(unittest.TestCase):
    def test_complete_first_draft_and_ordinals(self):
        rows = TRANSLATION["dialogues"]
        self.assertEqual(TRANSLATION["progress"]["translated"], 182)
        self.assertEqual(TRANSLATION["progress"]["total"], 182)
        self.assertEqual(TRANSLATION["progress"]["remaining"], 0)
        self.assertTrue(TRANSLATION["progress"]["complete"])
        self.assertEqual(len(rows), 182)
        self.assertEqual([x["ordinal"] for x in rows], list(range(1, 183)))
        self.assertEqual(sum(x["kind"] == "named" for x in rows), 177)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in rows), 5)
        self.assertEqual([x["source_line"] for x in rows], AUDIT["alignment"]["translated_source_lines"])

    def test_source_hashes_and_line_alignment(self):
        source = TRANSLATION["source"]
        alignment = AUDIT["alignment"]
        self.assertEqual(source["cn_git_blob_sha1"], "df3b196895c307d550ee2d501c2ae79b27dc84e3")
        self.assertEqual(source["en_git_blob_sha1"], "866908f1fcd804e41259bb399b4e8087d3cf8239")
        self.assertEqual((alignment["cn_physical_lines"], alignment["en_physical_lines"]), (365, 366))
        self.assertEqual((alignment["cn_named_positions"], alignment["en_named_positions"]), (177, 177))
        self.assertEqual((alignment["cn_unnamed_positions"], alignment["en_unnamed_positions"]), (5, 5))
        self.assertTrue(alignment["named_text_line_numbers_match"])
        self.assertTrue(alignment["unnamed_text_line_numbers_match"])
        self.assertTrue(alignment["speaker_label_positions_match"])

    def test_command_and_decision_integrity(self):
        a = AUDIT["alignment"]
        self.assertEqual((a["command_lines_cn"], a["command_lines_en"]), (183, 183))
        self.assertTrue(a["command_line_numbers_match"])
        self.assertTrue(a["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertEqual(a["command_counts"], {
            "HEADER": 1, "Background": 2, "PlayMusic": 2, "Delay": 4,
            "Character": 130, "PlaySound": 2, "Dialog": 11, "Blocker": 15,
            "stopmusic": 2, "Decision": 7, "Predicate": 7
        })
        decisions = TRANSLATION["decision_options_ru"]
        self.assertEqual(len(decisions), 7)
        self.assertEqual(sum(len(x["options_ru"]) for x in decisions), 9)
        self.assertEqual([x["source_line"] for x in decisions], [201, 205, 211, 228, 277, 303, 356])
        self.assertTrue(a["decision_values_and_predicate_references_match"])
        self.assertEqual(a["predicate_branches"], 7)

    def test_unnamed_captions_and_header(self):
        rows = [x for x in TRANSLATION["dialogues"] if x["kind"] == "unnamed"]
        self.assertEqual([x["source_line"] for x in rows], [133, 134, 135, 136, 350])
        self.assertEqual([x["text_ru"] for x in rows], [
            "15:22", "Руины района «14» в городе-спутнике Чернобога",
            "Поверхность сектора", "Спустя три часа после начала раскопок",
            "Подземные уровни Лунмэня"
        ])
        self.assertEqual(TRANSLATION["header_title_ru"], "Этап 1 (после боя)")

    def test_payload_integrity_and_cn_priority(self):
        text = "\n".join(x["text_ru"] for x in TRANSLATION["dialogues"])
        text += "\n" + "\n".join(y for d in TRANSLATION["decision_options_ru"] for y in d["options_ru"])
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", text))
        self.assertFalse(any(not x["text_ru"].strip() for x in TRANSLATION["dialogues"]))
        self.assertEqual(text.count("{@nickname}"), 0)
        self.assertEqual(AUDIT["alignment"]["untranslated_cjk_in_ru"], 0)
        self.assertEqual(AUDIT["alignment"]["empty_ru_entries"], 0)
        self.assertEqual(AUDIT["alignment"]["placeholder_count_ru"], 0)
        line204 = next(x["text_ru"] for x in TRANSLATION["dialogues"] if x["source_line"] == 204)
        self.assertEqual(line204, "Неужели я проиграю?")
        self.assertIn("Если они найдут их первыми… Если они найдут их первыми!", text)
        self.assertIn("через что им пришлось пройти", text)

    def test_selection_and_chapter_index(self):
        item = SELECTION["files"][SCENE]
        self.assertEqual(item["dialogue_count"], 182)
        self.assertEqual(item["named_dialogue_count"], 177)
        self.assertEqual(item["unnamed_dialogue_count"], 5)
        self.assertEqual(len(item["dialogues"]), 182)
        self.assertEqual(len(item["decisions"]), 7)
        self.assertEqual(sum(len(x) for x in item["decisions"].values()), 9)
        self.assertEqual(SELECTION["summary"]["complete_files"], 119)
        self.assertEqual(SELECTION["summary"]["total_dialogue_entries"], 8781)
        self.assertEqual(SELECTION["summary"]["historical_manifest_entries"], 8782)
        self.assertEqual(SELECTION["summary"]["inherited_delta"], 1)
        rows = [x for x in INDEX.splitlines() if x.startswith("level_main_06-13_end.txt\t")]
        self.assertEqual(len(rows), 1)
        self.assertIn("first_draft_complete\t177\t5\t182", rows[0])

    def test_manifest_and_qa_totals(self):
        t = MANIFEST["translation_integrity"]
        self.assertEqual(MANIFEST["version"], "v3.40")
        self.assertEqual(MANIFEST["next_file"], "obt/main/level_main_06-14_beg.txt")
        self.assertEqual((t["main_story_files"], t["main_story_named_ru_lines"]), (119, 8671))
        self.assertEqual((t["main_story_unnamed_ru_lines"], t["main_story_selection_files"]), (111, 119))
        self.assertEqual(t["main_story_selection_text_entries"], 8781)
        self.assertEqual((t["main_story_chapter_6_files"], t["main_story_chapter_6_complete_text_entries"]), (22, 2537))
        self.assertEqual(MANIFEST["next_source"]["text_positions"], 329)
        self.assertEqual(MANIFEST["next_source"]["named_positions"], 327)
        self.assertEqual(MANIFEST["next_source"]["unnamed_positions"], 2)
        self.assertEqual(QA["completed_story_files"], 119)
        self.assertEqual(QA["completed_story_named_ru"], 8671)
        self.assertEqual(QA["completed_story_unnamed_ru"], 111)
        self.assertEqual(QA["completed_story_text_entries"], 8782)
        self.assertEqual(QA["chapter_6_complete_files"], 22)
        self.assertEqual(QA["chapter_6_complete_text_entries"], 2537)
        self.assertEqual(QA["partial_scene_files"], 0)
        self.assertEqual(QA["next_scene"]["source_file"], "obt/main/level_main_06-14_beg.txt")
        self.assertEqual(QA["next_scene"]["remaining"], 329)

    def test_readme_and_glossary(self):
        self.assertIn("v3.40", README)
        self.assertIn("6-13 после боя", README)
        self.assertIn("182/182", README)
        self.assertIn("level_main_06-14_beg.txt", README)
        self.assertIn("Nesti / 大熊 — Нести", TERMS)
        self.assertIn("FrostNova / 霜星 — ФростНова", TERMS)
        self.assertIn("Yeti Squadron / 雪怪小队 — Отряд йети", TERMS)


if __name__ == "__main__":
    unittest.main()
