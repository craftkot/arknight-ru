# coding: utf-8
"""DM-6 before-battle v0.45 first-draft regression and preview checks."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as event

REL = "activities/act9d0/level_act9d0_06_beg.txt"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class DarknightsV045(unittest.TestCase):
    def test_full_translation_and_source_refs(self):
        doc=load("events/darknights_memoir_dm6_before_ru_v045.json")
        spec=doc["files"][REL]
        self.assertEqual(doc["version"],"v0.45")
        self.assertIn("not_game_tested",doc["status"])
        self.assertEqual((spec["dialogue_count"],spec["plain_dialogue_count"]),(219,6))
        self.assertEqual(set(spec["dialogues"]),set(map(str,range(1,220))))
        self.assertEqual(set(spec["plain_dialogues"]),set(map(str,range(1,7))))
        self.assertEqual(spec["cn_git_blob_sha1"],"d5b1c14de71cf9e2934de501849ffd2fd678342b")
        self.assertEqual(spec["en_git_blob_sha1"],"dad011c5c2e8b82bce388b3acf3b7b65d6430b49")
        self.assertIn("Талула",spec["dialogues"]["54"])
        self.assertIn("Воссоединения",spec["dialogues"]["82"])
        self.assertIn("Инес",spec["dialogues"]["203"])
        self.assertIn("22:14",spec["plain_dialogues"]["2"])
        for line in list(spec["dialogues"].values())+list(spec["plain_dialogues"].values()):
            self.assertTrue(isinstance(line,str) and line.strip())
            self.assertFalse(any(char in line for char in "\n\r\t"))
            self.assertEqual(event.quoted_tokens(line),[])

    def test_previous_ten_scenes_preserved(self):
        old=load("events/darknights_memoir_dm1_dm2_dm3_dm4_dm5_ru_v044.json")
        all_=load("events/darknights_memoir_dm1_to_dm6_before_ru_v045.json")
        new=load("events/darknights_memoir_dm6_before_ru_v045.json")
        self.assertEqual(len(all_["files"]),11)
        for key,spec in old["files"].items():
            self.assertEqual(all_["files"][key],spec)
        self.assertEqual(all_["files"][REL],new["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in all_["files"].values()),1531)
        self.assertEqual(sum(x["plain_dialogue_count"] for x in all_["files"].values()),150)

    def test_synthetic_preview_preserves_controls_and_speakers(self):
        spec=load("events/darknights_memoir_dm6_before_ru_v045.json")["files"][REL]
        speakers=["Hoederer","W","Ines","???","Reunion Soldier"]
        lines=['[HEADER(key="safe")]', '[playMusic(key="$safe")]']
        lines+=["Original plain %s"%i for i in range(1,7)]
        lines+=['[name="%s"] EN original %s'%(speakers[(i-1)%len(speakers)],i) for i in range(1,220)]
        lines+=['[Dialog]','[stopmusic]']
        raw=("\r\n".join(lines)+"\r\n").encode("utf-8")
        patched=event.patch(raw,spec)
        output=patched.decode("utf-8")
        after=output.splitlines()
        self.assertEqual(len(after),len(lines))
        self.assertEqual(after[:2],lines[:2])
        self.assertEqual(after[-2:],lines[-2:])
        self.assertEqual((len(event.extract(patched)[0]),len(event.extract(patched)[1])),(219,6))
        self.assertIn("Боец Воссоединения",output)
        self.assertIn('name="???"',output)
        self.assertIn("Хёдерер",output)

    def test_reject_modified_source_before_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=pathlib.Path(temporary)
            for language in ("en","cn"):
                path=root/"source"/language/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text('[name="W"] tampered content\n',encoding="utf-8")
            spec_path=root/"selected.json"
            spec_path.write_text((ROOT/"events/darknights_memoir_dm6_before_ru_v045.json").read_text(encoding="utf-8"),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                event.build(root/"source",root/"output",spec_path)
            self.assertFalse((root/"output").exists())

    def test_metadata(self):
        manifest=load("chronology/CHRONOLOGY_MANIFEST_v045.json")
        audit=load("reports/DM6_BEFORE_SOURCE_AUDIT_v045.json")
        qa=load("reports/QA_v045.json")
        index=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v045.tsv").read_text("utf-8")
        bat=(ROOT/"BUILD_DARKNIGHTS_DM1_TO_DM6_BEFORE_PREVIEW_v045.bat").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        spec=load("events/darknights_memoir_dm6_before_ru_v045.json")["files"][REL]
        self.assertEqual(manifest["next_file"],"activities/act9d0/level_act9d0_06_end.txt")
        self.assertEqual(manifest["translation_integrity"]["darknights_completed_files"],11)
        self.assertEqual(manifest["translation_integrity"]["darknights_named_ru_lines"],1531)
        self.assertEqual(manifest["translation_integrity"]["darknights_plain_ru_lines"],150)
        self.assertEqual(manifest["translation_integrity"]["darknights_ru_lines_including_partial"],1681)
        self.assertEqual((qa["new_named_ru_lines"],qa["new_unnamed_ru_lines"],qa["new_total"]),(219,6,225))
        self.assertTrue(qa["scene_complete"])
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"],spec["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"],spec["en_git_blob_sha1"])
        self.assertTrue(audit["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(audit["alignment"]["semantic_alignment_confirmed"])
        self.assertIn("level_act9d0_06_beg.txt\tfirst_draft_complete\t219\t6",index)
        self.assertIn(r"events\darknights_memoir_dm1_to_dm6_before_ru_v045.json",bat)
        self.assertIn("darknights_memoir_dm6_before_ru_v045.json",readme)

if __name__=="__main__":
    unittest.main()
