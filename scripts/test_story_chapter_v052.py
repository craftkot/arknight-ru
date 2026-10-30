# coding: utf-8
"""Chapter 3 stage 3-2 before-battle first draft safety regression tests."""
import copy
import csv
import json
import pathlib
import re
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-02_beg.txt"
def load(path):
    return json.loads((ROOT/path).read_text("utf-8"))
class Chapter3BeforeV052(unittest.TestCase):
    def test_sources_ordinals_and_speaker(self):
        doc=load("story/story_chapter_3_stage_3-2_before_ru_v052.json")
        self.assertEqual(set(doc["files"]),{REL})
        spec=doc["files"][REL]
        self.assertEqual(spec["dialogue_count"],37)
        self.assertEqual(set(spec["dialogues"]),set(map(str,range(1,38))))
        self.assertEqual(spec["cn_git_blob_sha1"],"e8df9153f936ed913c8244435857c5318adb5fd5")
        self.assertEqual(spec["en_git_blob_sha1"],"dead4546db26bd1362dc10e680a1e45387493bc9")
        self.assertEqual(ap.SPEAKER_RU["Hoshiguma"],"Хосигума")
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        self.assertIn("Хосигума",spec["dialogues"]["1"])
        self.assertTrue(all(x.strip() and not any(c in x for c in "\r\n\t") and not ap.quoted_tokens(x) for x in spec["dialogues"].values()))

    def test_previous_46_story_scripts_unchanged(self):
        old=load("story/story_main_selection_ru_v051.json")
        now=load("story/story_main_selection_ru_v052.json")
        part=load("story/story_chapter_3_stage_3-2_before_ru_v052.json")
        self.assertEqual(len(old["files"]),46)
        self.assertEqual(len(now["files"]),47)
        self.assertEqual(sum(v["dialogue_count"] for v in now["files"].values()),2539)
        for k,v in old["files"].items():self.assertEqual(now["files"][k],v)
        self.assertEqual(now["files"][REL],part["files"][REL])

    def test_local_safe_preview_and_revision_guard(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            doc=copy.deepcopy(load("story/story_chapter_3_stage_3-2_before_ru_v052.json"))
            d=doc["files"][REL]
            for lang in ("cn","en"):
                role="星熊" if lang=="cn" else "Hoshiguma"
                lines=['[Background(image="unchanged")]', '[PlayMusic(key="unchanged")]']
                lines+=['[name="'+role+'"] Test' if lang=="en" else '[name="'+role+'"] 测试' for _ in range(37)]
                lines+=['[Delay(time=1)]']
                data=("\n".join(lines)+"\n").encode("utf-8")
                path=root/"sources"/lang/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(data)
                d[lang+"_git_blob_sha1"]=ap.git_blob_sha1(data)
            cfg=root/"draft.json"
            cfg.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            report=ap.build(root/"sources",root/"out",cfg)
            self.assertEqual(report["lines_total"],37)
            en=(root/"sources"/"en"/REL).read_text("utf-8").splitlines()
            ru=(root/"out"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(en),len(ru))
            self.assertEqual(en[:2],ru[:2])
            self.assertEqual(en[-1],ru[-1])
            self.assertIn('[name="Хосигума"]',ru[2])
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"sources",root/"bad",ROOT/"story/story_chapter_3_stage_3-2_before_ru_v052.json")
            self.assertFalse((root/"bad").exists())

    def test_manifest_qa_and_next_scene(self):
        index=ROOT/"story/CHAPTER_3_INDEX_v052.tsv"
        with index.open(encoding="utf-8") as f:rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual([v["ru_status"] for v in rows],["first_draft_complete"]*3+["not_translated"])
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows),162)
        qa=load("reports/QA_MAIN_STORY_v052.json")
        man=load("chronology/CHRONOLOGY_MANIFEST_v052.json")
        self.assertEqual((qa["new_ru_dialogues"],qa["total_story_dialogues"]),(37,2539))
        self.assertEqual(man["translation_integrity"]["main_story_files"],47)
        self.assertEqual(man["translation_integrity"]["main_story_named_ru_lines"],2539)
        self.assertEqual(man["next_file"],"obt/main/level_main_03-02_end.txt")
        self.assertEqual(man["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(man["translation_integrity"]["darknights_completed_files"],13)
if __name__=="__main__":
    unittest.main()
