# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV171(unittest.TestCase):
    def test_translation_and_source_audit(self):
        t = load("story/story_chapter_6_stage_6-8_before_ru_v171.json")
        a = load("reports/MAIN_6-8_BEFORE_SOURCE_AUDIT_v171.json")
        self.assertEqual(t["version"], "v1.71")
        self.assertTrue(t["progress"]["complete"])
        self.assertEqual((t["progress"]["translated"], t["progress"]["total"], t["progress"]["remaining"]), (117, 117, 0))
        self.assertEqual(len(t["dialogues"]), 117)
        self.assertEqual([x["ordinal"] for x in t["dialogues"]], list(range(1, 118)))
        self.assertEqual([x["source_line"] for x in t["dialogues"]], sorted(x["source_line"] for x in t["dialogues"]))
        self.assertTrue(all(x["text_ru"].strip() for x in t["dialogues"]))
        self.assertEqual(t["source"]["cn_git_blob_sha1"], "198a8387a3748041f6f9063348fd61552c8c4cf2")
        self.assertEqual(t["source"]["en_git_blob_sha1"], "bf2271985bc64d1b87d338d2f0409e304ee97e60")
        self.assertTrue(a["alignment"]["named_position_count_match"])
        self.assertTrue(a["alignment"]["named_line_number_match"])
        self.assertTrue(a["alignment"]["command_text_and_parameter_match"])
        self.assertEqual(a["source"]["cn_command_lines"], 110)
        self.assertEqual(a["source"]["en_command_lines"], 110)
        self.assertEqual(sum(a["command_counts"].values()), 110)
        self.assertEqual(a["source"]["cn_unnamed_positions"], 0)
        self.assertEqual(a["source"]["en_unnamed_positions"], 0)
        self.assertEqual(t["header_title_ru"], "Этап 4 (до боя)")

    def test_selection_index_and_qa(self):
        s = load("story/story_main_selection_ru_v171.json")
        self.assertEqual(s["version"], "v1.71")
        self.assertEqual(len(s["files"]), 112)
        self.assertEqual(sum(x["dialogue_count"] for x in s["files"].values()), 7786)
        self.assertEqual(s["files"]["obt/main/level_main_06-08_beg.txt"]["dialogue_count"], 117)
        self.assertEqual(len(s["files"]["obt/main/level_main_06-08_beg.txt"]["dialogues"]), 117)
        idx = (ROOT / "story/CHAPTER_6_INDEX_v171.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-08_beg.txt\tfirst_draft_complete\t117\t0\t117", idx)
        q = load("reports/QA_MAIN_STORY_v171.json")
        self.assertEqual((q["completed_story_files"], q["completed_story_text_entries"]), (112, 7787))
        self.assertEqual((q["partial_scene_files"], q["partial_scene_text_entries"]), (2, 205))
        self.assertEqual(q["selection_vs_historical_manifest_delta"], 1)

    def test_chronology_and_readme(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v331.json")
        self.assertEqual(m["version"], "v3.31")
        self.assertEqual(m["translation_integrity"]["main_story_files"], 112)
        self.assertEqual(m["translation_integrity"]["main_story_partial_files"], 2)
        self.assertEqual(m["next_file"], "obt/main/level_main_06-09_end.txt")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v3.31", readme)
        self.assertIn("112 полных первых черновиков", readme)
        self.assertIn("6-9 после боя", readme)
        self.assertIn("Основной сюжет возобновлён после завершения Babel", readme)

if __name__ == "__main__":
    unittest.main()
