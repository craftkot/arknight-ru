# coding: utf-8
"""Chapter 3-3 before battle: 51 named lines and regression safety checks."""
import copy,csv,json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-03_beg.txt"
def load(path):
    return json.loads((ROOT/path).read_text("utf-8"))
class Chapter3Stage33BeforeV054(unittest.TestCase):
    def test_all_51_named_and_pinned_source_revisions(self):
        d=load("story/story_chapter_3_stage_3-3_before_ru_v054.json")
        self.assertEqual(d["version"],"v0.54")
        self.assertEqual(set(d["files"]),{REL})
        x=d["files"][REL]
        self.assertEqual(x["dialogue_count"],51)
        self.assertEqual(set(x["dialogues"]),set(map(str,range(1,52))))
        self.assertEqual(x["cn_git_blob_sha1"],"d85c4f4ad8e753c8c9a2ac57acae1398dd3c620a")
        self.assertEqual(x["en_git_blob_sha1"],"3b828496ac7fc1fb6bfeb95456c15679314160a7")
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        for t in x["dialogues"].values():
            self.assertTrue(t.strip())
            self.assertFalse(any(z in t for z in "\r\n\t"))
            self.assertEqual(ap.quoted_tokens(t),[])
        self.assertEqual(x["dialogues"]["22"],"Ой, извини.")
    def test_old_48_scenes_preserved_exactly(self):
        old=load("story/story_main_selection_ru_v053.json")
        new=load("story/story_main_selection_ru_v054.json")
        fresh=load("story/story_chapter_3_stage_3-3_before_ru_v054.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(48,49))
        self.assertEqual(sum(v["dialogue_count"] for v in old["files"].values()),2659)
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()),2710)
        for path,record in old["files"].items():
            self.assertEqual(record,new["files"][path])
        self.assertEqual(new["files"][REL],fresh["files"][REL])
    def test_safe_preview_does_not_modify_control_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            doc=copy.deepcopy(load("story/story_chapter_3_stage_3-3_before_ru_v054.json"))
            for lang in ("en","cn"):
                data=("[Background(image=\"unchanged\")]\r\n"+
                      "".join(('[name="'+("Texas" if lang=="en" else "德克萨斯")+'"] '+("Hello" if lang=="en" else "你好")+'\r\n[Delay(time=0.1)]\r\n') for _ in range(51))).encode("utf-8")
                f=root/"source"/lang/REL
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(data)
                doc["files"][REL][lang+"_git_blob_sha1"]=ap.git_blob_sha1(data)
            p=root/"draft.json"
            p.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            report=ap.build(root/"source",root/"preview",p)
            self.assertEqual(report["lines_total"],51)
            orig=(root/"source"/"en"/REL).read_text("utf-8").splitlines()
            trans=(root/"preview"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(orig),len(trans))
            self.assertEqual([s for s in orig if not ap.SPEAKER.search(s)],
                             [s for s in trans if not ap.SPEAKER.search(s)])
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"rejected",ROOT/"story/story_chapter_3_stage_3-3_before_ru_v054.json")
            self.assertFalse((root/"rejected").exists())
    def test_manifest_and_index(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v054.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),6)
        self.assertEqual([x["ru_status"] for x in rows[-2:]],["first_draft_complete","not_translated"])
        self.assertEqual(sum(int(x["dialogues_ru_count"]) for x in rows),333)
        m=load("chronology/CHRONOLOGY_MANIFEST_v054.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(49,2710))
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],13)
        self.assertEqual(m["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(m["next_file"],"obt/main/level_main_03-03_end.txt")
        qa=load("reports/QA_MAIN_STORY_v054.json")
        self.assertEqual((qa["new_dialogues"],qa["prior_dialogues"],qa["total_dialogues"]),(51,2659,2710))
        self.assertFalse(qa["game_tested"])
if __name__=="__main__":
    unittest.main()
