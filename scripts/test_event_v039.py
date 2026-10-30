# coding: utf-8
"""Regression checks for the DM-3 after-battle v0.39 partial draft."""
import json
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))
class DarknightsV039(unittest.TestCase):
    def test_prefix_and_safety(self):
        old = load("events/darknights_memoir_dm3_after_partial_ru_v038.json")
        doc = load("events/darknights_memoir_dm3_after_partial_ru_v039.json")
        self.assertEqual(doc["version"], "v0.39-partial")
        self.assertEqual(doc["format"], "partial_translation_work_in_progress")
        self.assertFalse(doc["progress"]["complete"])
        self.assertEqual(doc["source"], old["source"])
        self.assertEqual((doc["source"]["named_dialogue_count"],doc["source"]["plain_dialogue_count"]),(160,11))
        self.assertEqual(set(doc["dialogues"]), {str(i) for i in range(1,67)})
        self.assertEqual(doc["plain_dialogues"], {})
        for k,v in old["dialogues"].items():
            self.assertEqual(doc["dialogues"][k],v)
        self.assertEqual((doc["progress"]["named_ru_lines"],doc["progress"]["plain_ru_lines"],doc["progress"]["total_ru_lines"]),(66,0,66))
        self.assertEqual((doc["progress"]["next_named_ordinal"],doc["progress"]["next_plain_ordinal"]),(67,1))
        for value in doc["dialogues"].values():
            self.assertTrue(isinstance(value,str) and value.strip())
            self.assertFalse(any(c in value for c in "\r\n\t"))
    def test_metadata(self):
        doc=load("events/darknights_memoir_dm3_after_partial_ru_v039.json")
        audit=load("reports/DM3_AFTER_SOURCE_AUDIT_v039.json")
        qa=load("reports/QA_v039.json")
        m=load("chronology/CHRONOLOGY_MANIFEST_v039.json")
        idx=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v039.tsv").read_text(encoding="utf-8")
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertEqual(doc["source"]["cn_git_blob_sha1"],"2c6e2acad62c3037c561946ada0764c633a8adb9")
        self.assertEqual(doc["source"]["en_git_blob_sha1"],"9c52ccad2f1ba96dd007df147a4eece1515e2321")
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"],doc["source"]["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"],doc["source"]["en_git_blob_sha1"])
        self.assertTrue(audit["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(audit["alignment"]["semantic_alignment_confirmed"])
        self.assertEqual((audit["translation"]["named_lines_translated"],audit["translation"]["remaining_named_lines"]),(66,94))
        self.assertEqual((qa["new_named_ru_lines"],qa["new_total"],qa["event_ru_lines_including_partial"]),(6,6,905))
        self.assertFalse(qa["scene_complete"])
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],5)
        self.assertEqual(m["translation_integrity"]["darknights_ru_lines_including_partial"],905)
        self.assertEqual(m["next_file"],"activities/act9d0/level_act9d0_03_end.txt")
        self.assertIn("level_act9d0_03_end.txt\tpartial_first_draft\t66\t0",idx)
        self.assertIn("darknights_memoir_dm3_after_partial_ru_v039.json",readme)
        self.assertIn("Докторе",doc["dialogues"]["64"])
if __name__=="__main__":
    unittest.main()
