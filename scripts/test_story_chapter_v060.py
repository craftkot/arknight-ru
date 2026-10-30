# coding: utf-8
"""v0.60: CN-primary first draft of all 56 dialogue lines in 3-6 before battle."""
import copy
import csv
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap

REL="obt/main/level_main_03-06_beg.txt"
NEW="story/story_chapter_3_stage_3-6_before_ru_v060.json"
CN_SHA="1714fe93bbc26e37c51e1ae1c2d129695562794c"
EN_SHA="c8ccbc44eafbe4a6dc2af3f1d894768e98762a43"

def load(path):
    return json.loads((ROOT/path).read_text("utf-8"))

class Chapter3Stage36BeforeV060(unittest.TestCase):
    def test_full_source_pinned_draft(self):
        doc=load(NEW)
        self.assertEqual(doc["version"],"v0.60")
        self.assertEqual(set(doc["files"]),{REL})
        record=doc["files"][REL]
        self.assertEqual(record["dialogue_count"],56)
        self.assertEqual(set(record["dialogues"]),set(map(str,range(1,57))))
        self.assertEqual((record["cn_git_blob_sha1"],record["en_git_blob_sha1"]),(CN_SHA,EN_SHA))
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        for item in record["dialogues"].values():
            self.assertTrue(isinstance(item,str) and item.strip())
            self.assertFalse(any(ch in item for ch in "\r\n\t"))
        self.assertIn("городская стража сможет сразу арестовать",record["dialogues"]["19"])
        self.assertIn("разными путями",record["dialogues"]["31"])
        self.assertIn("я должна Мишу",record["dialogues"]["33"])
        self.assertIn("заклинатели",record["dialogues"]["43"])
        self.assertEqual(record["dialogues"]["56"],"Это не Чернобог… Теперь наша очередь остановить Воссоединение!")
        self.assertFalse(any(ap.INLINE.findall(x) for x in record["dialogues"].values()))

    def test_prior_54_records_unchanged(self):
        before=load("story/story_main_selection_ru_v059.json")
        after=load("story/story_main_selection_ru_v060.json")
        self.assertEqual((len(before["files"]),len(after["files"])),(54,55))
        self.assertEqual(sum(v["dialogue_count"] for v in after["files"].values()),3189)
        self.assertEqual(set(after["files"])-set(before["files"]),{REL})
        for path,record in before["files"].items():
            self.assertEqual(record,after["files"][path])
        self.assertEqual(after["files"][REL],load(NEW)["files"][REL])

    def test_preview_preserves_every_non_dialogue_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            doc=copy.deepcopy(load(NEW))
            rows=["[HEADER(key=\"title_test\")]\n","[Background(image=\"keep\")]\n","[PlayMusic(key=\"$loading_loop\")]\n"]
            names=["Amiya","Ch'en","Hoshiguma","Franka","Liskarm"]
            for i in range(56):
                rows.append('[Character(name="keep")]\n')
                rows.append('[name="'+names[i%len(names)]+'"] English source line '+str(i+1)+'\n')
                if i%11==0:rows.append("[Delay(time=0.1)]\n")
            rows+=["[Dialog]\n","[Blocker(block=true)]\n","[Image]\n"]
            original="".join(rows).encode("utf-8")
            for lang in ("cn","en"):
                path=root/"source"/lang/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(original)
                doc["files"][REL][lang+"_git_blob_sha1"]=ap.git_blob_sha1(original)
            draft=root/"draft.json"
            draft.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            out=ap.build(root/"source",root/"preview",draft)
            self.assertEqual(out["lines_total"],56)
            old=original.decode("utf-8").splitlines()
            new=(root/"preview"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(old),len(new))
            for a,b in zip(old,new):
                if not ap.SPEAKER.search(a):self.assertEqual(a,b)
            self.assertIn('[name="Франка"]',"\n".join(new))
            self.assertIn('[name="Лискарм"]',"\n".join(new))
            self.assertIn("Теперь наша очередь остановить Воссоединение!",new[-4])
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"rejected",ROOT/NEW)
            self.assertFalse((root/"rejected").exists())

    def test_chronology_index_qa_and_audit(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v060.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),12)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows),812)
        self.assertEqual(rows[-2]["source_filename"],"level_main_03-06_beg.txt")
        self.assertEqual((rows[-2]["ru_status"],rows[-2]["dialogues_ru_count"]),("first_draft_complete","56"))
        self.assertEqual((rows[-2]["cn_git_blob_sha1"],rows[-2]["en_git_blob_sha1"]),(CN_SHA,EN_SHA))
        self.assertEqual((rows[-1]["source_filename"],rows[-1]["ru_status"]),("level_main_03-06_end.txt","not_translated"))
        m=load("chronology/CHRONOLOGY_MANIFEST_v060.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(55,3189))
        self.assertEqual((m["translation_integrity"]["main_story_chapter_3_files"],m["translation_integrity"]["main_story_chapter_3_named_ru_lines"]),(11,812))
        self.assertEqual(m["translation_integrity"]["main_story_chapter_3_stages_completed"],5)
        self.assertEqual(m["next_file"],"obt/main/level_main_03-06_end.txt")
        qa=load("reports/QA_MAIN_STORY_v060.json")
        self.assertEqual((qa["new_named_ru"],qa["total_named_ru"]),(56,3189))
        self.assertFalse(qa["in_game_test"])
        audit=load("reports/CHAPTER_3_STAGE_3-6_BEFORE_SOURCE_AUDIT_v060.json")
        self.assertTrue(audit["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertEqual((audit["alignment"]["cn_named"],audit["alignment"]["en_named"]),(56,56))
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"],audit["sources"]["en"]["git_blob_sha1"]),(CN_SHA,EN_SHA))
        self.assertEqual(audit["alignment"]["cn_decision_commands"],0)
        self.assertEqual(audit["alignment"]["en_decision_commands"],0)

if __name__=="__main__":unittest.main()
