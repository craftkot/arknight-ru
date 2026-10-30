# coding: utf-8
"""v0.59: full first draft of 3-5 after battle, CN-primary, 114 aligned lines."""
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

REL="obt/main/level_main_03-05_end.txt"
NEW="story/story_chapter_3_stage_3-5_after_ru_v059.json"
def load(path):return json.loads((ROOT/path).read_text("utf-8"))

class Chapter3Stage35AfterV059(unittest.TestCase):
    def test_complete_source_pinned_draft(self):
        record=load(NEW)["files"][REL]
        self.assertEqual(record["dialogue_count"],114)
        self.assertEqual(set(record["dialogues"]),{str(i) for i in range(1,115)})
        self.assertEqual(record["cn_git_blob_sha1"],"15eff5f2e4a435fdd756c55b9b9d75962b3e9a6f")
        self.assertEqual(record["en_git_blob_sha1"],"796aeb10553a12b17f5f2bf5b43af74bf7dd697a")
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        for item in record["dialogues"].values():
            self.assertTrue(isinstance(item,str) and item.strip())
            self.assertFalse(any(ch in item for ch in "\r\n\t"))
        self.assertEqual(record["dialogues"]["110"],"Воссоединение — это заражённые…")
        self.assertEqual(record["dialogues"]["111"],"Они ведь тоже заражённые…")
        self.assertEqual(record["dialogues"]["27"],"А вот это уже не для Амии, а для всех вас.")
        self.assertEqual(record["dialogues"]["84"],"Не ты причиняла боль невинным людям! Ты в этом не виновата!")
        self.assertEqual(set(ap.SPEAKER_RU)&{"Girl's Voice","Young Man's Voice","Boy's Voice"},
                         {"Girl's Voice","Young Man's Voice","Boy's Voice"})
    def test_prior_53_records_unchanged(self):
        before=load("story/story_main_selection_ru_v058.json")
        after=load("story/story_main_selection_ru_v059.json")
        self.assertEqual((len(before["files"]),len(after["files"])),(53,54))
        self.assertEqual(sum(v["dialogue_count"] for v in after["files"].values()),3133)
        self.assertEqual(set(after["files"])-set(before["files"]),{REL})
        for path,record in before["files"].items():
            self.assertEqual(record,after["files"][path])
        self.assertEqual(after["files"][REL],load(NEW)["files"][REL])
    def test_preview_preserves_control_commands_and_plain_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            doc=copy.deepcopy(load(NEW))
            rows=["[Background(image=\"keep\")]\n","————\n"]
            names=["Amiya","Ch'en","Hoshiguma","W","Misha","Girl's Voice","Young Man's Voice","Boy's Voice"]
            for i in range(114):
                rows.append('[name="'+names[i%len(names)]+'"] English source line '+str(i+1)+'\n')
                if i%10==0:rows.append('[Delay(time=0.1)]\n')
            original="".join(rows).encode("utf-8")
            for lang in ("cn","en"):
                path=root/"source"/lang/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(original)
                doc["files"][REL][lang+"_git_blob_sha1"]=ap.git_blob_sha1(original)
            draft=root/"draft.json"
            draft.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            out=ap.build(root/"source",root/"preview",draft)
            self.assertEqual(out["lines_total"],114)
            old=original.decode("utf-8").splitlines()
            new=(root/"preview"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(old),len(new))
            for a,b in zip(old,new):
                if ap.SPEAKER.search(a):continue
                self.assertEqual(a,b)
            self.assertIn('[name="Голос девушки"]',"\n".join(new))
            self.assertIn('[name="Голос юноши"]',"\n".join(new))
            self.assertIn('[name="Голос мальчика"]',"\n".join(new))
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"rejected",ROOT/NEW)
            self.assertFalse((root/"rejected").exists())
    def test_index_chronology_qa_and_audit(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v059.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),11)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows),756)
        self.assertEqual(rows[-2]["ru_status"],"first_draft_complete")
        self.assertEqual(rows[-2]["dialogues_ru_count"],"114")
        self.assertEqual(rows[-1]["source_filename"],"level_main_03-06_beg.txt")
        self.assertEqual(rows[-1]["ru_status"],"not_translated")
        m=load("chronology/CHRONOLOGY_MANIFEST_v059.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(54,3133))
        self.assertEqual((m["translation_integrity"]["main_story_chapter_3_files"],m["translation_integrity"]["main_story_chapter_3_named_ru_lines"]),(10,756))
        self.assertEqual(m["translation_integrity"]["main_story_chapter_3_stages_completed"],5)
        self.assertEqual(m["next_file"],"obt/main/level_main_03-06_beg.txt")
        qa=load("reports/QA_MAIN_STORY_v059.json")
        self.assertEqual((qa["new_named_ru"],qa["total_named_ru"]),(114,3133))
        self.assertFalse(qa["in_game_test"])
        audit=load("reports/CHAPTER_3_STAGE_3-5_AFTER_SOURCE_AUDIT_v059.json")
        self.assertTrue(audit["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertEqual(audit["alignment"]["cn_named"],114)
        self.assertEqual(audit["alignment"]["unlabeled_line_position"],75)
if __name__=="__main__":unittest.main()
