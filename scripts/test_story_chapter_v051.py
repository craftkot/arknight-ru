# coding: utf-8
"""Regression tests for main story chapter 3, 3-1 before/after first draft."""
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

def get(path):
    return json.loads((ROOT/path).read_text("utf-8"))

STAGES=(
    "obt/main/level_main_03-01_beg.txt",
    "obt/main/level_main_03-01_end.txt",
)
SOURCES={
    STAGES[0]:("1386d716004d57d6d956ef09d585223a31aba676","209c67832505696d425489ba3519273a0ed13881",75),
    STAGES[1]:("1a68fd7bd2bfa419086ed67dffd1f5a413412e82","4b91c18980615f42d086bc6f138fb4976bde6750",50),
}

class MainStoryV051(unittest.TestCase):
    def setUp(self):
        self.stage=get("story/story_chapter_3_stage_3-1_ru_v051.json")
        self.full=get("story/story_main_selection_ru_v051.json")
        self.previous=get("story/story_main_selection_ru_v025.json")

    def test_two_finished_scripts_and_correct_source_hashes(self):
        self.assertEqual(self.stage["version"],"v0.51")
        self.assertEqual(set(self.stage["files"]),set(STAGES))
        for rel,(cn,en,count) in SOURCES.items():
            scene=self.stage["files"][rel]
            self.assertEqual((scene["cn_git_blob_sha1"],scene["en_git_blob_sha1"]),(cn,en))
            self.assertEqual(scene["dialogue_count"],count)
            self.assertEqual(set(scene["dialogues"]),set(map(str,range(1,count+1))))
            for value in scene["dialogues"].values():
                self.assertIsInstance(value,str)
                self.assertTrue(value.strip())
                self.assertFalse(any(x in value for x in "\r\n\t"))
                self.assertEqual(ap.quoted_tokens(value),[])

    def test_previous_44_scripts_preserved(self):
        self.assertEqual(len(self.previous["files"]),44)
        self.assertEqual(sum(v["dialogue_count"] for v in self.previous["files"].values()),2377)
        self.assertEqual(len(self.full["files"]),46)
        self.assertEqual(sum(v["dialogue_count"] for v in self.full["files"].values()),2502)
        for path,value in self.previous["files"].items():
            self.assertEqual(self.full["files"][path],value)
        for path in STAGES:
            self.assertEqual(self.full["files"][path],self.stage["files"][path])
            self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,path))
        self.assertEqual(ap.SPEAKER_RU["Reunion Suspect"],"Подозреваемый в связях с Воссоединением")

    def test_synthetic_patch_no_control_changes(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            doc=copy.deepcopy(self.stage)
            for rel in STAGES:
                spec=doc["files"][rel]
                lines_en=['[HEADER(key="title_test", is_skippable=true)] source title',
                          '[Background(image="bg_wild_m")]', '[PlayMusic(key="$mist_loop")]']
                lines_cn=['[HEADER(key="title_test", is_skippable=true)] 原文',
                          '[Background(image="bg_wild_m")]', '[PlayMusic(key="$mist_loop")]']
                for i in range(1,spec["dialogue_count"]+1):
                    role=("Reunion Suspect" if i%7==0 else "Ch'en" if i%2==0 else "Amiya")
                    lines_en+=['[name="'+role+'"]   Source '+str(i),'[Delay(time=1)]']
                    lines_cn+=['[name="陈"]   原文','[Delay(time=1)]']
                for lang,lines in (("cn",lines_cn),("en",lines_en)):
                    raw=("\r\n".join(lines)+"\r\n").encode("utf-8")
                    target=root/"input"/lang/rel
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(raw)
                    spec[lang+"_git_blob_sha1"]=ap.git_blob_sha1(raw)
            translation=root/"stage.json"
            translation.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            output=root/"preview"
            result=ap.build(root/"input",output,translation)
            self.assertEqual((len(result["files"]),result["lines_total"]),(2,125))
            for rel in STAGES:
                en=(root/"input"/"en"/rel).read_text("utf-8").splitlines()
                ru=(output/"ru"/rel).read_text("utf-8").splitlines()
                self.assertEqual(len(en),len(ru))
                self.assertEqual([x for x in en if x.startswith("[Delay")],[x for x in ru if x.startswith("[Delay")])
                self.assertEqual([x for x in en if x.startswith("[Background")],[x for x in ru if x.startswith("[Background")])
                self.assertEqual([x for x in en if x.startswith("[PlayMusic")],[x for x in ru if x.startswith("[PlayMusic")])
                self.assertEqual(en[:3],ru[:3])
                self.assertTrue(any("Подозреваемый в связях с Воссоединением" in x for x in ru))

    def test_changed_source_refused_and_no_output(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            for path in STAGES:
                for lang in ("cn","en"):
                    f=root/"source"/lang/path
                    f.parent.mkdir(parents=True,exist_ok=True)
                    f.write_text('[name="Amiya"] changed\n',"utf-8")
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"result",ROOT/"story/story_chapter_3_stage_3-1_ru_v051.json")
            self.assertFalse((root/"result").exists())

    def test_index_qa_chronology(self):
        index=ROOT/"story/CHAPTER_3_INDEX_v051.tsv"
        with index.open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),3)
        self.assertEqual([row["ru_status"] for row in rows],["first_draft_complete","first_draft_complete","not_translated"])
        self.assertEqual(sum(int(row["dialogues_ru_count"]) for row in rows),125)
        manifest=get("chronology/CHRONOLOGY_MANIFEST_v051.json")
        audit=get("reports/CHAPTER_3_STAGE_3-1_AUDIT_v051.json")
        qa=get("reports/QA_MAIN_STORY_v051.json")
        self.assertEqual(manifest["translation_integrity"]["main_story_named_ru_lines"],2502)
        self.assertEqual(manifest["translation_integrity"]["main_story_files"],46)
        self.assertEqual(manifest["translation_integrity"]["main_story_chapter_3_files"],2)
        self.assertEqual(manifest["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(manifest["translation_integrity"]["darknights_completed_files"],13)
        self.assertEqual(manifest["next_file"],"obt/main/level_main_03-02_beg.txt")
        self.assertEqual(audit["translation"]["new_dialogues"],125)
        self.assertFalse(audit["structure"]["semantic_alignment_confirmed"])
        self.assertEqual((qa["new_named_before"],qa["new_named_after"],qa["main_story_total_named"]),(75,50,2502))
        readme=(ROOT/"README.md").read_text("utf-8")
        self.assertIn("story/story_chapter_3_stage_3-1_ru_v051.json",readme)
        self.assertIn("story/story_main_selection_ru_v051.json",readme)

if __name__=="__main__":
    unittest.main()
