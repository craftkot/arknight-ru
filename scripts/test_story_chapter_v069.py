# coding: utf-8
"""v0.69: 4-1 after battle full first draft, 76 text positions and 3 decisions."""
import json
from pathlib import Path
import re
import sys
import unittest
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_04-01_end.txt"
NEW="story/story_chapter_4_stage_4-1_after_ru_v069.json"
CN="311a849380f0cc13048d20f1bdf052d71d6870d5"
EN="a86c16ded890cedd0be9d41be3ebdef8781f1ff5"
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Chapter41AfterV069(unittest.TestCase):
    def test_complete_text_and_choices(self):
        s=load(NEW)["files"][REL]
        self.assertEqual((s["dialogue_count"],s["named_dialogue_count"],s["unnamed_dialogue_count"]),(76,71,5))
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,77))))
        self.assertEqual((s["cn_git_blob_sha1"],s["en_git_blob_sha1"]),(CN,EN))
        self.assertEqual([len(s["decisions"][str(i)]) for i in range(1,4)],[3,2,3])
        for val in s["dialogues"].values():
            self.assertTrue(isinstance(val,str) and val.strip())
            self.assertFalse(any(c in val for c in "\\r\\n\\t"))
        self.assertEqual(s["dialogues"]["32"],"18:12 \\ Облачно \\ Видимость: 19 км")
        self.assertIn("мобильного города",s["dialogues"]["34"])
        self.assertIn("{@nickname}",s["dialogues"]["36"])
        self.assertIn("{@nickname}",s["dialogues"]["59"])
        self.assertEqual(s["dialogues"]["62"].count("&"),1)
        self.assertIn("другое задание",s["dialogues"]["74"])
    def test_preserve_previous_23(self):
        old=load("story/story_chapter_4_stage_4-1_after_partial_ru_v068.json")["files"][REL]
        new=load(NEW)["files"][REL]
        for k,v in old["dialogues"].items():
            self.assertEqual(new["dialogues"][k],v)
    def test_selection_preserves_previous_61(self):
        old=load("story/story_main_selection_ru_v067.json")
        new=load("story/story_main_selection_ru_v069.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(61,62))
        self.assertEqual(set(new["files"])-set(old["files"]),{REL})
        self.assertEqual(sum(s["dialogue_count"] for s in new["files"].values()),3698)
        for k,v in old["files"].items():
            self.assertEqual(new["files"][k],v)
        self.assertEqual(new["files"][REL],load(NEW)["files"][REL])
    def test_qa_chronology_and_index(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v069.json")
        t=m["translation_integrity"]
        self.assertEqual(m["next_file"],"obt/main/level_main_04-02_beg.txt")
        self.assertEqual((t["main_story_files"],t["main_story_named_ru_lines"]),(62,3691))
        self.assertEqual((t["main_story_chapter_4_files"],t["main_story_chapter_4_named_ru_lines"]),(2,160))
        self.assertEqual(t["main_story_chapter_4_partial_files"],0)
        a=load("reports/CHAPTER_4_STAGE_4-1_AFTER_SOURCE_AUDIT_v069.json")
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"],a["sources"]["en"]["git_blob_sha1"]),(CN,EN))
        self.assertEqual((a["alignment"]["ru_complete_text_entries"],a["alignment"]["ru_choice_options"]),(76,8))
        q=load("reports/QA_MAIN_STORY_v069.json")
        self.assertEqual((q["new_text_entries"],q["completed_story_files"]),(53,62))
        self.assertTrue(q["included_in_complete_story_selection"])
        self.assertFalse(q["in_game_test"])
        idx=(ROOT/"story/CHAPTER_4_INDEX_v069.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-01_end.txt\\tfirst_draft_complete\\t71\\t5\\t76",idx)
    def test_safe_preview_choices_and_unnamed(self):
        s=load(NEW)["files"][REL]
        lines=['[HEADER(key="test")]\\n']
        for i in range(1,77):
            speaker="" if i in (1,2,32,33,34) else "Amiya"
            lines.append('[name="'+speaker+'"] EN '+str(i)+'\\n')
            if i in (37,59,72):
                k={37:1,59:2,72:3}[i]
                n=len(s["decisions"][str(k)])
                lines.append('[Decision(options="'+ ';'.join('EN'+str(x) for x in range(n))+'", values="'+ ';'.join(str(x+1) for x in range(n))+'")]\\n')
                lines.append('[Predicate(references="'+ ';'.join(str(x+1) for x in range(n))+'")]\\n')
            if i%12==0:
                lines.append('[CameraShake(duration=0.5)]\\n')
        original="".join(lines).encode("utf-8")
        out,count=ap.patch_bytes(original,s["dialogues"],ru_choices=s["decisions"])
        self.assertEqual(count,76)
        before=original.decode().splitlines()
        after=out.decode().splitlines()
        self.assertEqual(len(before),len(after))
        for x,y in zip(before,after):
            if not ap.SPEAKER.search(x) and not ap.DECISION.search(x):
                self.assertEqual(x,y)
        self.assertTrue(any("Я буду по вам скучать." in x for x in after))
        self.assertTrue(any("мобильного города" in x for x in after))
if __name__=="__main__":
    unittest.main()
