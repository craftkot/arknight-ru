# coding: utf-8
"""v0.67: chapter 4-1 before battle, named + unnamed text and four decisions."""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap

REL="obt/main/level_main_04-01_beg.txt"
NEW="story/story_chapter_4_stage_4-1_before_ru_v067.json"
CN="be553a2f7ed2b086486a2cc8f2f599fe8b0fa0b0"
EN="9034b069d0501eb39395dd480aa2ad932e1d5ef0"

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

class Chapter41BeforeV067(unittest.TestCase):
    def test_full_scene_and_markup(self):
        d=load(NEW)
        self.assertEqual(d["version"],"v0.67")
        self.assertEqual(set(d["files"]),{REL})
        s=d["files"][REL]
        self.assertEqual((s["dialogue_count"],s["named_dialogue_count"],s["unnamed_dialogue_count"]),(91,89,2))
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,92))))
        self.assertEqual((s["cn_git_blob_sha1"],s["en_git_blob_sha1"]),(CN,EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH,REL))
        self.assertEqual([len(s["decisions"][str(i)]) for i in range(1,5)],[1,1,2,2])
        for line in s["dialogues"].values():
            self.assertTrue(isinstance(line,str) and line.strip())
            self.assertFalse(any(c in line for c in "\${ch}\${ch}\${ch}"))
        self.assertEqual(s["dialogues"]["1"],"20:36 \\ Дождь \\ Видимость: 12 км")
        self.assertIn("атмосфера",s["dialogues"]["24"])
        self.assertIn("уцелеть",s["dialogues"]["56"])
        self.assertIn("оболочка",s["dialogues"]["80"])
        for i in (27,31,49,51,67,74):
            self.assertIn("{@nickname}",s["dialogues"][str(i)])
    def test_selection_preserves_previous_60(self):
        old=load("story/story_main_selection_ru_v066.json")
        new=load("story/story_main_selection_ru_v067.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(60,61))
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()),3622)
        self.assertEqual(set(new["files"])-set(old["files"]),{REL})
        for key,val in old["files"].items():
            self.assertEqual(new["files"][key],val)
        self.assertEqual(new["files"][REL],load(NEW)["files"][REL])
    def test_manifest_and_audit(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v067.json")
        s=m["translation_integrity"]
        self.assertEqual((s["main_story_files"],s["main_story_named_ru_lines"]),(61,3620))
        self.assertEqual((s["main_story_chapter_4_files"],s["main_story_chapter_4_named_ru_lines"]),(1,89))
        self.assertEqual(m["next_file"],"obt/main/level_main_04-01_end.txt")
        a=load("reports/CHAPTER_4_STAGE_4-1_BEFORE_SOURCE_AUDIT_v067.json")
        self.assertEqual((a["alignment"]["cn_named"],a["alignment"]["en_named"]),(89,89))
        self.assertEqual((a["alignment"]["cn_unnamed"],a["alignment"]["en_unnamed"]),(2,2))
        self.assertEqual(a["alignment"]["decision_option_counts"],[1,1,2,2])
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"],a["sources"]["en"]["git_blob_sha1"]),(CN,EN))
        q=load("reports/QA_MAIN_STORY_v067.json")
        self.assertEqual((q["new_named_ru"],q["new_unnamed_ru"]),(89,2))
        self.assertFalse(q["in_game_test"])
    def test_safe_preview_with_unnamed_lines_and_choices(self):
        d=copy.deepcopy(load(NEW))
        s=d["files"][REL]
        lines=['[HEADER(key="test")]\${ch}','[PlayMusic(key="test")]\${ch}']
        for i in range(1,92):
            speaker="" if i<=2 else ("Amiya" if i%2 else "Kal'tsit")
            tokens=" ".join(ap.quoted_tokens(s["dialogues"][str(i)]))
            lines.append('[name="'+speaker+'"]   EN '+str(i)+' '+tokens+'\${ch}')
            if i in (29,41,50,84):
                k={29:1,41:2,50:3,84:4}[i]
                n=len(s["decisions"][str(k)])
                lines.append('[Decision(options="'+ ';'.join('EN'+str(x) for x in range(n))+'", values="'+ ';'.join(str(x+1) for x in range(n))+'")]\${ch}')
                lines.append('[Predicate(references="1")]\${ch}')
            if i%11==0:
                lines.append('[CameraShake(duration=0.5)]\${ch}')
        lines.append('[Image]\${ch}')
        original="".join(lines).encode("utf-8")
        result,count=ap.patch_bytes(original,s["dialogues"],ru_choices=s["decisions"])
        self.assertEqual(count,91)
        before=original.decode().splitlines()
        after=result.decode().splitlines()
        self.assertEqual(len(before),len(after))
        for x,y in zip(before,after):
            if not ap.SPEAKER.search(x) and not ap.DECISION.search(x):
                self.assertEqual(x,y)
        self.assertIn('name=""',after[2])
        self.assertTrue(any("Постучать" in x for x in after))
        self.assertTrue(any("уцелеть" in x for x in after))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for lang in ("cn","en"):
                p=root/"source"/lang/REL
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(original)
                s[lang+"_git_blob_sha1"]=ap.git_blob_sha1(original)
            draft=root/"draft.json"
            draft.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            report=ap.build(root/"source",root/"preview",draft)
            self.assertEqual(report["lines_total"],91)
            self.assertEqual((root/"preview"/"ru"/REL).read_bytes(),result)
if __name__=="__main__":
    unittest.main()
