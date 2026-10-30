# coding: utf-8
"""Chapter 3-4 before battle: 79 numbered dialogues and source-safe preview."""
import copy,csv,json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-04_beg.txt"
def load(p):
    return json.loads((ROOT/p).read_text("utf-8"))
class Chapter3Stage34BeforeV056(unittest.TestCase):
    def test_full_79_and_hashes(self):
        d=load("story/story_chapter_3_stage_3-4_before_ru_v056.json")
        self.assertEqual(d["version"],"v0.56")
        self.assertEqual(set(d["files"]),{REL})
        x=d["files"][REL]
        self.assertEqual(x["dialogue_count"],79)
        self.assertEqual(set(x["dialogues"]),set(map(str,range(1,80))))
        self.assertEqual(x["cn_git_blob_sha1"],"68357fc231568edc590d4e893a946a112a06e447")
        self.assertEqual(x["en_git_blob_sha1"],"396f62eb27e5004a7369898366f40d54d916a092")
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        for t in x["dialogues"].values():
            self.assertTrue(t.strip())
            self.assertFalse(any(z in t for z in "\r\n\t"))
            self.assertEqual(ap.quoted_tokens(t),[])
        self.assertIn("фланга",x["dialogues"]["42"])
        self.assertIn("клинок",x["dialogues"]["44"])
    def test_prior_50_records_unchanged(self):
        old=load("story/story_main_selection_ru_v055.json")
        new=load("story/story_main_selection_ru_v056.json")
        fresh=load("story/story_chapter_3_stage_3-4_before_ru_v056.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(50,51))
        self.assertEqual(sum(v["dialogue_count"] for v in old["files"].values()),2802)
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()),2881)
        for path,record in old["files"].items():
            self.assertEqual(record,new["files"][path])
        self.assertEqual(new["files"][REL],fresh["files"][REL])
    def test_commands_preserved_and_sha_pinning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            doc=copy.deepcopy(load("story/story_chapter_3_stage_3-4_before_ru_v056.json"))
            for lang in ("en","cn"):
                data=('[Background(image="keep")]\r\n'+''.join('[name="Texas"] Hello\r\n[Delay(time=0.1)]\r\n' for _ in range(79))).encode("utf-8")
                p=root/"source"/lang/REL
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(data)
                doc["files"][REL][lang+"_git_blob_sha1"]=ap.git_blob_sha1(data)
            p=root/"draft.json"
            p.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            result=ap.build(root/"source",root/"preview",p)
            self.assertEqual(result["lines_total"],79)
            orig=(root/"source"/"en"/REL).read_text("utf-8").splitlines()
            trans=(root/"preview"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(orig),len(trans))
            self.assertEqual([s for s in orig if not ap.SPEAKER.search(s)],
                             [s for s in trans if not ap.SPEAKER.search(s)])
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"rejected",ROOT/"story/story_chapter_3_stage_3-4_before_ru_v056.json")
            self.assertFalse((root/"rejected").exists())
    def test_index_manifest_qa(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v056.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),8)
        self.assertTrue(all(r["ru_status"]=="first_draft_complete" for r in rows[:7]))
        self.assertEqual(rows[-1]["ru_status"],"not_translated")
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows),504)
        m=load("chronology/CHRONOLOGY_MANIFEST_v056.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(51,2881))
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],13)
        self.assertEqual(m["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(m["next_file"],"obt/main/level_main_03-04_end.txt")
        qa=load("reports/QA_MAIN_STORY_v056.json")
        self.assertEqual((qa["new_named_ru"],qa["prior_named_ru"],qa["total_named_ru"]),(79,2802,2881))
        self.assertFalse(qa["in_game_test"])
        a=load("reports/CHAPTER_3_STAGE_3-4_BEFORE_SOURCE_AUDIT_v056.json")
        self.assertEqual(a["alignment"]["cn_named"],79)
        self.assertTrue(a["alignment"]["markup_tokens_preserved"])
if __name__=="__main__":
    unittest.main()
