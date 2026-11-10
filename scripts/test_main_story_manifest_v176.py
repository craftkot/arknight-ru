# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV176(unittest.TestCase):
    def test_partial_translation_and_decision_options(self):
        t=load("story/story_chapter_6_stage_6-11_before_partial_ru_v176.json")
        self.assertEqual(t["version"],"v1.76")
        self.assertEqual((t["progress"]["translated"],t["progress"]["total"],t["progress"]["remaining"]),(120,180,60))
        self.assertEqual((t["progress"]["next_ordinal"],t["progress"]["next_source_line"]),(121,238))
        self.assertEqual([x["ordinal"] for x in t["dialogues"]],list(range(1,121)))
        self.assertEqual([x["source_line"] for x in t["dialogues"]],[9,11,13,15,16,17,18,20,21,23,25,27,29,30,32,34,36,43,45,47,49,51,52,54,56,63,65,67,68,70,71,73,74,75,76,78,79,81,82,84,86,87,89,91,93,95,97,99,101,102,104,105,106,108,109,111,112,114,116,118,125,126,128,129,130,132,134,136,138,140,142,144,146,148,149,151,153,155,157,159,161,163,164,165,167,169,176,178,180,182,184,185,187,194,195,196,198,200,201,203,204,205,206,207,209,211,213,215,217,218,220,221,222,224,226,228,229,231,234,235])
        self.assertEqual(len(t["decision_options_ru"]),3)
        self.assertEqual([x["source_line"] for x in t["decision_options_ru"]],[236,240,246])
        self.assertEqual([x["values"] for x in t["decision_options_ru"]],[["1"],["1"],["1"]])
        self.assertEqual([x["options_ru"][0] for x in t["decision_options_ru"]],["Не хочешь смотреть?","Но, как тогда, в руинах Чернобога…","Вместе."])
        self.assertTrue(all(x["text_ru"].strip() for x in t["dialogues"]))
        self.assertFalse(any(re.search(r"[\u4e00-\u9fff]",x["text_ru"]) for x in t["dialogues"]))
        self.assertEqual((t["source"]["cn_git_blob_sha1"],t["source"]["en_git_blob_sha1"]),("0986ac67e9b36541dc93f82e53dd687780015d60","92b2237c92178fb888e2c6928c6bae6b2a45a0e8"))

    def test_source_audit(self):
        a=load("reports/CHAPTER_6_STAGE_6-11_BEFORE_SOURCE_AUDIT_v176.json")
        self.assertEqual((a["alignment"]["cn_text_positions"],a["alignment"]["en_text_positions"]),(180,180))
        self.assertEqual((a["alignment"]["command_lines_cn"],a["alignment"]["command_lines_en"]),(187,187))
        self.assertTrue(a["alignment"]["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertEqual((a["alignment"]["translated_range"]["translated_positions"],a["alignment"]["translated_range"]["remaining_positions"]),(120,60))
        self.assertEqual(a["alignment"]["translated_range"]["command_lines_cn"],115)
        self.assertEqual(a["alignment"]["translated_range"]["decision_options_translated"],3)
        self.assertEqual(a["alignment"]["decision_options_ru"][1]["options_ru"][0],"Но, как тогда, в руинах Чернобога…")
        self.assertFalse(a["editorial_review"])
        self.assertFalse(a["in_game_test"])

    def test_index_and_selection(self):
        idx=(ROOT/"story/CHAPTER_6_INDEX_v176.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-11_beg.txt\tpartial_first_draft\t120\t0\t120\t0986ac67e9b36541dc93f82e53dd687780015d60\t92b2237c92178fb888e2c6928c6bae6b2a45a0e8",idx)
        self.assertEqual(sum(1 for x in idx.splitlines() if x.strip())-1,19)
        s=load("story/story_main_selection_ru_v174.json")
        self.assertEqual((len(s["files"]),sum(x["dialogue_count"] for x in s["files"].values())),(115,8215))

    def test_qa_and_chronology(self):
        q=load("reports/QA_MAIN_STORY_v176.json")
        self.assertEqual((q["completed_story_files"],q["completed_story_text_entries"]),(115,8216))
        self.assertEqual((q["partial_scene_files"],q["partial_scene_named_ru"],q["partial_scene_text_entries"]),(1,120,120))
        self.assertEqual(q["all_story_text_entries_including_partial"],8336)
        self.assertEqual((q["chapter_6_partial_files"],q["chapter_6_partial_named_ru"],q["chapter_6_text_entries_including_partial"]),(1,120,2091))
        self.assertEqual((q["next_scene"]["next_ordinal"],q["next_scene"]["next_source_line"]),(121,238))
        m=load("chronology/CHRONOLOGY_MANIFEST_v336.json")
        self.assertEqual(m["version"],"v3.36")
        self.assertEqual((m["translation_integrity"]["main_story_partial_named_ru_lines"],m["translation_integrity"]["main_story_text_entries_including_partial"]),(120,8336))
        self.assertEqual((m["next_text_ordinal"],m["next_text_source_line"]),(121,238))

    def test_readme_and_decision_branches(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertIn("v3.36",readme)
        self.assertIn("120/180",readme)
        self.assertIn("Следующая позиция — №121",readme)
        a=load("reports/CHAPTER_6_STAGE_6-11_BEFORE_SOURCE_AUDIT_v176.json")
        self.assertEqual(a["alignment"]["predicate_branches"],3)
        self.assertEqual(a["alignment"]["decision_values_and_predicate_references_match"],True)

if __name__=="__main__":
    unittest.main()
