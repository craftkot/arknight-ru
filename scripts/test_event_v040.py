# coding: utf-8
"""Offline regression checks for complete first draft of DM-3 after battle."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as event
from apply_ru_story import git_blob_sha1

REL = "activities/act9d0/level_act9d0_03_end.txt"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class DarknightsV040(unittest.TestCase):
    def test_complete_contiguous_and_previous_preserved(self):
        previous = load("events/darknights_memoir_dm3_after_partial_ru_v039.json")
        complete = load("events/darknights_memoir_dm3_after_ru_v040.json")
        spec = complete["files"][REL]
        self.assertEqual(complete["version"], "v0.40")
        self.assertIn("not_game_tested", complete["status"])
        self.assertEqual((spec["dialogue_count"],spec["plain_dialogue_count"]),(160,11))
        self.assertEqual(set(spec["dialogues"]), {str(i) for i in range(1,161)})
        self.assertEqual(set(spec["plain_dialogues"]), {str(i) for i in range(1,12)})
        for key, line in previous["dialogues"].items():
            self.assertEqual(spec["dialogues"][key], line)
        self.assertEqual(spec["cn_git_blob_sha1"],previous["source"]["cn_git_blob_sha1"])
        self.assertEqual(spec["en_git_blob_sha1"],previous["source"]["en_git_blob_sha1"])
        self.assertEqual(spec["dialogues"]["67"][:3], "Ты ")
        self.assertIn("Терезия",spec["plain_dialogues"]["6"])
        self.assertIn("страшно",spec["dialogues"]["160"])
        for line in list(spec["dialogues"].values())+list(spec["plain_dialogues"].values()):
            self.assertIsInstance(line,str)
            self.assertTrue(line.strip())
            self.assertFalse(any(char in line for char in "\r\n\t"))
            self.assertEqual(event.quoted_tokens(line), [])

    def test_combined_six_previous_files_untouched(self):
        old=load("events/darknights_memoir_dm1_dm2_dm3_before_ru_v037.json")
        full=load("events/darknights_memoir_dm1_dm2_dm3_ru_v040.json")
        new=load("events/darknights_memoir_dm3_after_ru_v040.json")
        self.assertEqual(len(full["files"]),6)
        for key, spec in old["files"].items():
            self.assertEqual(full["files"][key],spec)
        self.assertEqual(full["files"][REL],new["files"][REL])
        self.assertEqual(sum(s["dialogue_count"] for s in full["files"].values()),906)
        self.assertEqual(sum(s["plain_dialogue_count"] for s in full["files"].values()),104)

    def test_synthetic_mixed_source_preserves_commands_and_order(self):
        spec=load("events/darknights_memoir_dm3_after_ru_v040.json")["files"][REL]
        speaker=["Kal'tsit","Hoederer","Ines","Scout","W","Sarkaz Captive"]
        lines=['[HEADER(key="title",is_skippable=true)]','[playMusic(key="$mist_loop")]']
        lines += ['[name="%s"] Fake EN %s'%(speaker[(i-1)%len(speaker)],i) for i in range(1,147)]
        lines += ['Synthetic narration %s'%i for i in range(1,4)]
        lines += ['[name="%s"] Fake EN %s'%(speaker[(i-1)%len(speaker)],i) for i in range(147,161)]
        lines += ['Synthetic narration %s'%i for i in range(4,12)]
        lines += ['[Dialog]','[stopmusic]']
        raw=("\r\n".join(lines)+"\r\n").encode("utf-8")
        ru=event.patch(raw,spec)
        after=ru.decode("utf-8").splitlines()
        self.assertEqual(len(after),len(lines))
        self.assertEqual(after[:2],lines[:2])
        self.assertEqual(after[-2:],lines[-2:])
        self.assertEqual(len(event.extract(ru)[0]),160)
        self.assertEqual(len(event.extract(ru)[1]),11)
        self.assertIn("Скаут",ru.decode("utf-8"))
        self.assertIn("Пленный сарказ",ru.decode("utf-8"))
        self.assertEqual(raw,("\r\n".join(lines)+"\r\n").encode("utf-8"))

    def test_rejects_revision_mismatch_without_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder)
            for lang in ("en","cn"):
                path=root/"source"/lang/REL
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text('[name="W"] test\n',encoding="utf-8")
            selection=root/"full.json"
            selection.write_text((ROOT/"events/darknights_memoir_dm3_after_ru_v040.json").read_text("utf-8"),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                event.build(root/"source",root/"out",selection)
            self.assertFalse((root/"out").exists())

    def test_metadata_and_next_scene(self):
        data=load("events/darknights_memoir_dm3_after_ru_v040.json")["files"][REL]
        audit=load("reports/DM3_AFTER_SOURCE_AUDIT_v040.json")
        qa=load("reports/QA_v040.json")
        manifest=load("chronology/CHRONOLOGY_MANIFEST_v040.json")
        index=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v040.tsv").read_text("utf-8")
        bat=(ROOT/"BUILD_DARKNIGHTS_DM1_DM2_DM3_PREVIEW_v040.bat").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        self.assertEqual(data["cn_git_blob_sha1"],"2c6e2acad62c3037c561946ada0764c633a8adb9")
        self.assertEqual(data["en_git_blob_sha1"],"9c52ccad2f1ba96dd007df147a4eece1515e2321")
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"],data["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"],data["en_git_blob_sha1"])
        self.assertTrue(audit["translation"]["complete_first_draft"])
        self.assertFalse(audit["alignment"]["semantic_alignment_confirmed"])
        self.assertEqual((qa["new_named_ru_lines"],qa["new_unnamed_ru_lines"],qa["new_total"]),(94,11,105))
        self.assertTrue(qa["scene_complete"])
        self.assertEqual(manifest["translation_integrity"]["darknights_completed_files"],6)
        self.assertEqual(manifest["translation_integrity"]["darknights_ru_lines_including_partial"],1010)
        self.assertEqual(manifest["next_file"],"activities/act9d0/level_act9d0_04_beg.txt")
        self.assertIn("level_act9d0_03_end.txt\tfirst_draft_complete\t160\t11",index)
        self.assertIn(r"events\darknights_memoir_dm1_dm2_dm3_ru_v040.json",bat)
        self.assertIn("darknights_memoir_dm3_after_partial_ru_v039.json",readme)

if __name__ == "__main__":
    unittest.main()
