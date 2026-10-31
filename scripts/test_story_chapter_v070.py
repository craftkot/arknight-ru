# coding: utf-8
"""v0.70: chapter 4-2 before battle, CN-primary 80/80 lines."""
import json
from pathlib import Path
import re
import sys
import unittest
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_04-02_beg.txt"
NEW="story/story_chapter_4_stage_4-2_before_ru_v070.json"
CN="f89dec7ec2749e911593165f6ae33eca0f6e1ed0"
EN="1f1bc2b6d54f164787ebe1c9f996d1e78dc58512"
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Chapter42BeforeV070(unittest.TestCase):
    def test_complete_scene_and_source_hashes(self):
        d=load(NEW)
        self.assertEqual(d["version"],"v0.70")
        self.assertEqual(set(d["files"]),{REL})
        s=d["files"][REL]
        self.assertEqual((s["dialogue_count"],s["named_dialogue_count"],s["unnamed_dialogue_count"]),(80,80,0))
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,81))))
        self.assertEqual((s["cn_git_blob_sha1"],s["en_git_blob_sha1"]),(CN,EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH,REL))
        self.assertNotIn("decisions",s)
        for v in s["dialogues"].values():
            self.assertTrue(isinstance(v,str) and v.strip())
            self.assertFalse(any(c in v for c in "\r\n\t"))
        self.assertIn("заброшенном городе",s["dialogues"]["40"])
        self.assertIn("разведку",s["dialogues"]["35"])
        self.assertIn("нагревается",s["dialogues"]["72"])
        self.assertIn("йети",s["dialogues"]["79"])
    def test_selection_preserves_previous_62(self):
        old=load("story/story_main_selection_ru_v069.json")
        new=load("story/story_main_selection_ru_v070.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(62,63))
        self.assertEqual(set(new["files"])-set(old["files"]),{REL})
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()),3778)
        for key,val in old["files"].items():
            self.assertEqual(new["files"][key],val)
        self.assertEqual(new["files"][REL],load(NEW)["files"][REL])
    def test_chronology_qa_index_and_command_divergence(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v070.json")
        t=m["translation_integrity"]
        self.assertEqual(m["next_file"],"obt/main/level_main_04-02_end.txt")
        self.assertEqual((t["main_story_files"],t["main_story_named_ru_lines"]),(63,3771))
        self.assertEqual((t["main_story_chapter_4_files"],t["main_story_chapter_4_named_ru_lines"]),(3,240))
        self.assertEqual(t["main_story_chapter_4_partial_files"],0)
        a=load("reports/CHAPTER_4_STAGE_4-2_BEFORE_SOURCE_AUDIT_v070.json")
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"],a["sources"]["en"]["git_blob_sha1"]),(CN,EN))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertEqual(len(a["alignment"]["non_dialogue_command_differences"]),1)
        self.assertFalse(a["alignment"]["cn_en_non_dialogue_commands_equal_excluding_header_and_decision_text"])
        q=load("reports/QA_MAIN_STORY_v070.json")
        self.assertEqual((q["new_text_entries"],q["completed_story_files"]),(80,63))
        self.assertFalse(q["in_game_test"])
        idx=(ROOT/"story/CHAPTER_4_INDEX_v070.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-02_beg.txt\tfirst_draft_complete\t80\t0\t80",idx)
    def test_safe_preview_and_speaker_names(self):
        s=load(NEW)["files"][REL]
        source=['[HEADER(key="test")]\n']
        speakers=["Jessica","Meteorite","Frostleaf","Kal'tsit","Reunion Member"]
        for i in range(1,81):
            source.append('[name="'+speakers[i%5]+'"] EN '+str(i)+'\n')
            if i%11==0:
                source.append('[CameraShake(duration=0.5)]\n')
        original="".join(source).encode("utf-8")
        out,count=ap.patch_bytes(original,s["dialogues"])
        self.assertEqual(count,80)
        before=original.decode().splitlines()
        after=out.decode().splitlines()
        self.assertEqual(len(before),len(after))
        for a,b in zip(before,after):
            if not ap.SPEAKER.search(a):
                self.assertEqual(a,b)
        self.assertTrue(any('name="Джессика"' in x for x in after))
        self.assertTrue(any('name="Метеорит"' in x for x in after))
        self.assertTrue(any('name="Фростлиф"' in x for x in after))
if __name__=="__main__":
    unittest.main()
