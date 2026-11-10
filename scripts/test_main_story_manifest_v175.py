# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV175(unittest.TestCase):
    def test_partial_translation_and_source_identity(self):
        t = load("story/story_chapter_6_stage_6-11_before_partial_ru_v175.json")
        self.assertEqual(t["version"], "v1.75")
        self.assertFalse(t["progress"]["complete"])
        self.assertEqual((t["progress"]["translated"], t["progress"]["total"], t["progress"]["remaining"]), (60, 180, 120))
        self.assertEqual(t["progress"]["next_ordinal"], 61)
        self.assertEqual(t["progress"]["next_source_line"], 125)
        self.assertEqual([x["ordinal"] for x in t["dialogues"]], list(range(1, 61)))
        self.assertEqual([x["source_line"] for x in t["dialogues"]], [9,11,13,15,16,17,18,20,21,23,25,27,29,30,32,34,36,43,45,47,49,51,52,54,56,63,65,67,68,70,71,73,74,75,76,78,79,81,82,84,86,87,89,91,93,95,97,99,101,102,104,105,106,108,109,111,112,114,116,118])
        self.assertTrue(all(x["kind"] == "named" for x in t["dialogues"]))
        self.assertTrue(all(x["text_ru"].strip() for x in t["dialogues"]))
        self.assertFalse(any(re.search(r"[\u4e00-\u9fff]", x["text_ru"]) for x in t["dialogues"]))
        self.assertEqual((t["source"]["cn_git_blob_sha1"], t["source"]["en_git_blob_sha1"]), ("0986ac67e9b36541dc93f82e53dd687780015d60", "92b2237c92178fb888e2c6928c6bae6b2a45a0e8"))
        self.assertEqual(t["header_title_ru"], "Этап 2 (после боя)")
        self.assertEqual(t["decision_options_ru"], [])
        self.assertEqual(t["dialogues"][4]["text_ru"], "Там будут и урсусцы, и жители Лунмэня. И заражённые, и обычные люди. Какими бы бедными или богатыми они ни были, уходят все с пустыми руками.")
        self.assertEqual(t["dialogues"][9]["text_ru"], "(Наверное, перенял это у Бати.)")
        self.assertEqual(t["dialogues"][40]["text_ru"], "Раз уж мы сражаемся, рано или поздно кто-нибудь погибнет в бою. Мы не против пасть здесь.")
        self.assertEqual(t["dialogues"][-1]["text_ru"], "Надеюсь, этот день наступит нескоро.")

    def test_full_source_alignment_and_partial_range_audit(self):
        a = load("reports/CHAPTER_6_STAGE_6-11_BEFORE_SOURCE_AUDIT_v175.json")
        self.assertEqual((a["source"]["cn_physical_lines"], a["source"]["en_physical_lines"]), (367, 368))
        self.assertEqual((a["alignment"]["cn_text_positions"], a["alignment"]["en_text_positions"]), (180, 180))
        self.assertTrue(a["alignment"]["text_line_numbers_match"])
        self.assertEqual((a["alignment"]["command_lines_cn"], a["alignment"]["command_lines_en"]), (187, 187))
        self.assertTrue(a["alignment"]["command_line_numbers_match"])
        self.assertTrue(a["alignment"]["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertEqual((a["alignment"]["decision_commands"], a["alignment"]["predicate_branches"]), (3, 3))
        r = a["alignment"]["translated_range"]
        self.assertEqual((r["first_ordinal"], r["last_ordinal"], r["translated_positions"], r["remaining_positions"]), (1, 60, 60, 120))
        self.assertEqual((r["source_line_start"], r["source_line_end"], r["command_lines_cn"]), (9, 118, 58))
        self.assertEqual(r["decision_commands"], 0)
        self.assertIn("_beg", a["header_title"]["note"])
        self.assertFalse(a["editorial_review"])
        self.assertFalse(a["in_game_test"])

    def test_chapter_index_and_unchanged_selection(self):
        idx = (ROOT / "story/CHAPTER_6_INDEX_v175.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-11_beg.txt\tpartial_first_draft\t60\t0\t60\t0986ac67e9b36541dc93f82e53dd687780015d60\t92b2237c92178fb888e2c6928c6bae6b2a45a0e8", idx)
        self.assertEqual(sum(1 for line in idx.splitlines() if line.strip()) - 1, 19)
        s = load("story/story_main_selection_ru_v174.json")
        self.assertEqual((s["version"], len(s["files"])), ("v1.74", 115))
        self.assertEqual(sum(x["dialogue_count"] for x in s["files"].values()), 8215)

    def test_qa_and_chronology_counts(self):
        q = load("reports/QA_MAIN_STORY_v175.json")
        self.assertEqual((q["completed_story_files"], q["completed_story_text_entries"]), (115, 8216))
        self.assertEqual((q["partial_scene_files"], q["partial_scene_named_ru"], q["partial_scene_text_entries"]), (1, 60, 60))
        self.assertEqual(q["all_story_text_entries_including_partial"], 8276)
        self.assertEqual((q["chapter_6_complete_files"], q["chapter_6_partial_files"], q["chapter_6_partial_text_entries"]), (18, 1, 60))
        self.assertEqual(q["chapter_6_text_entries_including_partial"], 2031)
        self.assertEqual(q["next_scene"]["next_ordinal"], 61)
        m = load("chronology/CHRONOLOGY_MANIFEST_v335.json")
        self.assertEqual(m["version"], "v3.35")
        self.assertEqual(m["translation_integrity"]["main_story_partial_files"], 1)
        self.assertEqual(m["translation_integrity"]["main_story_partial_named_ru_lines"], 60)
        self.assertEqual(m["translation_integrity"]["main_story_text_entries_including_partial"], 8276)
        self.assertEqual(m["next_file"], "obt/main/level_main_06-11_beg.txt")
        self.assertEqual((m["next_text_ordinal"], m["next_text_source_line"]), (61, 125))

    def test_readme_and_glossary(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v3.35", readme)
        self.assertIn("60/180", readme)
        self.assertIn("Следующая позиция — №61", readme)
        glossary = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertIn("Big Daddy / 大爹 — Батя", glossary)

if __name__ == "__main__":
    unittest.main()
