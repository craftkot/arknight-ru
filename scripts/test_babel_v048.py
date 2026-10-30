# coding: utf-8
"""Offline invariants for Babel BB-ST-1 opening, not an in-game patch."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
REL = "activities/act33side/level_act33side_st01.txt"
STICKER_LINES = [21, 24, 25, 29, 32, 33, 37, 38, 42, 43, 47, 50, 51, 52]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class BabelV048(unittest.TestCase):
    def setUp(self):
        self.d = load("events/babel_st01_opening_partial_ru_v048.json")

    def test_partial_contiguous_and_not_patchable(self):
        d = self.d
        self.assertEqual(d["source_file"], REL)
        self.assertEqual(d["version"], "v0.48-partial")
        self.assertIn("SCENE_NOT_COMPLETE", d["status"])
        self.assertIn("NOT_PATCHABLE", d["status"])
        p = d["progress"]
        self.assertFalse(p["complete"])
        self.assertEqual((p["source_lines_translated_through"], p["next_source_line"]), (114, 115))
        self.assertEqual((p["named_ru_lines"], p["plain_ru_lines"], p["sticker_ru_lines"]), (21, 15, 14))
        self.assertEqual(p["total_ru_text_entries"], 50)
        self.assertEqual(p["source_total_text_entries"], 141)
        self.assertEqual(p["next_named_ordinal"], 22)
        self.assertEqual(p["next_plain_ordinal"], 16)

    def test_all_entries_nonempty_and_ordered(self):
        d = self.d
        for key, count in [("dialogues", 21), ("plain_dialogues", 15), ("sticker_texts", 14)]:
            entries = d[key]
            self.assertEqual(set(entries), {str(i) for i in range(1, count + 1)})
            for entry in entries.values():
                ru = entry if isinstance(entry, str) else entry["ru"]
                self.assertTrue(isinstance(ru, str) and ru.strip())
                self.assertFalse(any(c in ru for c in "\\r\\n\\t"))
        self.assertEqual([d["sticker_texts"][str(i)]["source_line"] for i in range(1, 15)], STICKER_LINES)
        self.assertEqual(d["sticker_texts"]["1"]["sticker_id"], "st1")
        self.assertEqual(d["sticker_texts"]["9"]["sticker_id"], "st1")
        self.assertIn("шестеро", d["sticker_texts"]["5"]["ru"])
        self.assertIn("Аскалон", d["dialogues"]["1"])

    def test_pinned_source_metadata_and_audit(self):
        d = self.d
        a = load("reports/BABEL_ST01_SOURCE_AUDIT_v048.json")
        s = d["source"]
        self.assertEqual((s["cn_named_total"], s["en_named_total"]), (89, 89))
        self.assertEqual((s["cn_plain_total"], s["en_plain_total"]), (38, 38))
        self.assertEqual((s["cn_sticker_text_total"], s["en_sticker_text_total"]), (14, 14))
        for lang, expected in [("cn", "b892ff9507ab142d39a0ea18876444c3269ec055"),
                               ("en", "359381b0e52bae2a7811211ba908aeee0288b5f1")]:
            sha = s[f"{lang}_git_blob_sha1"]
            self.assertEqual(sha, expected)
            self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", sha))
            self.assertEqual(a["sources"][lang]["git_blob_sha1"], sha)
        self.assertFalse(a["translation"]["complete_scene"])
        self.assertFalse(a["translation"]["game_tested"])
        self.assertFalse(a["alignment"]["full_semantic_equivalence_confirmed"])

    def test_index_chronology_and_readme(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v048.json")
        idx = (ROOT / "events/BABEL_INDEX_v048.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(m["next_file"], REL)
        self.assertEqual(m["translation_integrity"]["darknights_completed_files"], 13)
        self.assertEqual(m["translation_integrity"]["babel_completed_files"], 0)
        self.assertEqual(m["translation_integrity"]["babel_partial_ru_text_entries"], 50)
        self.assertEqual(m["events"][1]["source_code"], "act33side")
        self.assertEqual(len(idx), 24)
        self.assertIn("level_act33side_st01.txt\\tpartial_first_draft\\t21\\t15\\t14", idx[1])
        self.assertIn("level_act33side_01_beg.txt", idx[2])
        self.assertIn("level_act33side_st02.txt", "\\n".join(idx))
        self.assertIn("Babel", (ROOT / "README.md").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
