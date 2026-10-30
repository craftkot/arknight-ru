# coding: utf-8
"""Arknights Darknights Memoir v0.47 complete first-draft regression checks."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_event as event
import build_release_testpack_v047 as release

REL="activities/act9d0/level_act9d0_st01.txt"
def load(path):return json.loads((ROOT/path).read_text("utf-8"))

class DarknightsV047(unittest.TestCase):
    def test_all_st01_lines_and_source_hashes(self):
        d=load("events/darknights_memoir_st01_ru_v047.json")
        s=d["files"][REL]
        self.assertEqual(d["version"],"v0.47")
        self.assertIn("not_game_tested",d["status"])
        self.assertEqual((s["dialogue_count"],s["plain_dialogue_count"]),(239,5))
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,240))))
        self.assertEqual(set(s["plain_dialogues"]),set(map(str,range(1,6))))
        self.assertEqual(s["cn_git_blob_sha1"],"ef38d6471d4890a126a4b487c56938aa7ed620cf")
        self.assertEqual(s["en_git_blob_sha1"],"10773adce6afe48cc35db38aa8de35ef594d4c3f")
        self.assertIn("Андрей",s["dialogues"]["228"])
        self.assertIn("Талула",s["dialogues"]["239"])
        for v in list(s["dialogues"].values())+list(s["plain_dialogues"].values()):
            self.assertTrue(isinstance(v,str) and v.strip())
            self.assertFalse(any(c in v for c in "\r\n\t"))
            self.assertEqual(event.quoted_tokens(v),[])

    def test_first_120_preserved_and_previous_12_scenes(self):
        partial=load("events/darknights_memoir_st01_partial_ru_v047.json")
        full=load("events/darknights_memoir_st01_ru_v047.json")["files"][REL]
        for k,v in partial["dialogues"].items():
            self.assertEqual(full["dialogues"][k],v)
        old=load("events/darknights_memoir_dm1_to_dm6_ru_v046.json")
        combo=load("events/darknights_memoir_all_ru_v047.json")
        self.assertEqual(len(combo["files"]),13)
        for k,v in old["files"].items():self.assertEqual(combo["files"][k],v)
        self.assertEqual(combo["files"][REL],full)
        self.assertEqual(sum(v["dialogue_count"] for v in combo["files"].values()),1902)
        self.assertEqual(sum(v["plain_dialogue_count"] for v in combo["files"].values()),160)

    def test_synthetic_patch_keeps_scene_control(self):
        s=load("events/darknights_memoir_st01_ru_v047.json")["files"][REL]
        speaker=["W","Unyielding Child","Waifish Child"]
        lines=['[HEADER(key="safety")]','[playMusic(key="$safe")]']
        lines+=['[name="%s"] Original EN %s'%(speaker[(i-1)%3],i) for i in range(1,238)]
        lines+=['Narration sample %s'%i for i in range(1,6)]
        lines+=['[name="W"] Original EN %s'%i for i in range(238,240)]
        lines+=['[Dialog]','[stopmusic]']
        raw=("\r\n".join(lines)+"\r\n").encode("utf-8")
        out=event.patch(raw,s)
        after=out.decode("utf-8").splitlines()
        self.assertEqual(len(lines),len(after))
        self.assertEqual(lines[:2],after[:2])
        self.assertEqual(lines[-2:],after[-2:])
        self.assertEqual((len(event.extract(out)[0]),len(event.extract(out)[1])),(239,5))
        self.assertIn("Стойкий ребёнок",out.decode("utf-8"))
        self.assertIn("Щуплый ребёнок",out.decode("utf-8"))

    def test_index_manifest_and_audit(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v047.json")
        a=load("reports/DM_ST01_SOURCE_AUDIT_v047.json")
        q=load("reports/QA_v047.json")
        idx=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v047.tsv").read_text("utf-8")
        bat=(ROOT/"BUILD_DARKNIGHTS_ALL_PREVIEW_v047.bat").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        self.assertIsNone(m["next_file"])
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],13)
        self.assertEqual(m["translation_integrity"]["darknights_ru_lines_including_partial"],2062)
        self.assertEqual(m["translation_integrity"]["darknights_named_ru_lines"],1902)
        self.assertEqual(m["translation_integrity"]["darknights_plain_ru_lines"],160)
        self.assertEqual((q["new_named_ru_lines"],q["new_unnamed_ru_lines"],q["new_total"]),(239,5,244))
        self.assertTrue(q["scene_complete"])
        self.assertEqual(a["sources"]["cn"]["git_blob_sha1"],"ef38d6471d4890a126a4b487c56938aa7ed620cf")
        self.assertEqual(a["sources"]["en"]["git_blob_sha1"],"10773adce6afe48cc35db38aa8de35ef594d4c3f")
        self.assertTrue(a["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(a["alignment"]["semantic_alignment_confirmed"])
        self.assertIn("level_act9d0_st01.txt\tfirst_draft_complete\t239\t5",idx)
        self.assertIn(r"events\darknights_memoir_all_ru_v047.json",bat)
        self.assertIn("darknights_memoir_all_ru_v047.json",readme)

    def test_release_zip_has_no_game_files_or_installers(self):
        with tempfile.TemporaryDirectory() as td:
            report=release.build(td)
            zip_path=pathlib.Path(td)/report["artifact"]
            self.assertEqual(report["dm_lines"],2062)
            self.assertEqual(report["ui_keyed"],2544)
            digest=hashlib.sha256(zip_path.read_bytes()).hexdigest()
            self.assertEqual(report["sha256"],digest)
            self.assertEqual((pathlib.Path(td)/"Arknights_RU_TestPack_v047.sha256").read_text("utf-8").split()[0],digest)
            with zipfile.ZipFile(zip_path) as z:
                names=z.namelist()
                self.assertIn("Arknights_RU_TestPack_v047/README_FIRST_RU.md",names)
                self.assertIn("Arknights_RU_TestPack_v047/Translation/ru/Text/Arknights_RU_UI_EXPERIMENTAL.txt",names)
                self.assertIn("Arknights_RU_TestPack_v047/events/darknights_memoir_all_ru_v047.json",names)
                self.assertFalse(any(x.lower().endswith((".exe",".dll",".apk")) for x in names))
                self.assertFalse(any("/cn/" in x or "/en/activities/" in x for x in names))
if __name__=="__main__":
    unittest.main()
