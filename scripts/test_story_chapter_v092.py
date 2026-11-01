# coding: utf-8
"""Regression tests for main story 5-2 before battle, v0.92."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_05-02_beg.txt"
NEW = "story/story_chapter_5_stage_5-2_before_ru_v092.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter52BeforeV092(unittest.TestCase):
    def test_complete_source_counts_and_hashes(self):
        cfg = load(NEW)["files"][REL]
        self.assertEqual((cfg["dialogue_count"], cfg["named_dialogue_count"], cfg["unnamed_dialogue_count"]), (85, 84, 1))
        self.assertEqual(set(cfg["dialogues"]), set(map(str, range(1, 86))))
        self.assertEqual(cfg["cn_git_blob_sha1"], "e77cf7669234275220faaf9332bb86018f038075")
        self.assertEqual(cfg["en_git_blob_sha1"], "d153d256fe0081062392357b10b9b34f8d200cb2")
        self.assertEqual(cfg["dialogues"]["22"], "Стук в дверь.")
        for value in cfg["dialogues"].values():
            self.assertTrue(value.strip())
            self.assertFalse(any(ch in value for ch in "\\r\\n\\t"))

    def test_selection_preserves_previous_82(self):
        old = load("story/story_main_selection_ru_v091.json")
        new = load("story/story_main_selection_ru_v092.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (82, 83))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, val in old["files"].items():
            self.assertEqual(val, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
        self.assertEqual(sum(f["dialogue_count"] for f in new["files"].values()), 5037)

    def test_manifest_audit_index_qa(self):
        m = load("chronology/CHRONOLOGY_MANIFEST_v092.json")
        a = load("reports/CHAPTER_5_STAGE_5-2_BEFORE_SOURCE_AUDIT_v092.json")
        q = load("reports/QA_MAIN_STORY_v092.json")
        self.assertEqual(m["next_file"], "obt/main/level_main_05-02_end.txt")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (83, 5016))
        self.assertEqual((q["new_named_ru"], q["new_unnamed_ru"], q["completed_story_files"]), (84, 1, 83))
        self.assertEqual((a["alignment"]["cn_non_dialogue_commands"], a["alignment"]["en_non_dialogue_commands"]), (119, 119))
        self.assertTrue(a["alignment"]["cn_en_text_source_line_positions_equal"])
        idx = (ROOT / "story/CHAPTER_5_INDEX_v092.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_05-02_beg.txt\\tfirst_draft_complete\\t84\\t1\\t85", idx)

    def test_preview_preserves_commands_and_untagged_sound(self):
        cfg = load(NEW)["files"][REL]
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertEqual(ap.SPEAKER_RU["Ch'en"], "Чэнь")
        source = '[HEADER(key="title_test")] sample\\n' + ''.join(
            ("(*knock* *knock*)\\n" if i == 22 else '[name="Ch\\'en"]   EN line ' + str(i) + '\\n')
            for i in range(1, 86)
        ) + '[Image]\\n'
        patched, count = ap.patch_bytes(source.encode("utf-8"), cfg["dialogues"], include_bare=True)
        self.assertEqual(count, 85)
        self.assertIn("Стук в дверь.\\n", patched.decode())
        self.assertIn('[name="Чэнь"]   ' + cfg["dialogues"]["1"], patched.decode())
        self.assertIn("[Image]\\n", patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(source.encode("utf-8"), dict(list(cfg["dialogues"].items())[:-1]), include_bare=True)

if __name__ == "__main__":
    unittest.main()
