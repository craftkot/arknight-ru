# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV174(unittest.TestCase):
    def test_complete_translation_and_source_identity(self):
        t = load("story/story_chapter_6_stage_6-10_after_ru_v174.json")
        self.assertEqual(t["version"], "v1.74")
        self.assertTrue(t["progress"]["complete"])
        self.assertEqual((t["progress"]["translated"], t["progress"]["total"], t["progress"]["remaining"]), (205, 205, 0))
        self.assertEqual([x["ordinal"] for x in t["dialogues"]], list(range(1, 206)))
        self.assertEqual(len(t["dialogues"]), 205)
        self.assertTrue(all(x["kind"] == "named" for x in t["dialogues"]))
        self.assertEqual([x["source_line"] for x in t["dialogues"]], sorted(x["source_line"] for x in t["dialogues"]))
        self.assertEqual((t["dialogues"][0]["source_line"], t["dialogues"][-1]["source_line"]), (13, 353))
        self.assertTrue(all(x["text_ru"].strip() for x in t["dialogues"]))
        self.assertFalse(any(re.search(r"[\u4e00-\u9fff]", x["text_ru"]) for x in t["dialogues"]))
        self.assertEqual((t["source"]["cn_git_blob_sha1"], t["source"]["en_git_blob_sha1"]),
                         ("bb62801e39e1b96789067cd5ed25aa567e06896f", "e9f0401e0c5a790c4ea0b37f3cf7a970eb4a879d"))
        self.assertEqual(t["header_title_ru"], "Этап 4 (после боя)")
        self.assertTrue(all(t["dialogues"][i]["text_ru"].startswith("(") and t["dialogues"][i]["text_ru"].endswith(")") for i in range(6)))
        self.assertEqual(t["dialogues"][98]["text_ru"], "К-как? Твой позвоночник?!")
        self.assertEqual(t["dialogues"][120]["text_ru"], "Почему?")
        self.assertEqual(t["dialogues"][48]["text_ru"], "Когда ты убивала Сергея, он раскаялся?")
        self.assertIn("изменить эту землю", t["dialogues"][178]["text_ru"])

    def test_full_source_audit(self):
        a = load("reports/MAIN_6-10_AFTER_SOURCE_AUDIT_v174.json")
        self.assertEqual((a["source"]["cn_physical_lines"], a["source"]["en_physical_lines"]), (357, 358))
        self.assertEqual((a["alignment"]["cn_text_positions"], a["alignment"]["en_text_positions"]), (205, 205))
        self.assertEqual((a["alignment"]["named_positions"], a["alignment"]["unnamed_positions"]), (205, 0))
        self.assertEqual((a["alignment"]["command_lines_cn"], a["alignment"]["command_lines_en"]), (152, 152))
        self.assertTrue(a["alignment"]["text_line_numbers_match"])
        self.assertTrue(a["alignment"]["command_names_and_parameters_match"])
        self.assertTrue(a["alignment"]["command_line_numbers_match"])
        self.assertEqual(a["cn_en_semantic_notes"][-1]["ordinal"], 121)
        self.assertEqual(a["header_title"]["translation_ru"], "Этап 4 (после боя)")
        self.assertFalse(a["editorial_review"])
        self.assertFalse(a["in_game_test"])

    def test_selection_index_and_qa(self):
        s = load("story/story_main_selection_ru_v174.json")
        self.assertEqual(s["version"], "v1.74")
        self.assertEqual(len(s["files"]), 115)
        self.assertEqual(sum(x["dialogue_count"] for x in s["files"].values()), 8215)
        key = "obt/main/level_main_06-10_end.txt"
        self.assertEqual(s["files"][key]["dialogue_count"], 205)
        self.assertEqual(len(s["files"][key]["dialogues"]), 205)
        self.assertEqual(s["files"][key]["dialogues"]["121"], "Почему?")
        self.assertIn("станет штаммом", s["files"][key]["dialogues"]["189"])
        idx = (ROOT / "story/CHAPTER_6_INDEX_v174.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-10_end.txt\tfirst_draft_complete\t205\t0\t205", idx)
        q = load("reports/QA_MAIN_STORY_v174.json")
        self.assertEqual((q["completed_story_files"], q["completed_story_text_entries"]), (115, 8216))
        self.assertEqual((q["selection_files"], q["selection_dialogue_entries_counted"]), (115, 8215))
        self.assertEqual((q["partial_scene_files"], q["partial_scene_text_entries"]), (0, 0))
        self.assertEqual((q["chapter_6_complete_files"], q["chapter_6_complete_text_entries"]), (18, 1971))
        self.assertEqual(q["selection_vs_historical_manifest_delta"], 1)

    def test_chronology_readme_and_glossary(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v334.json")
        self.assertEqual(m["version"], "v3.34")
        self.assertEqual(m["translation_integrity"]["main_story_files"], 115)
        self.assertEqual(m["translation_integrity"]["main_story_partial_files"], 0)
        self.assertEqual(m["next_file"], "obt/main/level_main_06-11_beg.txt")
        self.assertEqual(m["next_text_ordinal"], 1)
        self.assertEqual(m["next_text_source_line"], 9)
        self.assertEqual(m["next_source"]["text_positions"], 180)
        self.assertEqual(m["next_source"]["command_lines"], 187)
        self.assertEqual(m["next_source"]["decision_commands"], 3)
        self.assertTrue(m["next_source"]["localized_decision_option_payloads"])
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v3.34", readme)
        self.assertIn("6-10 после боя", readme)
        self.assertIn("6-11 до боя", readme)
        glossary = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertIn("Crownslayer / 弑君者 — Краунслеер", glossary)
        self.assertIn("Kal'tsit / 凯尔希 — Кальцит", glossary)

if __name__ == "__main__":
    unittest.main()
