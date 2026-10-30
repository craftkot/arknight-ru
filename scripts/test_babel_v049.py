# coding: utf-8
"""Offline invariants for Babel BB-ST-1 v0.49 cumulative partial draft."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelV049(unittest.TestCase):
    def setUp(self):
        self.d = load("events/babel_st01_opening_partial_ru_v049.json")
        self.old = load("events/babel_st01_opening_partial_ru_v048.json")

    def test_contiguous_progress_and_no_duplicate_work(self):
        d = self.d
        p = d["progress"]
        self.assertEqual((p["source_lines_translated_through"], p["next_source_line"]), (194, 195))
        self.assertEqual((p["named_ru_lines"], p["plain_ru_lines"], p["sticker_ru_lines"]), (34, 29, 14))
        self.assertEqual((p["total_ru_text_entries"], p["source_total_text_entries"]), (77, 141))
        self.assertFalse(p["complete"])
        self.assertIn("SCENE_NOT_COMPLETE", d["status"])
        self.assertIn("NOT_PATCHABLE", d["status"])
        self.assertEqual(d["source_file"], "activities/act33side/level_act33side_st01.txt")
        self.assertEqual(d["segment_v049"]["source_line_start"], self.old["progress"]["next_source_line"])
        self.assertEqual(d["segment_v049"]["source_line_end"], 194)
        for key in ("dialogues", "plain_dialogues", "sticker_texts"):
            for ordinal, text in self.old[key].items():
                self.assertEqual(d[key][ordinal], text)
        self.assertEqual(d["segment_v049"]["new_named_ru_lines"], 13)
        self.assertEqual(d["segment_v049"]["new_plain_ru_lines"], 14)
        self.assertEqual(d["segment_v049"]["new_sticker_ru_lines"], 0)

    def test_ordinals_and_source_positions(self):
        d = self.d
        s = d["segment_v049"]
        self.assertEqual(s["named_source_lines"], [126,133,135,136,137,145,147,157,178,179,180,181,188])
        self.assertEqual(s["plain_source_lines"], [129,139,140,141,142,143,149,151,152,158,161,162,163,174])
        self.assertEqual(len(set(s["named_source_lines"] + s["plain_source_lines"])), 27)
        for key, count in (("dialogues", 34), ("plain_dialogues", 29), ("sticker_texts", 14)):
            entries = d[key]
            self.assertEqual(set(entries), {str(i) for i in range(1, count + 1)})
            for entry in entries.values():
                ru = entry if isinstance(entry, str) else entry["ru"]
                self.assertTrue(isinstance(ru, str) and ru.strip())
                self.assertFalse(any(c in ru for c in "\r\n\t"))

    def test_pinned_sources_index_and_chronology(self):
        d = self.d
        a = load("reports/BABEL_ST01_SOURCE_AUDIT_v049.json")
        m = load("chronology/CHRONOLOGY_MANIFEST_v049.json")
        idx = (ROOT / "events/BABEL_INDEX_v049.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual((d["source"]["cn_git_blob_sha1"], d["source"]["en_git_blob_sha1"]),
                         ("b892ff9507ab142d39a0ea18876444c3269ec055",
                          "359381b0e52bae2a7811211ba908aeee0288b5f1"))
        for lang in ("cn", "en"):
            self.assertEqual(a["sources"][lang]["git_blob_sha1"], d["source"][lang+"_git_blob_sha1"])
            self.assertRegex(a["sources"][lang]["git_blob_sha1"], r"^[0-9a-f]{40}$")
        self.assertTrue(a["alignment"]["source_version_match_v048"])
        self.assertTrue(a["alignment"]["prefix_text_kind_order_identical"])
        self.assertFalse(a["translation"]["complete_scene"])
        self.assertEqual(m["next_file"], d["source_file"])
        self.assertEqual(m["translation_integrity"]["babel_completed_files"], 0)
        self.assertEqual(m["translation_integrity"]["babel_partial_ru_text_entries"], 77)
        self.assertEqual(len(idx), 24)
        self.assertIn("level_act33side_st01.txt\tpartial_first_draft\t34\t29\t14", idx[1])

if __name__ == "__main__":
    unittest.main()
