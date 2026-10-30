# coding: utf-8
"""Darknights Memoir DM-6 after battle v0.46 — static regression checks."""
import json
import pathlib
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import apply_ru_event as event
REL="activities/act9d0/level_act9d0_06_end.txt"
def load(path):
    return json.loads((ROOT/path).read_text("utf-8"))
class DarknightsV046(unittest.TestCase):
    def test_full_translation(self):
        d=load("events/darknights_memoir_dm6_after_ru_v046.json")
        s=d["files"][REL]
        self.assertEqual(d["version"],"v0.46")
        self.assertIn("not_game_tested",d["status"])
        self.assertEqual((s["dialogue_count"],s["plain_dialogue_count"]),(132,5))
        self.assertEqual(set(s["dialogues"]),set(map(str,range(1,133))))
        self.assertEqual(set(s["plain_dialogues"]),set(map(str,range(1,6))))
        self.assertEqual(s["cn_git_blob_sha1"],"006e64022a8cefc2a022e4cee1a74543df4f78d1")
        self.assertEqual(s["en_git_blob_sha1"],"4c436f81fec0777ae9aead191d1a0720bd0ea13e")
        self.assertIn("Исповедник",event.SPEAKER_EVENT_RU.values())
        self.assertIn("Рублёв",s["dialogues"]["126"])
        for line in list(s["dialogues"].values())+list(s["plain_dialogues"].values()):
            self.assertIsInstance(line,str)
            self.assertTrue(line.strip())
            self.assertFalse(any(x in line for x in "\n\r\t"))
            self.assertEqual(event.quoted_tokens(line),[])

    def test_previous_eleven_scenes_untouched(self):
        old=load("events/darknights_memoir_dm1_to_dm6_before_ru_v045.json")
        combined=load("events/darknights_memoir_dm1_to_dm6_ru_v046.json")
        current=load("events/darknights_memoir_dm6_after_ru_v046.json")
        self.assertEqual(len(combined["files"]),12)
        for k,v in old["files"].items():self.assertEqual(combined["files"][k],v)
        self.assertEqual(combined["files"][REL],current["files"][REL])
        self.assertEqual(sum(x["dialogue_count"] for x in combined["files"].values()),1581)
        self.assertEqual(sum(x["plain_dialogue_count"] for x in combined["files"].values()),237)

    def test_patch_control_lines_and_names(self):
        spec=load("events/darknights_memoir_dm6_after_ru_v046.json")["files"][REL]
        speakers=["Confessarius","Hoederer","Sarkaz Messenger","W","Unyielding Child","Waifish Child"]
        lines=['[HEADER(key="safe")]','[playMusic(key="$safe")]']
        lines+=['[name="%s"] EN %s'%(speakers[(i-1)%len(speakers)],i) for i in range(1,117)]
        lines+=["Plain source %s"%i for i in range(1,6)]
        lines+=['[name="%s"] EN %s'%(speakers[(i-1)%len(speakers)],i) for i in range(117,133)]
        lines+=['[Dialog]','[stopmusic]']
        data=("\r\n".join(lines)+"\r\n").encode("utf-8")
        out=event.patch(data,spec)
        after=out.decode("utf-8").splitlines()
        self.assertEqual(len(lines),len(after))
        self.assertEqual(lines[:2],after[:2])
        self.assertEqual(lines[-2:],after[-2:])
        self.assertEqual((len(event.extract(out)[0]),len(event.extract(out)[1])),(132,5))
        self.assertIn("Исповедник",out.decode("utf-8"))
        self.assertIn("Посыльный-сарказ",out.decode("utf-8"))
        self.assertIn("Стойкий ребёнок",out.decode("utf-8"))
        self.assertIn("Щуплый ребёнок",out.decode("utf-8"))

    def test_revision_drift_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)
            for lang in ("cn","en"):
                p=root/"sources"/lang/REL
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('[name="W"] fake source\n',"utf-8")
            translations=root/"translated.json"
            translations.write_text((ROOT/"events/darknights_memoir_dm6_after_ru_v046.json").read_text("utf-8"),"utf-8")
            with self.assertRaisesRegex(ValueError,"revision mismatch"):
                event.build(root/"sources",root/"out",translations)
            self.assertFalse((root/"out").exists())

    def test_manifest_readme_index_and_qa(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v046.json")
        q=load("reports/QA_v046.json")
        a=load("reports/DM6_AFTER_SOURCE_AUDIT_v046.json")
        index=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v046.tsv").read_text("utf-8")
        bat=(ROOT/"BUILD_DARKNIGHTS_DM1_TO_DM6_PREVIEW_v046.bat").read_text("utf-8")
        readme=(ROOT/"README.md").read_text("utf-8")
        spec=load("events/darknights_memoir_dm6_after_ru_v046.json")["files"][REL]
        self.assertEqual(m["next_file"],"activities/act9d0/level_act9d0_st01.txt")
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],12)
        self.assertEqual(m["translation_integrity"]["darknights_ru_lines_including_partial"],1818)
        self.assertEqual((q["new_named_ru_lines"],q["new_unnamed_ru_lines"],q["new_total"]),(132,5,137))
        self.assertTrue(q["scene_complete"])
        self.assertEqual(a["sources"]["cn"]["git_blob_sha1"],spec["cn_git_blob_sha1"])
        self.assertEqual(a["sources"]["en"]["git_blob_sha1"],spec["en_git_blob_sha1"])
        self.assertTrue(a["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(a["alignment"]["semantic_alignment_confirmed"])
        self.assertIn("level_act9d0_06_end.txt\tfirst_draft_complete\t132\t5",index)
        self.assertIn(r"events\darknights_memoir_dm1_to_dm6_ru_v046.json",bat)
        self.assertIn("darknights_memoir_dm6_after_ru_v046.json",readme)
if __name__=="__main__":
    unittest.main()
