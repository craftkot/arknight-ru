# coding: utf-8
"""Offline regression and preview safety tests for DM-3 v0.37 first draft."""
import json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as event
KEY = "activities/act9d0/level_act9d0_03_beg.txt"
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class DarknightsV037(unittest.TestCase):
    def test_old_translations_preserved_and_complete(self):
        old=load("events/darknights_memoir_dm3_before_partial_ru_v036.json")
        doc=load("events/darknights_memoir_dm3_before_ru_v037.json")
        s=doc["files"][KEY]
        self.assertEqual(doc["version"], "v0.37")
        self.assertIn("not_game_tested", doc["status"])
        for k in ("dialogues","plain_dialogues"):
            for i,t in old[k].items(): self.assertEqual(s[k][i],t)
        self.assertEqual((s["dialogue_count"],s["plain_dialogue_count"]),(152,35))
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,153))))
        self.assertEqual(set(s["plain_dialogues"]),set(map(str,range(1,36))))
        self.assertEqual((s["cn_git_blob_sha1"],s["en_git_blob_sha1"]),(old["source"]["cn_git_blob_sha1"],old["source"]["en_git_blob_sha1"]))
        for v in list(s["dialogues"].values())+list(s["plain_dialogues"].values()):
            self.assertTrue(isinstance(v,str) and v.strip())
            self.assertFalse(any(c in v for c in "\r\n\t"))
            self.assertEqual(event.quoted_tokens(v),[])
    def test_boundaries(self):
        s=load("events/darknights_memoir_dm3_before_ru_v037.json")["files"][KEY]
        self.assertIn("Казделе",s["dialogues"]["124"])
        self.assertIn("Терезия",s["dialogues"]["132"])
        self.assertIn("Доктор",s["dialogues"]["133"])
        self.assertIn("опасна",s["dialogues"]["140"])
        self.assertIn("Доктор",s["dialogues"]["146"])
        self.assertIn("Бабеля",s["dialogues"]["151"])
        self.assertIn("Терезии",s["plain_dialogues"]["23"])
        self.assertIn("Инес",s["plain_dialogues"]["32"])
        self.assertIn("Хёдерер",s["plain_dialogues"]["35"])
    def test_combined_selection(self):
        old=load("events/darknights_memoir_dm1_dm2_ru_v030.json")
        all=load("events/darknights_memoir_dm1_dm2_dm3_before_ru_v037.json")
        s=load("events/darknights_memoir_dm3_before_ru_v037.json")
        self.assertEqual(len(all["files"]),5)
        for k,v in old["files"].items(): self.assertEqual(all["files"][k],v)
        self.assertEqual(all["files"][KEY],s["files"][KEY])
        self.assertEqual(sum(x["dialogue_count"]+x["plain_dialogue_count"] for x in all["files"].values()),839)
    def test_patch_synthetic_preserves_controls(self):
        s=load("events/darknights_memoir_dm3_before_ru_v037.json")["files"][KEY]
        lines=['[HEADER(key="safe")]', '[playMusic(key="$safe")]', '[name="W"] Original line']
        lines+=['[name="W"] Original %s'%i for i in range(2,153)]
        lines+=['Plain original %s'%i for i in range(1,36)]
        lines+=['[Dialog]','[stopmusic(fadetime=1)]']
        output=event.patch(("\n".join(lines)+"\n").encode("utf-8"),s)
        after=output.decode("utf-8").splitlines()
        self.assertEqual(len(after),len(lines))
        self.assertEqual(after[:2],lines[:2])
        self.assertEqual(after[-2:],lines[-2:])
        self.assertEqual((len(event.extract(output)[0]),len(event.extract(output)[1])),(152,35))
        self.assertIn(s["dialogues"]["152"],after[153])
        self.assertIn(s["plain_dialogues"]["35"],after[-3])
    def test_manifest_index_audit_and_preview(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v037.json")
        q=load("reports/QA_v037.json")
        a=load("reports/DM3_SOURCE_AUDIT_v037.json")
        idx=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v037.tsv").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        bat=(ROOT/"BUILD_DARKNIGHTS_DM1_DM2_DM3_BEFORE_PREVIEW_v037.bat").read_text("utf-8")
        self.assertEqual(m["next_file"],"activities/act9d0/level_act9d0_03_end.txt")
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],5)
        self.assertEqual(m["translation_integrity"]["darknights_ru_lines_including_partial"],839)
        self.assertEqual(m["translation_integrity"]["darknights_partial_files"],0)
        self.assertEqual((q["new_named_ru_lines"],q["new_unnamed_ru_lines"],q["new_total"]),(32,14,46))
        self.assertTrue(q["scene_complete"])
        self.assertEqual((a["translation"]["named_lines_translated"],a["translation"]["plain_lines_translated"]),(152,35))
        self.assertTrue(a["translation"]["complete_first_draft"])
        self.assertFalse(a["alignment"]["semantic_alignment_confirmed"])
        self.assertIn("level_act9d0_03_beg.txt\tfirst_draft_complete\t152\t35",idx)
        self.assertIn("level_act9d0_03_end.txt\tnot_translated\t0\t0",idx)
        self.assertIn("darknights_memoir_dm3_before_ru_v037.json",readme)
        self.assertIn("darknights_memoir_dm3_before_partial_ru_v036.json",readme)
        self.assertIn(r"scripts\apply_ru_event.py",bat)
        self.assertIn(r"darknights_memoir_dm1_dm2_dm3_before_ru_v037.json",bat)
if __name__=="__main__":
    unittest.main()
