# coding: utf-8
"""Chapter 3-4 after battle: complete 55-line source-pinned Russian draft."""
import copy,csv,json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-04_end.txt"
def load(p): return json.loads((ROOT/p).read_text("utf-8"))
class Chapter3Stage34AfterV057(unittest.TestCase):
    def test_full_55_and_pinned_sources(self):
        d=load("story/story_chapter_3_stage_3-4_after_ru_v057.json")
        self.assertEqual(d["version"],"v0.57")
        self.assertEqual(set(d["files"]),{REL})
        x=d["files"][REL]
        self.assertEqual(x["dialogue_count"],55)
        self.assertEqual(set(x["dialogues"]),set(map(str,range(1,56))))
        self.assertEqual(x["cn_git_blob_sha1"],"25ee6b4823b7622740d1bd268c1870fc0ea603b4")
        self.assertEqual(x["en_git_blob_sha1"],"1ef401ec922d87566581d5d901c1146a2676a245")
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        for line in x["dialogues"].values():
            self.assertTrue(line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
            self.assertEqual(ap.quoted_tokens(line),[])
        self.assertIn("Хання",x["dialogues"]["31"])
        self.assertIn("сила",x["dialogues"]["46"])
    def test_previous_51_files_unchanged(self):
        old=load("story/story_main_selection_ru_v056.json")
        new=load("story/story_main_selection_ru_v057.json")
        added=load("story/story_chapter_3_stage_3-4_after_ru_v057.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(51,52))
        self.assertEqual(sum(v["dialogue_count"] for v in old["files"].values()),2881)
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()),2936)
        for path,record in old["files"].items():
            self.assertEqual(record,new["files"][path])
        self.assertEqual(new["files"][REL],added["files"][REL])
    def test_preview_commands_unchanged_and_revision_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            d=copy.deepcopy(load("story/story_chapter_3_stage_3-4_after_ru_v057.json"))
            for lang in ("cn","en"):
                data=('[Background(image="keep")]\r\n'+''.join('[name="Hoshiguma"] Original\r\n[Delay(time=0.1)]\r\n' for _ in range(55))).encode("utf-8")
                f=root/"source"/lang/REL
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(data)
                d["files"][REL][lang+"_git_blob_sha1"]=ap.git_blob_sha1(data)
            f=root/"draft.json"
            f.write_text(json.dumps(d,ensure_ascii=False),"utf-8")
            result=ap.build(root/"source",root/"preview",f)
            self.assertEqual(result["lines_total"],55)
            original=(root/"source"/"en"/REL).read_text("utf-8").splitlines()
            translated=(root/"preview"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(original),len(translated))
            self.assertEqual([s for s in original if not ap.SPEAKER.search(s)],[s for s in translated if not ap.SPEAKER.search(s)])
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"rejected",ROOT/"story/story_chapter_3_stage_3-4_after_ru_v057.json")
            self.assertFalse((root/"rejected").exists())
    def test_index_manifest_and_audit(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v057.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),9)
        self.assertTrue(all(r["ru_status"]=="first_draft_complete" for r in rows[:8]))
        self.assertEqual(rows[-1]["ru_status"],"not_translated")
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows),559)
        m=load("chronology/CHRONOLOGY_MANIFEST_v057.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(52,2936))
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],13)
        self.assertEqual(m["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(m["next_file"],"obt/main/level_main_03-05_beg.txt")
        qa=load("reports/QA_MAIN_STORY_v057.json")
        self.assertEqual((qa["new_named_ru"],qa["prior_named_ru"],qa["total_named_ru"]),(55,2881,2936))
        self.assertEqual(qa["stage_3_4_total_named"],134)
        self.assertFalse(qa["in_game_test"])
        audit=load("reports/CHAPTER_3_STAGE_3-4_AFTER_SOURCE_AUDIT_v057.json")
        self.assertEqual((audit["alignment"]["cn_named"],audit["alignment"]["en_named"]),(55,55))
        self.assertTrue(audit["alignment"]["markup_tokens_preserved"])
if __name__=="__main__":
    unittest.main()
