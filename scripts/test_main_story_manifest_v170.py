# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV170(unittest.TestCase):
    def test_selection_and_completed_scene_counts(self):
        s = load("story/story_main_selection_ru_v170.json")
        self.assertEqual(s["version"], "v1.70")
        files = s["files"]
        self.assertEqual(len(files), 111)
        self.assertEqual(sum(x["dialogue_count"] for x in files.values()), 7669)
        self.assertIn("obt/main/level_main_06-06_beg.txt", files)
        self.assertIn("obt/main/level_main_06-07_end.txt", files)
        for key in ("obt/main/level_main_06-08_beg.txt","obt/main/level_main_06-09_end.txt","obt/main/level_main_06-10_beg.txt"):
            self.assertNotIn(key, files)

    def test_chapter_index_and_qa(self):
        idx = (ROOT / "story/CHAPTER_6_INDEX_v170.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-06_beg.txt\tfirst_draft_complete\t150\t2\t152", idx)
        self.assertIn("level_main_06-10_beg.txt\tpartial_first_draft\t80\t5\t85", idx)
        q = load("reports/QA_MAIN_STORY_v170.json")
        self.assertEqual((q["completed_story_files"],q["completed_story_text_entries"]),(111,7670))
        self.assertEqual((q["partial_scene_files"],q["partial_scene_text_entries"]),(3,322))
        self.assertEqual(q["selection_vs_historical_manifest_delta"],1)

    def test_chronology_and_readme(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v294.json")
        self.assertEqual(m["translation_integrity"]["main_story_files"],111)
        self.assertEqual(m["translation_integrity"]["main_story_partial_files"],3)
        self.assertEqual(m["next_file"],"activities/act33side/level_act33side_06_beg.txt")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("111 полных первых черновиков", readme)
        self.assertIn("Основной сюжет приостановлен", readme)

if __name__ == "__main__":
    unittest.main()
