# coding: utf-8
"""Regression tests for chapter 4-7 after battle (v0.81)."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_04-07_end.txt"
NEW="story/story_chapter_4_stage_4-7_after_ru_v081.json"
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
class Chapter47AfterV081(unittest.TestCase):
    def test_complete_and_source_pins(self):
        cfg=load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"],cfg["named_dialogue_count"],cfg["unnamed_dialogue_count"]),(40,40,0))
        self.assertEqual(set(cfg["dialogues"]),set(map(str,range(1,41))))
        self.assertEqual((cfg["cn_git_blob_sha1"],cfg["en_git_blob_sha1"]),("429bd34de75b11cdbf25c00bd7630a26b7f93470","8e912427879d7868b826e2f06404503b1e99a0f8"))
        self.assertIn("защитных средств",cfg["dialogues"]["23"])
        self.assertIn("никого не бросит",cfg["dialogues"]["27"])
        for s in cfg["dialogues"].values():
            self.assertTrue(isinstance(s,str) and s.strip())
            self.assertFalse(any(c in s for c in "\\r\\n\\t"))
    def test_previous_scenes_unchanged(self):
        old=load("story/story_main_selection_ru_v080.json")
        new=load("story/story_main_selection_ru_v081.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(73,74))
        self.assertEqual(set(new["files"])-set(old["files"]),{REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()),4355)
        for k,v in old["files"].items(): self.assertEqual(new["files"][k],v)
        self.assertEqual(new["files"][REL],load(NEW)["files"][REL])
    def test_audit_and_manifest(self):
        a=load("reports/CHAPTER_4_STAGE_4-7_AFTER_SOURCE_AUDIT_v081.json")["alignment"]
        self.assertEqual((a["cn_named"],a["en_named"],a["ru_complete_text_entries"]),(40,40,40))
        self.assertEqual((a["source_non_dialogue_commands_cn"],a["source_non_dialogue_commands_en"]),(30,30))
        self.assertTrue(a["cn_en_text_source_line_positions_equal"] and a["cn_en_non_dialogue_commands_equal"])
        m=load("chronology/CHRONOLOGY_MANIFEST_v081.json")
        self.assertEqual(m["next_file"],"obt/main/level_main_04-08_beg.txt")
        t=m["translation_integrity"]
        self.assertEqual((t["main_story_files"],t["main_story_named_ru_lines"]),(74,4339))
        self.assertEqual((t["main_story_chapter_4_files"],t["main_story_chapter_4_named_ru_lines"],t["main_story_chapter_4_unnamed_ru_lines"]),(14,808,16))
        q=load("reports/QA_MAIN_STORY_v081.json")
        self.assertEqual((q["new_text_entries"],q["completed_story_files"]),(40,74))
        self.assertFalse(q["in_game_test"])
        idx=(ROOT/"story/CHAPTER_4_INDEX_v081.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-07_end.txt\\tfirst_draft_complete\\t40\\t0\\t40",idx)
    def test_preview_preserves_commands(self):
        cfg=load(NEW)["files"][REL]
        lines=['[HEADER(key="title_test")]\\n','[Background(image="bg_cher_2")]\\n']
        for i in range(1,41):
            lines.append('[Character(name="char_test")]\\n')
            lines.append('[name="Amiya"]   EN dialogue '+str(i)+'\\n')
        lines.append('[Image]\\n')
        original="".join(lines).encode("utf-8")
        patched,count=ap.patch_bytes(original,cfg["dialogues"])
        self.assertEqual(count,40)
        before,after=original.decode().splitlines(),patched.decode().splitlines()
        self.assertEqual(len(before),len(after))
        for x,y in zip(before,after):
            if x.startswith(("[Character","[HEADER","[Background","[Image")): self.assertEqual(x,y)
        self.assertIn(cfg["dialogues"]["40"],patched.decode())
        with self.assertRaises(ValueError): ap.patch_bytes(original,dict(list(cfg["dialogues"].items())[:-1]))
if __name__=="__main__": unittest.main()
