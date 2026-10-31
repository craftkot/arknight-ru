# coding: utf-8
"""v0.72: chapter 4-3 before battle; 50 CN-primary lines and five choice options."""
import json
from pathlib import Path
import re
import sys
import unittest
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap
REL = "obt/main/level_main_04-03_beg.txt"
NEW = "story/story_chapter_4_stage_4-3_before_ru_v072.json"
CN = "5ef1b5df788758e0310630246a2f9942e5e0fb50"
EN = "e7429897da0f4b9f95c21ac9a84a77961a39a1d1"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter43BeforeV072(unittest.TestCase):
    def test_complete_50_positions_choices_and_source_hashes(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.72")
        self.assertEqual(set(doc["files"]), {REL})
        scene = doc["files"][REL]
        self.assertEqual((scene["dialogue_count"], scene["named_dialogue_count"], scene["unnamed_dialogue_count"]), (50, 50, 0))
        self.assertEqual(set(scene["dialogues"]), set(map(str, range(1, 51))))
        self.assertEqual((scene["cn_git_blob_sha1"], scene["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertEqual([len(scene["decisions"][str(i)]) for i in range(1, 4)], [1, 2, 2])
        self.assertIn("{@nickname}", scene["dialogues"]["4"])
        self.assertIn("{@nickname}", scene["dialogues"]["12"])
        self.assertIn("Чэнь", scene["dialogues"]["23"])
        self.assertIn("сдамся", scene["dialogues"]["38"])
        for line in scene["dialogues"].values():
            self.assertIsInstance(line, str)
            self.assertTrue(line.strip())
            self.assertFalse(any(c in line for c in "\r\n\t"))

    def test_selection_preserves_previous_64(self):
        old = load("story/story_main_selection_ru_v071.json")
        new = load("story/story_main_selection_ru_v072.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (64, 65))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 3932)
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_index_chronology_qa(self):
        audit = load("reports/CHAPTER_4_STAGE_4-3_BEFORE_SOURCE_AUDIT_v072.json")
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        align = audit["alignment"]
        self.assertEqual((align["cn_named"], align["cn_unnamed"], align["ru_complete_text_entries"]), (50, 0, 50))
        self.assertTrue(align["cn_en_text_source_line_positions_equal"])
        self.assertTrue(align["cn_en_non_dialogue_commands_equal_excluding_header_and_decision_text"])
        self.assertEqual(align["decision_option_counts"], [1, 2, 2])
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v072.json")
        totals = manifest["translation_integrity"]
        self.assertEqual(manifest["next_file"], "obt/main/level_main_04-03_end.txt")
        self.assertEqual((totals["main_story_files"], totals["main_story_named_ru_lines"]), (65, 3916))
        self.assertEqual((totals["main_story_chapter_4_files"], totals["main_story_chapter_4_named_ru_lines"], totals["main_story_chapter_4_unnamed_ru_lines"]), (5, 385, 16))
        qa = load("reports/QA_MAIN_STORY_v072.json")
        self.assertEqual((qa["new_text_entries"], qa["completed_story_files"]), (50, 65))
        self.assertFalse(qa["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v072.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-03_beg.txt\tfirst_draft_complete\t50\t0\t50", idx)

    def test_safe_preview_preserves_commands_choices_and_variable(self):
        scene = load(NEW)["files"][REL]
        lines = ['[HEADER(key="test")]\n', '[Character(name="char_003_kalts_1")]\n']
        for i in range(1, 51):
            name = "Kal'tsit" if i <= 15 or i in (48, 49) else "Amiya"
            lines.append('[name="' + name + '"] EN ' + ('{@nickname}' if i in (4, 12) else str(i)) + '\n')
            if i in (5, 29, 31):
                j = {5: 1, 29: 2, 31: 3}[i]
                opts = {1: "She went to the slums.", 2: "Amiya has burdens.;...", 3: "You stayed true.;..."}[j]
                vals = {1: "1", 2: "1;2", 3: "1;2"}[j]
                lines.append('[Decision(options="' + opts + '", values="' + vals + '")]\n')
                lines.append('[Predicate(references="' + vals + '")]\n')
        original = "".join(lines).encode("utf-8")
        patched, count = ap.patch_bytes(original, scene["dialogues"], ru_choices=scene["decisions"])
        self.assertEqual(count, 50)
        before = original.decode().splitlines()
        after = patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith("[Predicate") or x.startswith("[Character") or x.startswith("[HEADER"):
                self.assertEqual(x, y)
            if x.startswith("[Decision"):
                self.assertEqual(x.split(', values="')[1], y.split(', values="')[1])
        self.assertTrue(any('name="Кальцит"' in x for x in after))
        self.assertTrue(any('name="Амия"' in x for x in after))
        self.assertTrue(any("{@nickname}" in x for x in after))
        self.assertIn("Амия отправилась в трущобы.", patched.decode())
        with self.assertRaises(ValueError):
            ap.patch_bytes(original, scene["dialogues"], ru_choices={"1": ["wrong"]})

if __name__ == "__main__":
    unittest.main()
