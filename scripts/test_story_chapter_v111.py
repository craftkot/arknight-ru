# coding: utf-8
"""Regression tests for completed 5-10 before-battle v1.11."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-10_beg.txt"
NEW = "story/story_chapter_5_stage_5-10_before_ru_v111.json"

def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

class Chapter510BeforeV111(unittest.TestCase):
    def test_complete_entries_choices_and_source_hashes(self):
        c = load(NEW)["files"][REL]
        self.assertEqual((c["dialogue_count"], c["named_dialogue_count"], c["empty_speaker_dialogue_count"], c["unnamed_dialogue_count"]), (247, 245, 2, 1))
        self.assertEqual(set(c["dialogues"]), {str(i) for i in range(1, 248)})
        self.assertEqual(len(c["source_dialogue_line_numbers"]), 247)
        self.assertEqual((c["source_dialogue_line_numbers"]["158"], c["source_dialogue_line_numbers"]["173"], c["source_dialogue_line_numbers"]["174"], c["source_dialogue_line_numbers"]["247"]), (484, 524, 525, 665))
        self.assertEqual(c["bare_narration_by_source_line"], {"523": "За несколько минут до этого…"})
        self.assertEqual({k: len(v) for k, v in c["decisions"].items()}, {"1": 3, "2": 1, "3": 3, "4": 1, "5": 1, "6": 1})
        self.assertTrue(all(v.strip() and not any(x in v for x in "\r\n\t") for v in c["dialogues"].values()))
        self.assertEqual((c["cn_git_blob_sha1"], c["en_git_blob_sha1"]), ("922973f06fdda4acb1ad0207ef2ae6f07e3472f1", "dbf64cfdcc8e97b720398c386000477d0da81ea8"))
        self.assertIn("{@nickname}", c["dialogues"]["247"])

    def test_prior_157_unchanged_and_selection(self):
        old = load("story/story_chapter_5_stage_5-10_before_partial_ru_v110.json")
        c = load(NEW)["files"][REL]
        self.assertEqual({k: c["dialogues"][k] for k in old["dialogues"]}, old["dialogues"])
        self.assertEqual({k: c["source_dialogue_line_numbers"][k] for k in old["source_dialogue_line_numbers"]}, old["source_dialogue_line_numbers"])
        prev = load("story/story_main_selection_ru_v107.json")
        sel = load("story/story_main_selection_ru_v111.json")
        self.assertEqual((len(prev["files"]), len(sel["files"])), (94, 95))
        self.assertEqual(set(sel["files"]) - set(prev["files"]), {REL})
        for k, v in prev["files"].items():
            self.assertEqual(sel["files"][k], v)
        self.assertEqual(sel["files"][REL], c)
        self.assertEqual(sum(x["dialogue_count"] for x in sel["files"].values()), 5987)
        self.assertEqual(sum(x["dialogue_count"] + len(x.get("bare_narration_by_source_line", {})) for x in sel["files"].values()), 5988)

    def test_manifest_index_audit_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v111.json")
        q = load("reports/QA_MAIN_STORY_v111.json")
        a = load("reports/CHAPTER_5_STAGE_5-10_BEFORE_SOURCE_AUDIT_v111.json")["alignment"]
        self.assertEqual((m["next_file"], m["translation_integrity"]["main_story_files"]), ("obt/main/level_main_05-10_end.txt", 95))
        self.assertEqual((m["translation_integrity"]["main_story_named_ru_lines"], m["translation_integrity"]["main_story_text_entries_including_unnamed"]), (5950, 5988))
        self.assertEqual((q["new_tagged_ru"], q["new_choice_options_ru"], q["scene_remaining_text_entries"]), (90, 10, 0))
        self.assertEqual((a["cn_tagged"], a["en_tagged"], a["cn_bracket_commands"], a["en_bracket_commands"]), (247, 247, 425, 425))
        self.assertEqual((a["cn_empty_speaker"], a["cn_bare"], a["source_choice_options"]), (2, 1, 10))
        self.assertTrue(a["cn_en_non_decision_command_text_equal"])
        self.assertIn("level_main_05-10_beg.txt\tfirst_draft_complete\t245\t3\t248", (ROOT / "story/CHAPTER_5_INDEX_v111.tsv").read_text(encoding="utf-8"))

    def test_preview_patches_choices_and_bare_without_commands(self):
        c = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        lines = ["[Dialog]"] * 673
        for ordinal in range(1, 248):
            pos = c["source_dialogue_line_numbers"][str(ordinal)] - 1
            name = "" if ordinal in (173, 174) else "Ch'en"
            tokens = " ".join(ap.quoted_tokens(c["dialogues"][str(ordinal)]))
            lines[pos] = '[name="' + name + '"]  EN sample ' + tokens
        lines[522] = "A few minutes ago..."
        for i, ln in enumerate((528, 629, 643, 648, 666, 668), 1):
            n = len(c["decisions"][str(i)])
            lines[ln - 1] = '[Decision(options="' + ";".join("EN" + str(x) for x in range(n)) + '", values="' + ";".join(str(x + 1) for x in range(n)) + '")]'
        lines[500] = '[PlaySound(key="$test")]'
        raw = "\n".join(lines) + "\n"
        patched, count = ap.patch_bytes(raw.encode("utf-8"), c["dialogues"], ru_choices=c["decisions"], bare_by_line=c["bare_narration_by_source_line"])
        txt = patched.decode("utf-8").splitlines()
        self.assertEqual(count, 247)
        self.assertEqual(txt[522], "За несколько минут до этого…")
        self.assertEqual(txt[500], lines[500])
        self.assertIn("Blaze", ap.SPEAKER_RU)
        self.assertIn("«Родос Айленд», слушайте мой приказ.", txt[665])
        self.assertIn("04:21", txt[523])
        self.assertEqual(len(txt), 673)

if __name__ == "__main__":
    unittest.main()
