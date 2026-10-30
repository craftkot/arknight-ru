# coding: utf-8
"""v0.64: CN-primary 3-7 after battle, preservation and safe local preview."""
import copy
import csv
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_story as ap

REL = "obt/main/level_main_03-07_end.txt"
NEW = "story/story_chapter_3_stage_3-7_after_ru_v064.json"
CN = "16be90a2b08049f419f219642c88e11ded8bf8de"
EN = "1e294478d30ad50aac8701865d1233c15492734c"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter3Stage37AfterV064(unittest.TestCase):
    def test_full_scene_and_source_pins(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.64")
        self.assertEqual(set(doc["files"]), {REL})
        scene = doc["files"][REL]
        self.assertEqual(scene["dialogue_count"], 78)
        self.assertEqual(set(scene["dialogues"]), set(map(str, range(1, 79))))
        self.assertEqual((scene["cn_git_blob_sha1"], scene["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        for line in scene["dialogues"].values():
            self.assertTrue(isinstance(line, str) and line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
            self.assertFalse(ap.INLINE.findall(line))
        self.assertIn("втором этаже", scene["dialogues"]["16"])
        self.assertIn("сжимайте кольцо", scene["dialogues"]["75"])
        self.assertEqual(scene["dialogues"]["78"], "Нет…")

    def test_selection_preserves_previous_57_files(self):
        old = load("story/story_main_selection_ru_v063.json")
        new = load("story/story_main_selection_ru_v064.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (57, 58))
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 3392)
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_metadata_and_qa(self):
        with (ROOT / "story/CHAPTER_3_INDEX_v064.tsv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        self.assertEqual(len(rows), 14)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows), 1015)
        self.assertEqual((rows[-1]["source_filename"], rows[-1]["ru_status"], rows[-1]["dialogues_ru_count"]),
                         ("level_main_03-07_end.txt", "first_draft_complete", "78"))
        self.assertEqual((rows[-1]["cn_git_blob_sha1"], rows[-1]["en_git_blob_sha1"]), (CN, EN))
        m = load("chronology/CHRONOLOGY_MANIFEST_v064.json")
        stats = m["translation_integrity"]
        self.assertEqual((stats["main_story_files"], stats["main_story_named_ru_lines"]), (58, 3392))
        self.assertEqual((stats["main_story_chapter_3_files"], stats["main_story_chapter_3_named_ru_lines"]), (14, 1015))
        self.assertEqual(stats["main_story_chapter_3_stages_completed"], 7)
        self.assertEqual(stats["main_story_chapter_3_partial_named_ru_lines"], 0)
        self.assertEqual(m["next_file"], "obt/main/level_main_03-08_beg.txt")
        qa = load("reports/QA_MAIN_STORY_v064.json")
        self.assertEqual((qa["new_named_ru"], qa["source_named_total"]), (78, 78))
        self.assertEqual(qa["source_named_remaining"], 0)
        self.assertTrue(qa["included_in_complete_story_selection"])
        self.assertFalse(qa["in_game_test"])
        audit = load("reports/CHAPTER_3_STAGE_3-7_AFTER_SOURCE_AUDIT_v064.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (78, 78))
        self.assertTrue(audit["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["non_dialogue_source_lines_equal_after_ignoring_terminal_newline"])
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))

    def test_safe_preview_preserves_all_commands_and_rejects_wrong_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = copy.deepcopy(load(NEW))
            speakers = ["Reunion Member", "Hoshiguma", "Franka", "Liskarm",
                        "Exusiai", "Texas", "Reunion Caster", "Amiya",
                        "L.G.D. Agent", "Ch'en", "Skullshatterer"]
            lines = ['[HEADER(key="test", is_skippable=true)]\n',
                     '[Background(image="bg_wild_a")]\n',
                     '[PlayMusic(key="$mist_loop")]\n']
            for i in range(1, 79):
                lines.append('[Character(name="char_test")]\n')
                lines.append('[name="' + speakers[(i-1) % len(speakers)] + '"]   EN line ' + str(i) + '\n')
                if i % 6 == 0:
                    lines.append('[CameraShake(duration=0.5)]\n')
                if i % 8 == 0:
                    lines.append('[Dialog]\n')
            lines.extend(['[Blocker(block=true)]\n', '[Image]'])
            original = "".join(lines).encode("utf-8")
            for lang in ("cn", "en"):
                p = root / "source" / lang / REL
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(original)
                doc["files"][REL][lang + "_git_blob_sha1"] = ap.git_blob_sha1(original)
            draft = root / "draft.json"
            draft.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
            result = ap.build(root / "source", root / "preview", draft)
            self.assertEqual(result["lines_total"], 78)
            before = original.decode("utf-8").splitlines()
            after = (root / "preview" / "ru" / REL).read_text("utf-8").splitlines()
            self.assertEqual(len(before), len(after))
            for a, b in zip(before, after):
                if not ap.SPEAKER.search(a):
                    self.assertEqual(a, b)
            self.assertIn('[name="Крушитель Черепов"]', "\n".join(after))
            self.assertTrue(any("сжимайте кольцо" in x for x in after))
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                ap.build(root / "source", root / "rejected", ROOT / NEW)
            self.assertFalse((root / "rejected").exists())

if __name__ == "__main__":
    unittest.main()
