# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class MainStory71InterludeV204(unittest.TestCase):
    def test_prefix_and_new_ordinals(self):
        old=load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v203.json")
        new=load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v204.json")
        self.assertEqual(new["version"],"v2.04")
        self.assertEqual(len(new["dialogues"]),120)
        self.assertEqual([x["ordinal"] for x in new["dialogues"]],list(range(1,121)))
        self.assertEqual(new["dialogues"][:80],old["dialogues"])
        self.assertEqual([x["source_line"] for x in new["dialogues"][80:]],[150,151,154,169,170,171,172,173,176,180,181,188,189,190,191,192,194,198,199,200,201,202,206,208,209,211,213,228,229,231,232,234,235,237,238,239,241,243,245,249])
    def test_counts_and_text_integrity(self):
        d=load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v204.json")
        named=[x for x in d["dialogues"] if x["kind"]=="named"];unnamed=[x for x in d["dialogues"] if x["kind"]=="unnamed"]
        self.assertEqual((len(named),len(unnamed)),(77,43))
        self.assertTrue(all(x["text_ru"].strip() for x in d["dialogues"]))
        self.assertFalse(any(re.search(r"[\u4e00-\u9fff]",x["text_ru"]) for x in d["dialogues"]))
        self.assertEqual((d["progress"]["translated"],d["progress"]["total"],d["progress"]["remaining"],d["progress"]["complete"]),(120,286,166,False))
        self.assertEqual((d["progress"]["next_ordinal"],d["progress"]["next_source_line"]),(121,250))
    def test_source_audit_and_commands(self):
        d=load("story/story_chapter_7_stage_7-1_interlude_partial_ru_v204.json");a=load("reports/MAIN_7-1_INTERLUDE_SOURCE_AUDIT_v204.json")
        self.assertEqual((d["source"]["cn_git_blob_sha1"],d["source"]["en_git_blob_sha1"]),("1c613bfbf006470b3b8e131b9fcb8b8f53e19ea5","7a204cb0010abcbf60f12017f0b2b4d02eaba156"))
        self.assertEqual((a["alignment"]["cn_text_positions"],a["alignment"]["en_text_positions"]),(286,286))
        self.assertEqual((a["alignment"]["command_lines_cn"],a["alignment"]["command_lines_en"]),(276,276))
        self.assertTrue(a["alignment"]["commands_match_cn_en"])
        self.assertEqual(a["translated_range"]["command_lines_in_range"],129)
        self.assertEqual(a["translated_range"]["newly_translated_positions"],40)
        self.assertEqual(a["translated_range"]["remaining_positions"],166)
        self.assertEqual(a["translated_range"]["command_counts"]["Character"],55)
        self.assertEqual(a["translated_range"]["command_counts"]["Blocker"],27)
        self.assertFalse(a["editorial_review"]);self.assertFalse(a["in_game_test"])
    def test_index_qa_manifest(self):
        idx=(ROOT/"story/CHAPTER_7_INDEX_v204.tsv").read_text(encoding="utf-8")
        self.assertIn("level_st_07-01.txt\tpartial_first_draft\t77\t43\t120",idx)
        q=load("reports/QA_MAIN_STORY_v204.json")
        self.assertEqual((q["partial_scene_named_ru"],q["partial_scene_unnamed_ru"],q["partial_scene_text_entries"],q["all_story_text_entries_including_partial"]),(77,43,120,10082))
        self.assertEqual((q["next_scene"]["next_ordinal"],q["next_scene"]["next_source_line"]),(121,250))
        self.assertFalse(q["editorial_review"]);self.assertFalse(q["in_game_test"])
        m=load("chronology/CHRONOLOGY_MANIFEST_v364.json")
        self.assertEqual(m["version"],"v3.64")
        self.assertEqual((m["next_text_ordinal"],m["next_text_source_line"]),(121,250))
        self.assertEqual((m["translation_integrity"]["main_story_partial_text_entries"],m["translation_integrity"]["main_story_partial_named_ru_lines"],m["translation_integrity"]["main_story_partial_unnamed_ru_lines"]),(120,77,43))
        self.assertEqual(m["translation_integrity"]["main_story_selection_files"],124)
    def test_readme_glossary(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8");terms=(ROOT/"docs/TERMS_RU.txt").read_text(encoding="utf-8")
        self.assertIn("v3.64",readme);self.assertIn("120/286",readme);self.assertIn("№121",readme)
        self.assertIn("Savra / 萨弗拉 — савра",terms);self.assertIn("Arts — Искусства",terms)
if __name__=="__main__": unittest.main()
