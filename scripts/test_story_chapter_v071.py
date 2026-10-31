# coding: utf-8
"""v0.71: complete 4-2 after-battle draft, including nine bare narration lines."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_04-02_end.txt"
NEW = "story/story_chapter_4_stage_4-2_after_ru_v071.json"
CN = "23e3e402e87a0c23b3bac428b01c681657630a8e"
EN = "492aa64e5659dc935c0d487755d6ae730c926422"
BARE = {55, 58, 60, 61, 64, 66, 69, 70, 71}

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter42AfterV071(unittest.TestCase):
    def test_full_104_positions_and_hashes(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.71")
        self.assertEqual(set(doc["files"]), {REL})
        scene = doc["files"][REL]
        self.assertEqual((scene["dialogue_count"], scene["named_dialogue_count"], scene["unnamed_dialogue_count"]), (104, 95, 9))
        self.assertEqual(set(scene["dialogues"]), set(map(str, range(1, 105))))
        self.assertEqual((scene["cn_git_blob_sha1"], scene["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertNotIn("decisions", scene)
        for line in scene["dialogues"].values():
            self.assertIsInstance(line, str)
            self.assertTrue(line.strip())
            self.assertFalse(any(c in line for c in "\r\n\t"))
        self.assertIn("граммофон", scene["dialogues"]["19"])
        self.assertIn("сестрёнка-кролик", scene["dialogues"]["45"])
        self.assertTrue(scene["dialogues"]["71"].startswith("Только"))
        self.assertIn("Чэнь", scene["dialogues"]["99"])

    def test_previous_63_scenes_unchanged(self):
        old = load("story/story_main_selection_ru_v070.json")
        new = load("story/story_main_selection_ru_v071.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (63, 64))
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        self.assertEqual(sum(x["dialogue_count"] for x in new["files"].values()), 3882)
        for key, value in old["files"].items():
            self.assertEqual(new["files"][key], value)
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_audit_index_chronology_qa(self):
        audit = load("reports/CHAPTER_4_STAGE_4-2_AFTER_SOURCE_AUDIT_v071.json")
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        align = audit["alignment"]
        self.assertEqual((align["cn_named"], align["cn_unnamed"], align["ru_complete_text_entries"]), (95, 9, 104))
        self.assertTrue(align["cn_en_text_source_line_positions_equal"])
        self.assertTrue(align["cn_en_non_dialogue_commands_equal_excluding_header_and_decision_text"])
        manifest = load("chronology/CHRONOLOGY_MANIFEST_v071.json")
        totals = manifest["translation_integrity"]
        self.assertEqual(manifest["next_file"], "obt/main/level_main_04-03_beg.txt")
        self.assertEqual((totals["main_story_files"], totals["main_story_named_ru_lines"]), (64, 3866))
        self.assertEqual((totals["main_story_chapter_4_files"], totals["main_story_chapter_4_named_ru_lines"], totals["main_story_chapter_4_unnamed_ru_lines"]), (4, 335, 16))
        qa = load("reports/QA_MAIN_STORY_v071.json")
        self.assertEqual((qa["new_text_entries"], qa["completed_story_files"]), (104, 64))
        self.assertFalse(qa["in_game_test"])
        idx = (ROOT / "story/CHAPTER_4_INDEX_v071.tsv").read_text(encoding="utf-8")
        self.assertIn("level_main_04-02_end.txt\tfirst_draft_complete\t95\t9\t104", idx)

    def test_safe_preview_bare_narration_and_commands(self):
        translations = load(NEW)["files"][REL]["dialogues"]
        lines = ['[HEADER(key="test")]\n']
        for i in range(1, 105):
            if i in BARE:
                lines.append("Original bare narration " + str(i) + "\n")
            else:
                name = "Little Girl" if i in (78, 79, 85, 86, 87, 88) else ("Another Girl's Voice" if i in (80, 89) else "Amiya")
                lines.append('[name="' + name + '"] EN ' + str(i) + '\n')
            if i % 9 == 0:
                lines.append('[CameraShake(duration=0.5)]\n')
        source = "".join(lines).encode("utf-8")
        self.assertEqual(len(ap.dialogues_in_text(source, include_bare=True)), 104)
        self.assertEqual(len(ap.dialogues_in_text(source)), 95)
        patched, count = ap.patch_bytes(source, translations, include_bare=True)
        self.assertEqual(count, 104)
        before = source.decode().splitlines()
        after = patched.decode().splitlines()
        self.assertEqual(len(before), len(after))
        for x, y in zip(before, after):
            if x.startswith("[CameraShake") or x.startswith("[HEADER"):
                self.assertEqual(x, y)
        self.assertTrue(any("Люди, лишённые" in x for x in after))
        self.assertTrue(any('name="Маленькая девочка"' in x for x in after))
        self.assertTrue(any('name="Голос другой девушки"' in x for x in after))
        with self.assertRaises(ValueError):
            ap.patch_bytes(source, translations)  # explicit opt-in required

if __name__ == "__main__":
    unittest.main()
