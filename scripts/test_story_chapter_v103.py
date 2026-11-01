# coding: utf-8
"""Regression checks for Arknights RU v1.03: 5-9 before battle."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap
REL = "obt/main/level_main_05-09_beg.txt"
NEW = "story/story_chapter_5_stage_5-9_before_ru_v103.json"

def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

class Chapter59BeforeV103(unittest.TestCase):
    def test_complete_and_source_pins(self):
        c=load(NEW)["files"][REL]
        self.assertEqual((c["dialogue_count"],c["named_dialogue_count"],c["unnamed_dialogue_count"]),(46,44,2))
        self.assertEqual(set(c["dialogues"]),{str(i) for i in range(1,47)})
        self.assertTrue(all(s.strip() and not any(x in s for x in "\\r\\n\\t") for s in c["dialogues"].values()))
        self.assertEqual(c["cn_git_blob_sha1"],"69e9a66b3aefa468d2dc1522aa70371199d631fa")
        self.assertEqual(c["en_git_blob_sha1"],"5a01f7285acbbb292ab87ed46bb3873650b667ec")
        self.assertIn("бои",c["dialogues"]["5"])
    def test_selection_preserves_all_92_previous_files(self):
        old,new=load("story/story_main_selection_ru_v102.json"),load("story/story_main_selection_ru_v103.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(92,93))
        self.assertEqual(set(new["files"])-set(old["files"]),{REL})
        for k,v in old["files"].items(): self.assertEqual(new["files"][k],v)
        self.assertEqual(new["files"][REL],load(NEW)["files"][REL])
        self.assertEqual(sum(c["dialogue_count"] for c in new["files"].values()),5604)
    def test_audit_manifest_index_qa(self):
        a=load("reports/CHAPTER_5_STAGE_5-9_BEFORE_SOURCE_AUDIT_v103.json")
        m=load("chronology/CHRONOLOGY_MANIFEST_v103.json")
        q=load("reports/QA_MAIN_STORY_v103.json")
        self.assertEqual((a["alignment"]["cn_named"],a["alignment"]["en_named"]),(44,44))
        self.assertEqual((a["alignment"]["cn_bare"],a["alignment"]["en_bare"]),(2,2))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"],a["alignment"]["en_non_dialogue_commands"]),(55,55))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertTrue(a["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(m["next_file"],"obt/main/level_main_05-09_end.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(93,5569))
        self.assertEqual((q["new_text_entries"],q["source_text_entries_remaining"],q["completed_story_files"]),(46,0,93))
        self.assertIn("level_main_05-09_beg.txt\\tfirst_draft_complete\\t44\\t2\\t46",(ROOT/"story/CHAPTER_5_INDEX_v103.tsv").read_text(encoding="utf-8"))
    def test_preview_commands_and_speakers(self):
        c=load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH,REL))
        lines=['[HEADER(key="title_test")] title','[Image]']
        for i in range(1,47):
            name="" if i<=2 else ("Mephisto" if i==44 else ("???" if i in (41,42) else ("L.G.D. Agent" if i==3 else "Ch'en")))
            lines.append('[name="'+name+'"]  EN line '+str(i))
        lines.append("[Dialog]")
        raw="\\n".join(lines)+"\\n"
        patched,count=ap.patch_bytes(raw.encode("utf-8"),c["dialogues"])
        result=patched.decode("utf-8").splitlines()
        self.assertEqual(count,46)
        self.assertEqual(result[:2],lines[:2])
        self.assertEqual(result[-1],"[Dialog]")
        self.assertEqual(result[2],'[name=""]  '+c["dialogues"]["1"])
        self.assertEqual(result[4],'[name="Сотрудник городской стражи"]  '+c["dialogues"]["3"])
        self.assertEqual(result[45],'[name="Мефисто"]  '+c["dialogues"]["44"])
        with self.assertRaises(ValueError):
            ap.patch_bytes(raw.encode("utf-8"),{k:v for k,v in c["dialogues"].items() if k!="46"})
if __name__=="__main__":
    unittest.main()
