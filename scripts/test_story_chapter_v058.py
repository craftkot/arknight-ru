# coding: utf-8
"""v0.58: 3-5 before battle; 83 dialogues and 5 translated decision options."""
import copy,csv,json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-05_beg.txt"
def load(p): return json.loads((ROOT/p).read_text("utf-8"))
class Chapter3Stage35BeforeV058(unittest.TestCase):
    def test_full_draft_and_sources(self):
        x=load("story/story_chapter_3_stage_3-5_before_ru_v058.json")["files"][REL]
        self.assertEqual(x["dialogue_count"],83)
        self.assertEqual(set(x["dialogues"]),set(map(str,range(1,84))))
        self.assertEqual(x["cn_git_blob_sha1"],"d4e655e1044c228cf7cd0e6a6102819416bbf68c")
        self.assertEqual(x["en_git_blob_sha1"],"aab530ba1f1af9bfa2c942e88dd5811ce6dc3994")
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        self.assertEqual([len(x["decisions"][str(i)]) for i in (1,2,3)],[1,3,1])
        for s in x["dialogues"].values():
            self.assertTrue(s.strip())
            self.assertFalse(any(c in s for c in "\r\n\t"))
        self.assertEqual(ap.quoted_tokens(x["dialogues"]["1"]),["{@nickname}"])
        self.assertEqual(ap.quoted_tokens(x["dialogues"]["31"]),["{@nickname}"])
        self.assertIn("слабая",x["dialogues"]["34"])
    def test_unchanged_old_records(self):
        old=load("story/story_main_selection_ru_v057.json")
        new=load("story/story_main_selection_ru_v058.json")
        fresh=load("story/story_chapter_3_stage_3-5_before_ru_v058.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(52,53))
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()),3019)
        for path,record in old["files"].items():
            self.assertEqual(record,new["files"][path])
        self.assertEqual(new["files"][REL],fresh["files"][REL])
    def test_preview_preserves_branch_ids_and_nontext_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            doc=copy.deepcopy(load("story/story_chapter_3_stage_3-5_before_ru_v058.json"))
            fake='[Background(image="keep")]\r\n'
            fake+='[Decision(options="A", values="1")]\r\n'
            fake+='[Predicate(references="1")]\r\n'
            fake+='[Decision(options="B;C;D", values="1;2;3")]\r\n'
            fake+='[Predicate(references="1;2;3")]\r\n'
            fake+='[Decision(options="E", values="1")]\r\n'
            fake+=''.join('[name="Amiya"] Hello'+(' {@nickname}' if i in (1,11,14,31) else '')+'\r\n[Delay(time=0.1)]\r\n' for i in range(1,84))
            data=fake.encode("utf-8")
            for lang in ("cn","en"):
                f=root/"source"/lang/REL
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(data)
                doc["files"][REL][lang+"_git_blob_sha1"]=ap.git_blob_sha1(data)
            f=root/"draft.json"
            f.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            result=ap.build(root/"source",root/"preview",f)
            self.assertEqual(result["lines_total"],83)
            original=(root/"source"/"en"/REL).read_text("utf-8").splitlines()
            translated=(root/"preview"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(original),len(translated))
            for a,b in zip(original,translated):
                if ap.SPEAKER.search(a): continue
                if ap.DECISION.search(a):
                    ma,mb=ap.DECISION.search(a),ap.DECISION.search(b)
                    self.assertEqual(a[:ma.start(2)]+a[ma.end(2):],b[:mb.start(2)]+b[mb.end(2):])
                else: self.assertEqual(a,b)
            self.assertIn("Ты боишься?",'\n'.join(translated))
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"rejected",ROOT/"story/story_chapter_3_stage_3-5_before_ru_v058.json")
            self.assertFalse((root/"rejected").exists())
    def test_metadata(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v058.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),10)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows),642)
        self.assertEqual(rows[-2]["ru_status"],"first_draft_complete")
        self.assertEqual(rows[-1]["ru_status"],"not_translated")
        m=load("chronology/CHRONOLOGY_MANIFEST_v058.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(53,3019))
        self.assertEqual(m["next_file"],"obt/main/level_main_03-05_end.txt")
        qa=load("reports/QA_MAIN_STORY_v058.json")
        self.assertEqual((qa["new_named_ru"],qa["new_choice_options_ru"]),(83,5))
        self.assertFalse(qa["in_game_test"])
        audit=load("reports/CHAPTER_3_STAGE_3-5_BEFORE_SOURCE_AUDIT_v058.json")
        self.assertEqual(audit["alignment"]["decision_option_counts"],[1,3,1])
if __name__=="__main__":unittest.main()
