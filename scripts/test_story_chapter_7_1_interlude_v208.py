# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class MainStory71InterludeV208(unittest.TestCase):
    def test_scene_is_complete_and_preserves_v207_prefix(self):
        old = load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v207.json")
        new = load("story/story_chapter_7_stage_7-1_interlude_ru_v208.json")
        self.assertEqual(new["version"], "v2.08")
        self.assertEqual(new["status"], "first_draft_complete")
        self.assertEqual(new["dialogues"][:240], old["dialogues"])
        self.assertEqual(len(new["dialogues"]), 286)
        self.assertEqual([x["ordinal"] for x in new["dialogues"]], list(range(1, 287)))
        self.assertEqual(new["progress"]["translated"], 286)
        self.assertEqual(new["progress"]["total"], 286)
        self.assertEqual(new["progress"]["remaining"], 0)
        self.assertTrue(new["progress"]["complete"])
        self.assertEqual((new["progress"]["named_translated"], new["progress"]["unnamed_translated"]), (215, 71))
        self.assertIsNone(new["progress"]["next_ordinal"])
        self.assertIsNone(new["progress"]["next_source_line"])

    def test_final_positions_are_exact_and_contiguous(self):
        new = load("story/story_chapter_7_stage_7-1_interlude_ru_v208.json")
        expected = [489,490,492,493,494,496,498,500,501,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,531,532,533,540,541,542,544,545,547,549,550,551,552,553,554,555,556,558,559]
        tail = new["dialogues"][240:]
        self.assertEqual([x["ordinal"] for x in tail], list(range(241, 287)))
        self.assertEqual([x["source_line"] for x in tail], expected)
        self.assertEqual(len(tail), 46)
        self.assertEqual(sum(x["kind"] == "named" for x in tail), 46)
        self.assertEqual(sum(x["kind"] == "unnamed" for x in tail), 0)
        self.assertEqual(tail[0]["speaker_cn"], "塔露拉")
        self.assertEqual(tail[9]["speaker_cn"], "凛冽的声音")
        self.assertEqual(tail[10]["speaker_cn"], "沙哑的声音")
        self.assertEqual(tail[-1]["speaker_cn"], "萨卡兹战士")

    def test_source_pins_and_complete_command_preservation(self):
        d = load("story/story_chapter_7_stage_7-1_interlude_ru_v208.json")
        a = load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v208.json")
        self.assertEqual(d["source"]["cn_git_blob_sha1"], "1c613bfbf006470b3b8e131b9fcb8b8f53e19ea5")
        self.assertEqual(d["source"]["en_git_blob_sha1"], "7a204cb0010abcbf60f12017f0b2b4d02eaba156")
        self.assertEqual((d["source_alignment"]["cn_text_positions"], d["source_alignment"]["en_text_positions"]), (286, 286))
        self.assertEqual((d["source_alignment"]["command_lines_cn"], d["source_alignment"]["command_lines_en"]), (276, 276))
        r = d["source_alignment"]["translated_range"]
        self.assertEqual(r["command_lines_in_range"], 276)
        self.assertEqual(r["new_segment_command_lines"], 29)
        self.assertEqual(sum(r["command_counts"].values()), 276)
        self.assertIn(488, r["command_line_numbers"])
        self.assertTrue(d["source_alignment"]["commands_match_cn_en"])
        self.assertTrue(a["integrity"]["complete"])
        self.assertEqual(a["integrity"]["untranslated_positions"], 0)
        self.assertTrue(a["command_preservation"]["all_source_command_positions_preserved"])
        self.assertEqual(a["command_preservation"]["translated_range_command_positions"], 276)
        self.assertEqual(a["command_preservation"]["new_segment_command_positions"], 29)

    def test_cn_primary_differences_and_russian_payload(self):
        d = load("story/story_chapter_7_stage_7-1_interlude_ru_v208.json")
        a = load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v208.json")
        expected = {105,143,176,228,238,363,378,384,406,465,511,544,553}
        self.assertEqual({x["source_line"] for x in d["source_alignment"]["version_differences"]}, expected)
        self.assertIn("Thirteen lexical/meaning differences", d["source"]["version_difference"])
        self.assertIn(553, [x["source_line"] for x in a["version_differences"]])
        for entry in d["dialogues"]:
            self.assertTrue(entry["text_ru"].strip())
            self.assertFalse(re.search(r"[\u4e00-\u9fff]", entry["text_ru"]))

    def test_selection_contains_newly_completed_scene(self):
        s = load("story/story_main_selection_ru_v193.json")
        d = load("story/story_chapter_7_stage_7-1_interlude_ru_v208.json")
        key = "obt/main/level_st_07-01.txt"
        self.assertEqual(s["version"], "v1.93")
        self.assertEqual(len(s["files"]), 125)
        self.assertIn(key, s["files"])
        self.assertEqual(s["files"][key]["dialogue_count"], 286)
        self.assertEqual(s["files"][key]["dialogues"], {str(x["ordinal"]): x["text_ru"] for x in d["dialogues"]})
        self.assertEqual(s["summary"]["complete_files"], 125)
        self.assertEqual(s["summary"]["total_dialogue_entries_counted"], 10247)
        self.assertEqual(s["summary"]["historical_manifest_entries"], 10248)
        self.assertEqual(s["summary"]["inherited_delta"], 1)

    def test_qa_manifest_readme_glossary_and_next_scene(self):
        q = load("reports/QA_MAIN_STORY_v209.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v369.json")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        terms = (ROOT / "docs/TERMS_RU.txt").read_text(encoding="utf-8")
        index = (ROOT / "story/CHAPTER_7_INDEX_v209.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual((q["completed_story_files"], q["completed_story_named_ru"], q["completed_story_unnamed_ru"], q["completed_story_text_entries"]), (125,10015,233,10248))
        self.assertEqual((q["partial_scene_files"], q["partial_scene_text_entries"]), (1,40))
        self.assertEqual(len(q["partial_scenes"]), 1)
        self.assertEqual(q["partial_scenes"][0]["source_file"], "obt/main/level_main_07-02_beg.txt")
        self.assertEqual((q["partial_scenes"][0]["translated"], q["partial_scenes"][0]["remaining"]), (40,172))
        self.assertEqual((q["chapter_7_complete_files"], q["chapter_7_complete_text_entries"]), (1,286))
        self.assertEqual((q["chapter_7_partial_files"], q["chapter_7_partial_text_entries"]), (1,40))
        self.assertEqual(q["next_scene"]["source_file"], "obt/main/level_main_07-02_beg.txt")
        self.assertEqual((q["next_scene"]["total"], q["next_scene"]["translated"], q["next_scene"]["next_ordinal"], q["next_scene"]["next_source_line"]), (212,40,41,97))
        self.assertEqual((m["version"], m["next_file"], m["next_text_ordinal"], m["next_text_source_line"]), ("v3.69","obt/main/level_main_07-02_beg.txt",41,97))
        self.assertEqual(m["translation_integrity"]["main_story_selection_text_entries"], 10247)
        self.assertIn("v3.71", readme.splitlines()[0])
        self.assertIn("v3.70", readme)
        self.assertIn("286/286", readme[:7000])
        self.assertIn("7-2 Night of Farewells", readme[:7000])
        self.assertIn("Леденящий голос", terms)
        self.assertIn("Хриплый голос", terms)
        self.assertIn("воин Сарказов", terms)
        self.assertEqual(len(index), 3)
        self.assertIn("level_st_07-01.txt\tfirst_draft_complete\t215\t71\t286", index[1])
        self.assertIn("level_main_07-02_beg.txt\tfirst_draft_partial\t38\t2\t40", index[2])

if __name__ == "__main__":
    unittest.main()
