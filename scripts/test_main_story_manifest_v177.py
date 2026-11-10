# -*- coding: utf-8 -*-
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV177(unittest.TestCase):
    def test_full_scene_and_preserved_partial(self):
        t = load("story/story_chapter_6_stage_6-11_before_ru_v177.json")
        old = load("story/story_chapter_6_stage_6-11_before_partial_ru_v176.json")
        self.assertEqual(t["version"], "v1.77")
        self.assertEqual((t["progress"]["translated"], t["progress"]["total"], t["progress"]["remaining"]), (180, 180, 0))
        self.assertTrue(t["progress"]["complete"])
        self.assertEqual(len(t["dialogues"]), 180)
        self.assertEqual([x["ordinal"] for x in t["dialogues"]], list(range(1, 181)))
        self.assertEqual(t["dialogues"][:120], old["dialogues"])
        self.assertTrue(all(x["text_ru"].strip() for x in t["dialogues"]))
        self.assertFalse(any(re.search(r"[\u4e00-\u9fff]", x["text_ru"]) for x in t["dialogues"]))
        self.assertEqual(t["decision_options_ru"], old["decision_options_ru"])

    def test_new_tail_source_positions(self):
        t = load("story/story_chapter_6_stage_6-11_before_ru_v177.json")
        tail = t["dialogues"][120:]
        self.assertEqual([x["source_line"] for x in tail], [238,239,243,244,245,249,256,258,260,262,264,266,268,270,271,273,274,276,278,279,280,282,284,291,292,294,296,298,299,301,303,305,307,308,310,312,314,321,322,323,324,325,326,333,335,337,339,340,341,348,349,350,352,354,356,357,359,360,361,363])
        self.assertEqual(tail[21]["speaker_cn"], "大熊")
        self.assertEqual(tail[-2]["speaker_cn"], "佩特洛娃")
        self.assertEqual(tail[-1]["speaker_cn"], "煌")
        self.assertIn("хлеба", tail[9]["text_ru"])
        self.assertIn("супом", tail[9]["text_ru"])
        self.assertIn("Булдроккас'ти", tail[55]["text_ru"])

    def test_source_audit(self):
        a = load("reports/CHAPTER_6_STAGE_6-11_BEFORE_SOURCE_AUDIT_v177.json")
        self.assertEqual((a["alignment"]["cn_text_positions"], a["alignment"]["en_text_positions"]), (180, 180))
        self.assertEqual((a["alignment"]["command_lines_cn"], a["alignment"]["command_lines_en"]), (187, 187))
        self.assertTrue(a["alignment"]["command_names_and_parameters_match_after_decision_option_normalization"])
        self.assertEqual(a["alignment"]["decision_option_total"], 3)
        self.assertEqual(a["alignment"]["predicate_branches"], 3)
        self.assertEqual(a["alignment"]["translated_range"]["newly_translated_positions"], 60)
        self.assertEqual(a["alignment"]["translated_range"]["remaining_positions"], 0)
        self.assertFalse(a["editorial_review"])
        self.assertFalse(a["in_game_test"])

    def test_index_and_selection(self):
        idx = (ROOT / "story/CHAPTER_6_INDEX_v177.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-11_beg.txt\tfirst_draft_complete\t180\t0\t180\t0986ac67e9b36541dc93f82e53dd687780015d60\t92b2237c92178fb888e2c6928c6bae6b2a45a0e8", idx)
        s = load("story/story_main_selection_ru_v175.json")
        self.assertEqual((s["version"], len(s["files"])), ("v1.75", 116))
        self.assertEqual(s["summary"]["total_dialogue_entries"], 8395)
        f = s["files"]["obt/main/level_main_06-11_beg.txt"]
        self.assertEqual(f["dialogue_count"], 180)
        self.assertEqual(len(f["dialogues"]), 180)
        self.assertEqual(len(f["decisions"]), 3)

    def test_qa_and_chronology(self):
        q = load("reports/QA_MAIN_STORY_v177.json")
        self.assertEqual((q["completed_story_files"],q["completed_story_named_ru"],q["completed_story_text_entries"]),(116,8290,8396))
        self.assertEqual((q["partial_scene_files"],q["partial_scene_named_ru"],q["partial_scene_text_entries"]),(0,0,0))
        self.assertEqual((q["chapter_6_complete_files"],q["chapter_6_complete_named_ru"],q["chapter_6_complete_text_entries"]),(19,2087,2151))
        m = load("chronology/CHRONOLOGY_MANIFEST_v337.json")
        self.assertEqual(m["version"],"v3.37")
        self.assertEqual((m["next_text_ordinal"],m["next_text_source_line"]),(1,6))
        self.assertEqual(m["next_source"]["cn_git_blob_sha1"],"68639fdcc567ae79289307d5c9a9a7faf64e10a4")
        self.assertEqual(m["next_source"]["en_git_blob_sha1"],"d3aa2303aea8ec614f3de6c9a739211a0971e73")

    def test_readme_and_terms(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v3.37", readme)
        self.assertIn("180/180", readme)
        self.assertIn("level_main_06-12_end.txt", readme)
        terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertIn("Buldrokkas'tee / 博卓卡斯替 — Булдроккас'ти", terms)
        self.assertIn("Frost Originium / 霜冻源石", terms)

if __name__ == "__main__":
    unittest.main()
