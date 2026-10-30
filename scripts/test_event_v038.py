# coding: utf-8
"""DM-3 after-battle v0.38 partial draft integrity checks."""
import json
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class DarknightsV038(unittest.TestCase):
    def test_partial_prefix_and_safety(self):
        doc=load("events/darknights_memoir_dm3_after_partial_ru_v038.json")
        self.assertEqual(doc["version"],"v0.38-partial")
        self.assertEqual(doc["format"],"partial_translation_work_in_progress")
        self.assertFalse(doc["progress"]["complete"])
        self.assertEqual((doc["source"]["named_dialogue_count"],doc["source"]["plain_dialogue_count"]),(160,11))
        self.assertEqual(set(doc["dialogues"]),{str(i) for i in range(1,61)})
        self.assertEqual(doc["plain_dialogues"],{})
        self.assertEqual((doc["progress"]["next_named_ordinal"],doc["progress"]["next_plain_ordinal"]),(61,1))
        for s in doc["dialogues"].values():
            self.assertTrue(isinstance(s,str) and s.strip())
            self.assertFalse(any(ch in s for ch in "\r\n\t"))
    def test_source_and_counts(self):
        doc=load("events/darknights_memoir_dm3_after_partial_ru_v038.json")
        audit=load("reports/DM3_AFTER_SOURCE_AUDIT_v038.json")
        q=load("reports/QA_v038.json")
        self.assertEqual((doc["source"]["cn_git_blob_sha1"],doc["source"]["en_git_blob_sha1"]),("2c6e2acad62c3037c561946ada0764c633a8adb9","9c52ccad2f1ba96dd007df147a4eece1515e2321"))
        self.assertEqual(audit["sources"]["cn"]["git_blob_sha1"],doc["source"]["cn_git_blob_sha1"])
        self.assertEqual(audit["sources"]["en"]["git_blob_sha1"],doc["source"]["en_git_blob_sha1"])
        self.assertTrue(audit["alignment"]["dialogue_kind_sequence_identical"])
        self.assertFalse(audit["alignment"]["semantic_alignment_confirmed"])
        self.assertEqual((q["new_named_ru_lines"],q["new_unnamed_ru_lines"],q["new_total"]),(60,0,60))
        self.assertFalse(q["scene_complete"])
    def test_manifest_index_readme(self):
        m=load("chronology/CHRONOLOGY_MANIFEST_v038.json")
        idx=(ROOT/"events/DARKNIGHTS_MEMOIR_INDEX_v038.tsv").read_text(encoding="utf-8")
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertEqual(m["next_file"],"activities/act9d0/level_act9d0_03_end.txt")
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"],5)
        self.assertEqual(m["translation_integrity"]["darknights_ru_lines_including_partial"],899)
        self.assertEqual(m["translation_integrity"]["darknights_partial_files"],1)
        self.assertIn("level_act9d0_03_end.txt\tpartial_first_draft\t60\t0",idx)
        self.assertIn("darknights_memoir_dm3_after_partial_ru_v038.json",readme)
    def test_cn_overrides_known_en_differences(self):
        d=load("events/darknights_memoir_dm3_after_partial_ru_v038.json")["dialogues"]
        self.assertIn("Оставил",d["44"])
        self.assertIn("мог",d["54"])
        self.assertIn("Ты и я",d["59"])
if __name__=="__main__":
    unittest.main()
