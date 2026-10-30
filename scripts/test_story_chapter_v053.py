# coding: utf-8
"""Main story 3-2 after battle v0.53 first-draft invariants and safe preview."""
import copy,csv,json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_story as ap
REL="obt/main/level_main_03-02_end.txt"
def load(path):
    return json.loads((ROOT/path).read_text("utf-8"))

class Chapter3Stage32AfterV053(unittest.TestCase):
    def test_full_120_and_pinned_cn_en_sources(self):
        d=load("story/story_chapter_3_stage_3-2_after_ru_v053.json")
        self.assertEqual(d["version"],"v0.53")
        self.assertEqual(set(d["files"]),{REL})
        x=d["files"][REL]
        self.assertEqual(x["dialogue_count"],120)
        self.assertEqual(set(x["dialogues"]),set(map(str,range(1,121))))
        self.assertEqual(x["cn_git_blob_sha1"],"47e83a40c6e41984661069d1b75fdfa7f33d178f")
        self.assertEqual(x["en_git_blob_sha1"],"03ab515ff47a41f7e439d045772e4de74748fd24")
        for t in x["dialogues"].values():
            self.assertIsInstance(t,str)
            self.assertTrue(t.strip())
            self.assertFalse(any(z in t for z in "\r\n\t"))
            self.assertEqual(ap.quoted_tokens(t),[])
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH,REL))
        self.assertIn("против Урсуса",x["dialogues"]["79"])
        self.assertIn("Миша",x["dialogues"]["60"])
        self.assertIn("Экзия",x["dialogues"]["117"])

    def test_all_prior_47_files_unchanged(self):
        d=load("story/story_chapter_3_stage_3-2_after_ru_v053.json")
        old=load("story/story_main_selection_ru_v052.json")
        new=load("story/story_main_selection_ru_v053.json")
        self.assertEqual((len(old["files"]),len(new["files"])),(47,48))
        self.assertEqual(sum(x["dialogue_count"] for x in old["files"].values()),2539)
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()),2659)
        for k,v in old["files"].items():
            self.assertEqual(new["files"][k],v)
        self.assertEqual(new["files"][REL],d["files"][REL])
        self.assertIn("Reunion Member",ap.SPEAKER_RU)
        for name in ("Misha","Skullshatterer","Exusiai","Texas"):
            self.assertIn(name,ap.SPEAKER_RU)

    def test_patch_on_synthetic_source_preserves_commands_and_rejects_unknown_sha(self):
        with tempfile.TemporaryDirectory() as rootname:
            root=pathlib.Path(rootname)
            d=copy.deepcopy(load("story/story_chapter_3_stage_3-2_after_ru_v053.json"))
            scene=d["files"][REL]
            for language in ("en","cn"):
                txt=['[Background(image="kept")]', '[PlayMusic(key="$test")]']
                for i in range(120):
                    role="Reunion Member" if i%4==0 else "Misha" if i%4==1 else "Exusiai" if i%4==2 else "Texas"
                    txt.append('[name="'+(role if language=="en" else "米莎")+'"] '+("Original" if language=="en" else "原文"))
                    txt.append("[Delay(time=0.1)]")
                data=("\r\n".join(txt)+"\r\n").encode("utf-8")
                path=root/"input"/language/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(data)
                scene[language+"_git_blob_sha1"]=ap.git_blob_sha1(data)
            doc=root/"draft.json"
            doc.write_text(json.dumps(d,ensure_ascii=False),"utf-8")
            report=ap.build(root/"input",root/"output",doc)
            self.assertEqual((len(report["files"]),report["lines_total"]),(1,120))
            old=(root/"input"/"en"/REL).read_text("utf-8").splitlines()
            new=(root/"output"/"ru"/REL).read_text("utf-8").splitlines()
            self.assertEqual(len(old),len(new))
            self.assertEqual(old[:2],new[:2])
            self.assertEqual([x for x in old if x.startswith("[Delay")],
                             [x for x in new if x.startswith("[Delay")])
            self.assertEqual(old[1],new[1])
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                ap.build(root/"input",root/"bad",ROOT/"story/story_chapter_3_stage_3-2_after_ru_v053.json")
            self.assertFalse((root/"bad").exists())

    def test_index_chronology_and_audit(self):
        with (ROOT/"story/CHAPTER_3_INDEX_v053.tsv").open(encoding="utf-8") as f:
            rows=list(csv.DictReader(f,delimiter="\t"))
        self.assertEqual(len(rows),4)
        self.assertTrue(all(row["ru_status"]=="first_draft_complete" for row in rows))
        self.assertEqual(sum(int(row["dialogues_ru_count"]) for row in rows),282)
        m=load("chronology/CHRONOLOGY_MANIFEST_v053.json")
        q=load("reports/QA_MAIN_STORY_v053.json")
        a=load("reports/CHAPTER_3_STAGE_3-2_AFTER_SOURCE_AUDIT_v053.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"],m["translation_integrity"]["main_story_named_ru_lines"]),(48,2659))
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],13)
        self.assertEqual(m["translation_integrity"]["babel_completed_files"],1)
        self.assertEqual(m["next_file"],"obt/main/level_main_03-03_beg.txt")
        self.assertEqual((q["new_dialogues"],q["total_dialogues"],q["stage_3_2_combined_dialogues"]),(120,2659,157))
        self.assertTrue(a["alignment"]["dialogue_order_and_source_positions_match"])
        self.assertFalse(a["alignment"]["semantic_alignment_confirmed"])
        self.assertEqual(a["sources"]["cn"]["git_blob_sha1"],"47e83a40c6e41984661069d1b75fdfa7f33d178f")
if __name__=="__main__":
    unittest.main()
