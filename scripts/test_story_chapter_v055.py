# coding: utf-8
"""Chapter 3-3 after battle: 92 dialogue lines and safe local preview regression."""
import copy,csv,json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-03_end.txt"
def load(path):
    return json.loads((ROOT/path).read_text("utf-8"))
class Chapter3Stage33AfterV055(unittest.TestCase):
    def test_all_92_and_source_shas(self):
        d=load("story/story_chapter_3_stage_3-3_after_ru_v055.json")
        self.assertEqual(d["version"],"v0.55")
        self.assertEqual(set(d["files"]),{REL})
        x=d["files"][REL]
        self.assertEqual(x["dialogue_count"],92)
        self.assertEqual(set(x["dialogues"]),set(map(str,range(1,93))))
        self.assertEqual(x["cn_git_blob_sha1"],"c8f7a5f143f3793a573cc3783e04496658fe126e")
        self.assertEqual(x["en_git_blob_sha1"],"f3d5e32725a2b5183cd0715b1ff68b943e8709ac")
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        for k,t in x["dialogues"].items():
            self.assertTrue(t.strip())
            self.assertFalse(any(z in t for z in "\r\n\t"))
            self.assertEqual(ap.quoted_tokens(t),["{@nickname}"] if k=="77" else [])
        self.assertIn("рукоять",x["dialogues"]["7"])
        self.assertIn("Искусства",x["dialogues"]["8"])
        self.assertIn("Доктор {@nickname}",x["dialogues"]["77"])
    def test_preserve_prior_49_entries_exactly(self):
        old=load("story/story_main_selection_ru_v054.json")
        new=load("story/story_main_selection_ru_v055.json")
        added=load("story/story_chapter_3_stage_3-3_after_ru_v055.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(49,50))
        self.assertEqual(sum(v["dialogue_count"] for v in old["files"].values()),2710)
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()),2802)
        for path,record in old["files"].items():
            self.assertEqual(record,new["files"][path])
        self.assertEqual(new["files"][REL],added["files"][REL])
    def test_preview_preserves_commands_and_rejects_wrong_source_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            doc=copy.deepcopy(load("story/story_chapter_3_stage_3-3_after_ru_v055.json"))
            for lang in ("en","cn"):
                lines=['[Background(image="keep")]', '[PlayMusic(key="$keep")]']
                for i in range(1,93):
                    speaker="W" if lang=="en" else "W"
                    text=("Dr. {@nickname}" if lang=="en" else "Dr.{@nickname}") if i==77 else ("Original" if lang=="en" else "原文")
                    lines.extend(['[name="'+speaker+'"] '+text,'[Delay(time=0.1)]'])
                data=("\r\n".join(lines)+"\r\n").encode("utf-8")
                f=root/"source"/lang/REL
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(data)
                doc["files"][REL][lang+"_git_blob_sha1"]=ap.git_blob_sha1(data)
            p=root/"draft.json"
            p.write_text(json.dumps(doc,ensure_ascii=False),"utf-8")
            report=ap.build(root/"source",root/"preview",p)
            self.assertEqual(report["lines_total"],92)
            orig=(root/"source"/"en"/REL).read_text("utf-8").splitlines()
            trans=(root/"preview"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(orig),len(trans))
            self.assertEqual([s for s in orig if not ap.SPEAKER.search(s)],
                             [s for s in trans if not ap.SPEAKER.search(s)])
            self.assertIn("{@nickname}",trans[2+2*(77-1)])
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"source",root/"rejected",ROOT/"story/story_chapter_3_stage_3-3_after_ru_v055.json")
            self.assertFalse((root/"rejected").exists())
    def test_index_manifest_audit(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v055.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),7)
        self.assertTrue(all(row["ru_status"]=="first_draft_complete" for row in rows[:6]))
        self.assertEqual(rows[6]["ru_status"],"not_translated")
        self.assertEqual(sum(int(row["dialogues_ru_count"]) for row in rows),425)
        m=load("chronology/CHRONOLOGY_MANIFEST_v055.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(50,2802))
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],13)
        self.assertEqual(m["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(m["next_file"],"obt/main/level_main_03-04_beg.txt")
        qa=load("reports/QA_MAIN_STORY_v055.json")
        self.assertEqual((qa["new_named_ru"],qa["prior_named_ru"],qa["total_named_ru"]),(92,2710,2802))
        self.assertEqual(qa["stage_3_3_total_named"],143)
        self.assertFalse(qa["in_game_test"])
        audit=load("reports/CHAPTER_3_STAGE_3-3_AFTER_SOURCE_AUDIT_v055.json")
        self.assertEqual(audit["alignment"]["cn_named"],92)
        self.assertTrue(audit["alignment"]["markup_tokens_preserved"])
if __name__=="__main__":
    unittest.main()
