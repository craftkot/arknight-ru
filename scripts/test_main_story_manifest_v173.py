# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV173(unittest.TestCase):
    def test_complete_translation_and_source_identity(self):
        t = load("story/story_chapter_6_stage_6-10_before_ru_v173.json")
        self.assertEqual(t["version"], "v1.73")
        self.assertTrue(t["progress"]["complete"])
        self.assertEqual((t["progress"]["translated"], t["progress"]["total"], t["progress"]["remaining"]), (104, 104, 0))
        self.assertEqual([x["ordinal"] for x in t["dialogues"]], list(range(1, 105)))
        self.assertEqual(len(t["dialogues"]), 104)
        self.assertEqual(sum(x["kind"] == "named" for x in t["dialogues"]), 99)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in t["dialogues"]), 5)
        self.assertEqual([x["source_line"] for x in t["dialogues"]], sorted(x["source_line"] for x in t["dialogues"]))
        self.assertTrue(all(x["text_ru"].strip() for x in t["dialogues"]))
        self.assertFalse(any(re.search(r"[\u4e00-\u9fff]", x["text_ru"]) for x in t["dialogues"]))
        self.assertEqual((t["source"]["cn_git_blob_sha1"], t["source"]["en_git_blob_sha1"]),
                         ("8a5d4c711491343324dc29b668e30d972724bba5", "448f0d022a8c992d15badbf3e2c2e85a5d70c83e"))
        self.assertEqual(t["header_title_ru"], "Этап 4 (до боя)")
        self.assertEqual(sum(len(re.findall(r"\{@[^}]+\}", x["text_ru"])) for x in t["dialogues"]), 1)
        self.assertIn("{@nickname}", t["dialogues"][79]["text_ru"])

    def test_decisions_and_predicates(self):
        t = load("story/story_chapter_6_stage_6-10_before_ru_v173.json")
        d = t["decision_options_ru"]
        self.assertEqual([x["source_line"] for x in d], [155, 162, 184, 191])
        self.assertEqual([len(x["values"]) for x in d], [3, 3, 3, 1])
        self.assertEqual([len(x["options_ru"]) for x in d], [3, 3, 3, 1])
        self.assertEqual(sum(len(x["options_ru"]) for x in d), 10)
        self.assertEqual(d[2]["options_ru"][2], "А, так она не умеет подбирать слова?")

    def test_full_source_audit(self):
        a = load("reports/MAIN_6-10_BEFORE_SOURCE_AUDIT_v173.json")
        self.assertEqual(a["source"]["cn_physical_lines"], 203)
        self.assertEqual(a["source"]["en_physical_lines"], 204)
        self.assertEqual(a["alignment"]["cn_text_positions"], 104)
        self.assertEqual(a["alignment"]["en_text_positions"], 104)
        self.assertEqual((a["alignment"]["named_positions"], a["alignment"]["unnamed_positions"]), (99, 5))
        self.assertEqual(a["alignment"]["command_lines_cn"], 99)
        self.assertEqual(a["alignment"]["command_lines_en"], 99)
        self.assertTrue(a["alignment"]["command_names_and_parameters_match"])
        self.assertTrue(a["alignment"]["command_line_numbers_match"])
        self.assertEqual(a["alignment"]["decision_commands_cn"], 4)
        self.assertEqual(a["alignment"]["decision_option_total_ru"], 10)
        self.assertEqual(a["alignment"]["predicate_commands_cn"], 7)
        self.assertEqual((a["alignment"]["placeholder_count_cn"], a["alignment"]["placeholder_count_en"], a["alignment"]["placeholder_count_ru"]), (1, 1, 1))
        self.assertEqual(a["header_title"]["translation_ru"], "Этап 4 (до боя)")
        self.assertFalse(a["editorial_review"])
        self.assertFalse(a["in_game_test"])

    def test_selection_index_and_qa(self):
        s = load("story/story_main_selection_ru_v173.json")
        self.assertEqual(s["version"], "v1.73")
        self.assertEqual(len(s["files"]), 114)
        self.assertEqual(sum(x["dialogue_count"] for x in s["files"].values()), 8010)
        key = "obt/main/level_main_06-10_beg.txt"
        self.assertEqual(s["files"][key]["dialogue_count"], 104)
        self.assertEqual(len(s["files"][key]["dialogues"]), 104)
        idx = (ROOT / "story/CHAPTER_6_INDEX_v173.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-10_beg.txt\tfirst_draft_complete\t99\t5\t104", idx)
        q = load("reports/QA_MAIN_STORY_v173.json")
        self.assertEqual((q["completed_story_files"], q["completed_story_text_entries"]), (114, 8011))
        self.assertEqual((q["partial_scene_files"], q["partial_scene_text_entries"]), (0, 0))
        self.assertEqual((q["chapter_6_complete_files"], q["chapter_6_complete_text_entries"]), (17, 1766))
        self.assertEqual(q["selection_vs_historical_manifest_delta"], 1)

    def test_chronology_and_readme(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v333.json")
        self.assertEqual(m["version"], "v3.33")
        self.assertEqual(m["translation_integrity"]["main_story_files"], 114)
        self.assertEqual(m["translation_integrity"]["main_story_partial_files"], 0)
        self.assertEqual(m["next_file"], "obt/main/level_main_06-10_end.txt")
        self.assertEqual(m["next_text_ordinal"], 1)
        self.assertEqual(m["next_text_source_line"], 13)
        self.assertEqual(m["next_source"]["text_positions"], 205)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v3.34", readme)  # latest README after the v1.74 scene update
        self.assertIn("6-10 до боя завершена", readme)
        self.assertIn("6-10 после боя", readme)
        self.assertIn("Историческая отметка v3.32", readme)

if __name__ == "__main__":
    unittest.main()
