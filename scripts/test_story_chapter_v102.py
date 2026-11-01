# coding: utf-8
"""Regression checks for Arknights RU v1.02, 5-7 after battle."""
import json
import re
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap
REL = "obt/main/level_main_05-07_end.txt"
NEW = "story/story_chapter_5_stage_5-7_after_ru_v102.json"
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class Chapter57AfterV102(unittest.TestCase):
    def test_complete_and_pinned(self):
        c = load(NEW)["files"][REL]
        self.assertEqual((c["dialogue_count"],c["named_dialogue_count"],c["unnamed_dialogue_count"]),(92,90,2))
        self.assertEqual(set(c["dialogues"]),{str(i) for i in range(1,93)})
        self.assertTrue(all(s.strip() and not any(x in s for x in "\r\n\t") for s in c["dialogues"].values()))
        self.assertEqual(c["cn_git_blob_sha1"],"b1ddd2da99c09995c17c717cd51855d4216cd1ef")
        self.assertEqual(c["en_git_blob_sha1"],"cb5b1c86451cde4993a9a2b0dc1c1835dc3ffbfa")
        self.assertIn("опереться",c["dialogues"]["73"])
    def test_selection_preserves_91_previous_files(self):
        old,new=load("story/story_main_selection_ru_v101.json"),load("story/story_main_selection_ru_v102.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(91,92))
        self.assertEqual(set(new["files"])-set(old["files"]),{REL})
        for k,v in old["files"].items():
            self.assertEqual(new["files"][k],v)
        self.assertEqual(new["files"][REL],load(NEW)["files"][REL])
        self.assertEqual(sum(c["dialogue_count"] for c in new["files"].values()),5558)
    def test_audit_manifest_index_qa(self):
        a=load("reports/CHAPTER_5_STAGE_5-7_AFTER_SOURCE_AUDIT_v102.json")
        m=load("chronology/CHRONOLOGY_MANIFEST_v102.json")
        q=load("reports/QA_MAIN_STORY_v102.json")
        self.assertEqual((a["alignment"]["cn_named"],a["alignment"]["en_named"]),(90,90))
        self.assertEqual((a["alignment"]["cn_bare"],a["alignment"]["en_bare"]),(2,2))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"],a["alignment"]["en_non_dialogue_commands"]),(95,95))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        self.assertTrue(a["alignment"]["cn_en_non_dialogue_commands_equal"])
        self.assertEqual(m["next_file"],"obt/main/level_main_05-09_beg.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(92,5525))
        self.assertEqual((q["new_text_entries"],q["source_text_entries_remaining"],q["completed_story_files"]),(92,0,92))
        self.assertIn("level_main_05-07_end.txt\tfirst_draft_complete\t90\t2\t92",(ROOT/"story/CHAPTER_5_INDEX_v102.tsv").read_text(encoding="utf-8"))
    def test_preview_commands_speakers_and_captions(self):
        c=load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH,REL))
        lines=['[HEADER(key="title_test")] title','[Image]']
        for i in range(1,93):
            name="" if i in (78,79) else ("Radio Operator" if 18<=i<=30 else ("???" if i in (50,65) else "Ch'en"))
            lines.append('[name="'+name+'"]  EN line '+str(i))
        lines.append("[Dialog]")
        raw="\n".join(lines)+"\n"
        patched,count=ap.patch_bytes(raw.encode("utf-8"),c["dialogues"])
        result=patched.decode("utf-8").splitlines()
        self.assertEqual(count,92)
        self.assertEqual(result[:2],lines[:2])
        self.assertEqual(result[-1],"[Dialog]")
        self.assertEqual(result[2],'[name="Чэнь"]  '+c["dialogues"]["1"])
        self.assertEqual(result[19],'[name="Радиосвязь"]  '+c["dialogues"]["18"])
        self.assertEqual(result[79],'[name=""]  '+c["dialogues"]["78"])
        self.assertEqual(result[80],'[name=""]  '+c["dialogues"]["79"])
        with self.assertRaises(ValueError):
            ap.patch_bytes(raw.encode("utf-8"),{k:v for k,v in c["dialogues"].items() if k!="92"})
if __name__=="__main__":
    unittest.main()
