# coding: utf-8
"""v0.66 complete chapter 3-8 ending: structure, preservation and safe preview."""
import copy
import csv
import json
from pathlib import Path
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-08_end.txt"
NEW="story/story_chapter_3_stage_3-8_after_ru_v066.json"
CN="60055bdcb79136fef9d1e728a6c53ba0187f14c1"
EN="da19cbb7090e5207621d210670e609cc407119f1"
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
class Chapter38EndingV066(unittest.TestCase):
    def test_scene_and_source_pins(self):
        d=load(NEW)
        self.assertEqual(d["version"],"v0.66")
        self.assertEqual(set(d["files"]),{REL})
        s=d["files"][REL]
        self.assertEqual(s["dialogue_count"],70)
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,71))))
        self.assertEqual((s["cn_git_blob_sha1"],s["en_git_blob_sha1"]),(CN,EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH,REL))
        self.assertNotIn("decisions",s)
        for line in s["dialogues"].values():
            self.assertTrue(isinstance(line,str) and line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
            self.assertEqual(ap.quoted_tokens(line),[])
        self.assertIn("рак",s["dialogues"]["8"])
        self.assertIn("судьба",s["dialogues"]["30"])
        self.assertIn("терновая цепь",s["dialogues"]["45"])
        self.assertIn("его маску",s["dialogues"]["54"])
    def test_preserve_selection(self):
        old=load("story/story_main_selection_ru_v065.json")
        new=load("story/story_main_selection_ru_v066.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(59,60))
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()),3531)
        self.assertEqual(set(new["files"])-set(old["files"]),{REL})
        for k,v in old["files"].items(): self.assertEqual(v,new["files"][k])
        self.assertEqual(new["files"][REL],load(NEW)["files"][REL])
    def test_index_audit_qa_chronology(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v066.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),16)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows),1154)
        self.assertEqual((rows[-1]["source_filename"],rows[-1]["dialogues_ru_count"]),("level_main_03-08_end.txt","70"))
        self.assertEqual((rows[-1]["cn_git_blob_sha1"],rows[-1]["en_git_blob_sha1"]),(CN,EN))
        m=load("chronology/CHRONOLOGY_MANIFEST_v066.json")
        st=m["translation_integrity"]
        self.assertEqual((st["main_story_files"],st["main_story_named_ru_lines"]),(60,3531))
        self.assertEqual((st["main_story_chapter_3_files"],st["main_story_chapter_3_named_ru_lines"]),(16,1154))
        self.assertEqual(st["main_story_chapter_3_stages_completed"],8)
        self.assertEqual(m["next_file"],"obt/main/level_main_04-01_beg.txt")
        a=load("reports/CHAPTER_3_STAGE_3-8_AFTER_SOURCE_AUDIT_v066.json")
        self.assertEqual((a["alignment"]["cn_named"],a["alignment"]["en_named"]),(70,70))
        self.assertTrue(a["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertTrue(a["alignment"]["cn_en_non_dialogue_source_lines_equal_after_ignoring_terminal_newline"])
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"],a["sources"]["en"]["git_blob_sha1"]),(CN,EN))
        q=load("reports/QA_MAIN_STORY_v066.json")
        self.assertEqual((q["new_named_ru"],q["source_named_total"]),(70,70))
        self.assertEqual(q["source_named_remaining"],0)
        self.assertFalse(q["in_game_test"])
    def test_safe_preview_does_not_change_commands(self):
        s=load(NEW)["files"][REL]
        en=["[HEADER(key=\\"test\\")]\n","[PlayMusic(key=\\"test\\")]\n"]
        for i in range(1,71):
            en.append('[Character(name="char_test")]\n')
            en.append('[name="Ch\\'en"]   EN line '+str(i)+'\n')
            if i%10==0: en.append("[dialog]\n")
        original="".join(en).encode("utf-8")
        patched,count=ap.patch_bytes(original,s["dialogues"])
        self.assertEqual(count,70)
        before=original.decode("utf-8").splitlines()
        after=patched.decode("utf-8").splitlines()
        self.assertEqual(len(before),len(after))
        for x,y in zip(before,after):
            if not ap.SPEAKER.search(x): self.assertEqual(x,y)
        self.assertTrue(any("Погасить ненависть" in x for x in after))
        self.assertTrue(any('[name="Чэнь"]' in x for x in after))
if __name__=="__main__": unittest.main()
