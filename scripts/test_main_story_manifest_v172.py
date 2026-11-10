# -*- coding: utf-8 -*-
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStoryManifestV172(unittest.TestCase):
    def test_translation_and_source_audit(self):
        t = load("story/story_chapter_6_stage_6-9_after_ru_v172.json")
        a = load("reports/MAIN_6-9_AFTER_SOURCE_AUDIT_v172.json")
        self.assertEqual(t["version"], "v1.72")
        self.assertTrue(t["progress"]["complete"])
        self.assertEqual((t["progress"]["translated"], t["progress"]["total"], t["progress"]["remaining"]), (120, 120, 0))
        self.assertEqual(len(t["dialogues"]), 120)
        self.assertEqual([x["ordinal"] for x in t["dialogues"]], list(range(1, 121)))
        self.assertEqual([x["source_line"] for x in t["dialogues"]], sorted(x["source_line"] for x in t["dialogues"]))
        self.assertTrue(all(x["text_ru"].strip() for x in t["dialogues"]))
        self.assertEqual(t["source"]["cn_git_blob_sha1"], "ff213f0a92ac216e8c9a1a8066b563724ed2ce9c")
        self.assertEqual(t["source"]["en_git_blob_sha1"], "4e2a11deddd5e00efd20e3b64bc77381fa6eb519")
        self.assertEqual(t["header_title_ru"], "Этап 4 (после боя)")
        self.assertEqual(t["existing_translation_revision"]["new_dialogue_positions_in_this_change"], 0)
        self.assertEqual(t["existing_translation_revision"]["revised_dialogue_positions"], 16)
        self.assertEqual(t["dialogues"][97]["text_ru"], "Они сносят трущобы до основания.")
        self.assertEqual(t["dialogues"][80]["text_ru"], "Где Нести? Огневой мощи не хватает! Нужно усилить подавляющий обстрел!")
        self.assertTrue(a["alignment"]["named_position_count_match"])
        self.assertTrue(a["alignment"]["named_line_number_match"])
        self.assertTrue(a["alignment"]["command_text_and_parameter_match"])
        self.assertEqual(a["source"]["cn_command_lines"], 135)
        self.assertEqual(a["source"]["en_command_lines"], 135)
        self.assertEqual(sum(a["command_counts"].values()), 135)
        self.assertEqual(a["source"]["cn_unnamed_positions"], 0)
        self.assertEqual(a["source"]["en_unnamed_positions"], 0)
        self.assertEqual(a["header_title"]["translation_ru"], "Этап 4 (после боя)")

    def test_selection_index_and_qa(self):
        s = load("story/story_main_selection_ru_v172.json")
        self.assertEqual(s["version"], "v1.72")
        self.assertEqual(len(s["files"]), 113)
        self.assertEqual(sum(x["dialogue_count"] for x in s["files"].values()), 7906)
        self.assertEqual(s["files"]["obt/main/level_main_06-09_end.txt"]["dialogue_count"], 120)
        self.assertEqual(len(s["files"]["obt/main/level_main_06-09_end.txt"]["dialogues"]), 120)
        idx = (ROOT / "story/CHAPTER_6_INDEX_v172.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_06-09_end.txt\tfirst_draft_complete\t120\t0\t120", idx)
        q = load("reports/QA_MAIN_STORY_v172.json")
        self.assertEqual((q["completed_story_files"], q["completed_story_text_entries"]), (113, 7907))
        self.assertEqual((q["partial_scene_files"], q["partial_scene_text_entries"]), (1, 85))
        self.assertEqual(q["selection_vs_historical_manifest_delta"], 1)
        self.assertEqual(q["completed_scene_audit"]["command_lines"], 135)

    def test_chronology_and_readme(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v332.json")
        self.assertEqual(m["version"], "v3.32")
        self.assertEqual(m["translation_integrity"]["main_story_files"], 113)
        self.assertEqual(m["translation_integrity"]["main_story_partial_files"], 1)
        self.assertEqual(m["next_file"], "obt/main/level_main_06-10_beg.txt")
        self.assertEqual(m["next_text_ordinal"], 86)
        self.assertEqual(m["next_text_source_line"], 174)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v3.32", readme)
        self.assertIn("113 полных первых черновиков", readme)
        self.assertIn("6-9 после боя", readme)
        self.assertIn("6-10 до боя", readme)

if __name__ == "__main__":
    unittest.main()
