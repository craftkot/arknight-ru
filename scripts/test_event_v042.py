# coding: utf-8
"""Regression tests for DM-4 after battle v0.42 full first draft."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as event

REL = "activities/act9d0/level_act9d0_04_end.txt"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class DarknightsV042(unittest.TestCase):
    def test_full_scene_counts_source_and_text(self):
        doc=load("events/darknights_memoir_dm4_after_ru_v042.json")
        spec=doc["files"][REL]
        self.assertEqual(doc["version"],"v0.42")
        self.assertIn("not_game_tested",doc["status"])
        self.assertEqual((spec["dialogue_count"],spec["plain_dialogue_count"]),(76,14))
        self.assertEqual(set(spec["dialogues"]),set(map(str,range(1,77))))
        self.assertEqual(set(spec["plain_dialogues"]),set(map(str,range(1,15))))
        self.assertEqual(spec["cn_git_blob_sha1"],"144c07a31324e378d204bfd509d5f3c4e12ecac5")
        self.assertEqual(spec["en_git_blob_sha1"],"641b70cdbc5b2bbfe6bde990146ad1088c413c2d")
        self.assertIn("орипатии",spec["dialogues"]["48"])
        self.assertIn("Хм-хм",spec["dialogues"]["59"])
        self.assertIn("Терезиса",spec["dialogues"]["71"])
        self.assertIn("Война",spec["plain_dialogues"]["13"])
        for item in list(spec["dialogues"].values())+list(spec["plain_dialogues"].values()):
            self.assertIsInstance(item,str)
            self.assertTrue(item.strip())
            self.assertFalse(any(ch in item for ch in "\n\r\t"))
            self.assertEqual(event.quoted_tokens(item),[])

    def test_old_seven_scenes_preserved(self):
        old=load("events/darknights_memoir_dm1_dm2_dm3_dm4_before_ru_v041.json")
        all_=load("events/darknights_memoir_dm1_dm2_dm3_dm4_ru_v042.json")
        new=load("events/darknights_memoir_dm4_after_ru_v042.json")
        self.assertEqual(len(all_["files"]),8)
        for key,value in old["files"].items():
            self.assertEqual(all_["files"][key],value)
        self.assertEqual(all_["files"][REL],new["files"][REL])
        self.assertEqual(sum(item["dialogue_count"] for item in all_["files"].values()),1136)
        self.assertEqual(sum(item["plain_dialogue_count"] for item in all_["files"].values()),134)

    def test_synthetic_preview_named_plain_controls_and_talulah(self):
        spec=load("events/darknights_memoir_dm4_after_ru_v042.json")["files"][REL]
        speaker=["Hoederer","Ines","W","Sarkaz Warrior","Talulah"]
        lines=['[HEADER(key="safe")]', '[playMusic(key="$music")]']
        lines+=["Narration sample %s"%i for i in range(1,5)]
        lines+=['[name="%s"] Original EN %s'%(speaker[(i-1)%5],i) for i in range(1,74)]
        lines+=["Narration sample %s"%i for i in range(5,11)]
        lines+=['[name="Talulah"] Original EN %s'%i for i in range(74,77)]
        lines+=["Narration sample %s"%i for i in range(11,15)]
        lines+=['[Dialog]', '[stopmusic]']
        raw=("\r\n".join(lines)+"\r\n").encode("utf-8")
        result=event.patch(raw,spec)
        after=result.decode("utf-8").splitlines()
        self.assertEqual(len(after),len(lines))
        self.assertEqual(after[:2],lines[:2])
        self.assertEqual(after[-2:],lines[-2:])
        self.assertEqual((len(event.extract(result)[0]),len(event.extract(result)[1])),(76,14))
        self.assertIn("Талула",result.decode("utf-8"))
        self.assertIn("Добро пожаловать",result.decode("utf-8"))

    def test_reject_modified_source_without_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            for lang in ("cn","en"):
                path=root/"source"/lang/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text('[name="W"] wrong source\n',encoding="utf-8")
            saved=root/"selection.json"
            saved.write_text((ROOT/"events/darknights_memoir_dm4_after_ru_v042.json").read_text("utf-8"),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                event.build(root/"source",root/"preview",saved)
            self.assertFalse((root/"preview").exists())

    def test_manifest_index_source_audit_and_preview(self):
        manifest=load("chronology/CHRONOLOGY_MANIFEST_v042.json")
        index=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v042.tsv").read_text("utf-8")
        audit=load("reports/DM4_AFTER_SOURCE_AUDIT_v042.json")
        qa=load("reports/QA_v042.json")
        bat=(ROOT/"BUILD_DARKNIGHTS_DM1_TO_DM4_PREVIEW_v042.bat").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        spec=load("events/darknights_memoir_dm4_after_ru_v042.json")["files"][REL]
        self.assertEqual(manifest["next_file"],"activities/act9d0/level_act9d0_05_beg.txt")
        self.assertEqual(manifest["translation_integrity"]["darknights_completed_files"],8)
        self.assertEqual(manifest["translation_integrity"]["darknights_named_ru_lines"],1136)
        self.assertEqual(manifest["translation_integrity"]["darknights_plain_ru_lines"],134)
        self.assertEqual(manifest["translation_integrity"]["darknights_ru_lines_including_partial"],1270)
        self.assertEqual((qa["new_named_ru_lines"],qa["new_unnamed_ru_lines"],qa["new_total"]),(76,14,90))
        self.assertTrue(qa["scene_complete"])
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"],spec["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"],spec["en_git_blob_sha1"])
        self.assertTrue(audit["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(audit["alignment"]["semantic_alignment_confirmed"])
        self.assertIn("level_act9d0_04_end.txt\tfirst_draft_complete\t76\t14",index)
        self.assertIn(r"events\darknights_memoir_dm1_dm2_dm3_dm4_ru_v042.json",bat)
        self.assertIn("darknights_memoir_dm4_after_ru_v042.json",readme)

if __name__=="__main__":
    unittest.main()
