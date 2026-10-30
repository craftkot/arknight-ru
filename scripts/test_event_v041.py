# coding: utf-8
"""DM-4 before battle v0.41 first draft regression and preview checks."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as event

REL = "activities/act9d0/level_act9d0_04_beg.txt"

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class DarknightsV041(unittest.TestCase):
    def test_complete_and_source_pins(self):
        file = read("events/darknights_memoir_dm4_before_ru_v041.json")
        spec = file["files"][REL]
        self.assertEqual(file["version"], "v0.41")
        self.assertIn("not_game_tested",file["status"])
        self.assertEqual((spec["dialogue_count"],spec["plain_dialogue_count"]),(154,16))
        self.assertEqual(set(spec["dialogues"]),set(map(str,range(1,155))))
        self.assertEqual(set(spec["plain_dialogues"]),set(map(str,range(1,17))))
        self.assertEqual(spec["cn_git_blob_sha1"], "6cee84b7a2cf120af3efd713cf905ecec83bfe3d")
        self.assertEqual(spec["en_git_blob_sha1"], "2b15bfbf0c33a9e833b0a46d7533a636b3be27a5")
        self.assertIn("Терезису", spec["dialogues"]["73"])
        self.assertIn("Воссоединения", spec["dialogues"]["140"])
        self.assertIn("Казделя", spec["plain_dialogues"]["16"])
        for t in list(spec["dialogues"].values())+list(spec["plain_dialogues"].values()):
            self.assertTrue(isinstance(t,str) and t.strip())
            self.assertFalse(any(c in t for c in "\r\n\t"))
            self.assertEqual(event.quoted_tokens(t),[])

    def test_old_six_scenes_preserved(self):
        old=read("events/darknights_memoir_dm1_dm2_dm3_ru_v040.json")
        combined=read("events/darknights_memoir_dm1_dm2_dm3_dm4_before_ru_v041.json")
        current=read("events/darknights_memoir_dm4_before_ru_v041.json")
        self.assertEqual(len(combined["files"]),7)
        for k,v in old["files"].items():self.assertEqual(combined["files"][k],v)
        self.assertEqual(combined["files"][REL],current["files"][REL])
        self.assertEqual(sum(v["dialogue_count"] for v in combined["files"].values()),1060)
        self.assertEqual(sum(v["plain_dialogue_count"] for v in combined["files"].values()),120)

    def test_synthetic_patch_preserves_controls(self):
        spec=read("events/darknights_memoir_dm4_before_ru_v041.json")["files"][REL]
        speakers=["Hoederer","Ines","W","Sarkaz Warrior","???"]
        lines=['[HEADER(key="dummy")]', '[playMusic(key="$safe")]']
        lines+=["Dummy plain %s"%i for i in range(1,10)]
        lines+=['[name="%s"] Dummy named %s'%(speakers[(i-1)%5],i) for i in range(1,155)]
        lines+=["Dummy plain %s"%i for i in range(10,17)]
        lines+=['[Dialog]','[stopmusic]']
        original=("\r\n".join(lines)+"\r\n").encode("utf-8")
        patched=event.patch(original,spec)
        after=patched.decode("utf-8").splitlines()
        self.assertEqual(len(after),len(lines))
        self.assertEqual(after[:2],lines[:2])
        self.assertEqual(after[-2:],lines[-2:])
        self.assertEqual(len(event.extract(patched)[0]),154)
        self.assertEqual(len(event.extract(patched)[1]),16)
        self.assertIn("Хёдерер",patched.decode("utf-8"))
        self.assertEqual(original,("\r\n".join(lines)+"\r\n").encode("utf-8"))

    def test_reject_changed_source_without_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            for lang in ("en","cn"):
                path=root/"source"/lang/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text('[name="W"] not original\n',encoding="utf-8")
            translation=root/"spec.json"
            translation.write_text((ROOT/"events/darknights_memoir_dm4_before_ru_v041.json").read_text(encoding="utf-8"),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                event.build(root/"source",root/"out",translation)
            self.assertFalse((root/"out").exists())

    def test_metadata(self):
        manifest=read("chronology/CHRONOLOGY_MANIFEST_v041.json")
        audit=read("reports/DM4_BEFORE_SOURCE_AUDIT_v041.json")
        qa=read("reports/QA_v041.json")
        index=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v041.tsv").read_text(encoding="utf-8")
        bat=(ROOT/"BUILD_DARKNIGHTS_DM1_TO_DM4_BEFORE_PREVIEW_v041.bat").read_text(encoding="utf-8")
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        spec=read("events/darknights_memoir_dm4_before_ru_v041.json")["files"][REL]
        self.assertEqual(manifest["next_file"],"activities/act9d0/level_act9d0_04_end.txt")
        self.assertEqual(manifest["translation_integrity"]["darknights_completed_files"],7)
        self.assertEqual(manifest["translation_integrity"]["darknights_ru_lines_including_partial"],1180)
        self.assertEqual(qa["new_total"],170)
        self.assertTrue(qa["scene_complete"])
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"],spec["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"],spec["en_git_blob_sha1"])
        self.assertTrue(audit["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(audit["alignment"]["semantic_alignment_confirmed"])
        self.assertIn("level_act9d0_04_beg.txt\tfirst_draft_complete\t154\t16",index)
        self.assertIn(r"events\darknights_memoir_dm1_dm2_dm3_dm4_before_ru_v041.json",bat)
        self.assertIn("darknights_memoir_dm4_before_ru_v041.json",readme)

if __name__ == "__main__":
    unittest.main()
