# coding: utf-8
"""Regression checks: Darknights Memoir DM-5 before-battle v0.43."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as event

REL = "activities/act9d0/level_act9d0_05_beg.txt"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class DarknightsV043(unittest.TestCase):
    def test_full_scene_and_source_pins(self):
        doc = load("events/darknights_memoir_dm5_before_ru_v043.json")
        spec = doc["files"][REL]
        self.assertEqual(doc["version"], "v0.43")
        self.assertIn("not_game_tested", doc["status"])
        self.assertEqual((spec["dialogue_count"],spec["plain_dialogue_count"]), (102,0))
        self.assertEqual(set(spec["dialogues"]), set(map(str,range(1,103))))
        self.assertEqual(spec["plain_dialogues"], {})
        self.assertEqual(spec["cn_git_blob_sha1"], "052baf117c32259107ca11c57360c1555953d741")
        self.assertEqual(spec["en_git_blob_sha1"], "7105d149710be623cc1ca24b8d193bf4944b28c9")
        self.assertIn("самого себя", spec["dialogues"]["16"])
        self.assertIn("Надеюсь", spec["dialogues"]["56"])
        self.assertIn("Хёдерер", spec["dialogues"]["97"])
        for x in spec["dialogues"].values():
            self.assertTrue(isinstance(x,str) and x.strip())
            self.assertFalse(any(ch in x for ch in "\n\r\t"))
            self.assertEqual(event.quoted_tokens(x),[])

    def test_previous_eight_complete_scenes_untouched(self):
        old=load("events/darknights_memoir_dm1_dm2_dm3_dm4_ru_v042.json")
        combined=load("events/darknights_memoir_dm1_dm2_dm3_dm4_dm5_before_ru_v043.json")
        new=load("events/darknights_memoir_dm5_before_ru_v043.json")
        self.assertEqual(len(combined["files"]),9)
        for path,spec in old["files"].items():
            self.assertEqual(combined["files"][path],spec)
        self.assertEqual(combined["files"][REL],new["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in combined["files"].values()),1238)
        self.assertEqual(sum(x["plain_dialogue_count"] for x in combined["files"].values()),134)

    def test_synthetic_patch_speakers_and_commands(self):
        spec=load("events/darknights_memoir_dm5_before_ru_v043.json")["files"][REL]
        speakers=["Sarkaz Mercenary Leader", "Ines", "Scout", "Talulah?", "Hoederer", "Talulah"]
        lines=['[HEADER(key="safe")]', '[playMusic(key="$safe")]']
        lines+=['[name="%s"] EN line %s'%(speakers[(i-1)%len(speakers)],i) for i in range(1,103)]
        lines+=['[Dialog]', '[stopmusic]']
        raw=("\r\n".join(lines)+"\r\n").encode("utf-8")
        patched=event.patch(raw,spec)
        output=patched.decode("utf-8")
        after=output.splitlines()
        self.assertEqual(len(after),len(lines))
        self.assertEqual(after[:2],lines[:2])
        self.assertEqual(after[-2:],lines[-2:])
        self.assertEqual((len(event.extract(patched)[0]),len(event.extract(patched)[1])),(102,0))
        self.assertIn("Командир наёмников-сарказов",output)
        self.assertIn("Талула?",output)
        self.assertIn("Талула",output)

    def test_reject_wrong_source_without_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            for lang in ("cn","en"):
                path=root/"source"/lang/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text('[name="W"] not original\n',encoding="utf-8")
            translations=root/"dm.json"
            translations.write_text((ROOT/"events/darknights_memoir_dm5_before_ru_v043.json").read_text("utf-8"),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                event.build(root/"source",root/"out",translations)
            self.assertFalse((root/"out").exists())

    def test_qa_manifest_index_and_bat(self):
        manifest=load("chronology/CHRONOLOGY_MANIFEST_v043.json")
        audit=load("reports/DM5_BEFORE_SOURCE_AUDIT_v043.json")
        qa=load("reports/QA_v043.json")
        index=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v043.tsv").read_text("utf-8")
        bat=(ROOT/"BUILD_DARKNIGHTS_DM1_TO_DM5_BEFORE_PREVIEW_v043.bat").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        spec=load("events/darknights_memoir_dm5_before_ru_v043.json")["files"][REL]
        self.assertEqual(manifest["next_file"],"activities/act9d0/level_act9d0_05_end.txt")
        self.assertEqual(manifest["translation_integrity"]["darknights_completed_files"],9)
        self.assertEqual(manifest["translation_integrity"]["darknights_named_ru_lines"],1238)
        self.assertEqual(manifest["translation_integrity"]["darknights_plain_ru_lines"],134)
        self.assertEqual(manifest["translation_integrity"]["darknights_ru_lines_including_partial"],1372)
        self.assertEqual((qa["new_named_ru_lines"],qa["new_unnamed_ru_lines"],qa["new_total"]),(102,0,102))
        self.assertTrue(qa["scene_complete"])
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"],spec["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"],spec["en_git_blob_sha1"])
        self.assertTrue(audit["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(audit["alignment"]["semantic_alignment_confirmed"])
        self.assertIn("level_act9d0_05_beg.txt\tfirst_draft_complete\t102\t0",index)
        self.assertIn(r"events\darknights_memoir_dm1_dm2_dm3_dm4_dm5_before_ru_v043.json",bat)
        self.assertIn("darknights_memoir_dm5_before_ru_v043.json",readme)

if __name__=="__main__":
    unittest.main()
