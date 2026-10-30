# coding: utf-8
"""v0.65: verify complete 3-8 opening, source pins, preservation and safe preview."""
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

REL = "obt/main/level_main_03-08_beg.txt"
NEW = "story/story_chapter_3_stage_3-8_before_ru_v065.json"
CN = "9d435d88bcefca622e04b7590fb9eeb9a91e4ae3"
EN = "f8e82127f69225bf8bc8c141c78661b5d27acc3f"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter3Stage38BeforeV065(unittest.TestCase):
    def test_full_scene_and_source_pins(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.65")
        self.assertEqual(set(doc["files"]), {REL})
        scene = doc["files"][REL]
        self.assertEqual(scene["dialogue_count"], 69)
        self.assertEqual(set(scene["dialogues"]), set(map(str, range(1, 70))))
        self.assertEqual((scene["cn_git_blob_sha1"], scene["en_git_blob_sha1"]), (CN, EN))
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertEqual(scene["decisions"], {"1": ["Делай то, что должна, Амия."]})
        for line in scene["dialogues"].values():
            self.assertTrue(isinstance(line, str) and line.strip())
            self.assertFalse(any(ch in line for ch in "\r\n\t"))
            self.assertFalse(ap.INLINE.findall(line))
        self.assertIn("сражаться до самого конца", scene["dialogues"]["17"])
        self.assertEqual(scene["dialogues"]["46"], "Но я…")
        self.assertIn("твои враги", scene["dialogues"]["65"])

    def test_selection_preserves_all_previous_files(self):
        old = load("story/story_main_selection_ru_v064.json")
        new = load("story/story_main_selection_ru_v065.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (58, 59))
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 3461)
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_index_chronology_audit_qa(self):
        with (ROOT / "story/CHAPTER_3_INDEX_v065.tsv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        self.assertEqual(len(rows), 15)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows), 1084)
        self.assertEqual((rows[-1]["source_filename"], rows[-1]["ru_status"], rows[-1]["dialogues_ru_count"]),
                         ("level_main_03-08_beg.txt", "first_draft_complete", "69"))
        self.assertEqual((rows[-1]["cn_git_blob_sha1"], rows[-1]["en_git_blob_sha1"]), (CN, EN))
        m = load("chronology/CHRONOLOGY_MANIFEST_v065.json")
        stats = m["translation_integrity"]
        self.assertEqual((stats["main_story_files"], stats["main_story_named_ru_lines"]), (59, 3461))
        self.assertEqual((stats["main_story_chapter_3_files"], stats["main_story_chapter_3_named_ru_lines"]), (15, 1084))
        self.assertEqual(stats["main_story_chapter_3_stages_completed"], 7)
        self.assertEqual(m["next_file"], "obt/main/level_main_03-08_end.txt")
        qa = load("reports/QA_MAIN_STORY_v065.json")
        self.assertEqual((qa["new_named_ru"], qa["source_named_total"]), (69, 69))
        self.assertEqual(qa["source_named_remaining"], 0)
        self.assertTrue(qa["included_in_complete_story_selection"])
        self.assertFalse(qa["in_game_test"])
        audit = load("reports/CHAPTER_3_STAGE_3-8_BEFORE_SOURCE_AUDIT_v065.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (69, 69))
        self.assertTrue(audit["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["non_dialogue_source_lines_equal_after_ignoring_terminal_newline"])
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))
        self.assertEqual(audit["alignment"]["decision_option_counts"], [1])

    def test_preview_preserves_commands_and_choice_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = copy.deepcopy(load(NEW))
            speakers = ["Reunion Member", "Skullshatterer", "Hoshiguma", "Franka",
                        "L.G.D. Agent", "Ch'en", "Amiya"]
            lines = ['[HEADER(key="test", is_skippable=true)]\n',
                     '[Background(image="bg_wild_a")]\n']
            for i in range(1, 70):
                lines.append('[Character(name="char_test")]\n')
                lines.append('[name="' + speakers[(i - 1) % len(speakers)] + '"]   EN line ' + str(i) + '\n')
                if i == 45:
                    lines.append('[Decision(options="You know what you have to do, Amiya.", values="1")]\n')
                    lines.append('[Predicate(references="1")]\n')
                if i % 8 == 0:
                    lines.append('[CameraShake(duration=0.5)]\n')
            lines.append('[Image]\n')
            original = "".join(lines).encode("utf-8")
            for lang in ("cn", "en"):
                p = root / "source" / lang / REL
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(original)
                doc["files"][REL][lang + "_git_blob_sha1"] = ap.git_blob_sha1(original)
            draft = root / "draft.json"
            draft.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
            result = ap.build(root / "source", root / "preview", draft)
            self.assertEqual(result["lines_total"], 69)
            before = original.decode("utf-8").splitlines()
            after = (root / "preview" / "ru" / REL).read_text("utf-8").splitlines()
            self.assertEqual(len(before), len(after))
            for a, b in zip(before, after):
                if not ap.SPEAKER.search(a) and not ap.DECISION.search(a):
                    self.assertEqual(a, b)
            self.assertTrue(any("Делай то, что должна, Амия." in x for x in after))
            self.assertIn('[Predicate(references="1")]', after)
            self.assertTrue(any("сражаться до самого конца" in x for x in after))
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                ap.build(root / "source", root / "rejected", ROOT / NEW)
            self.assertFalse((root / "rejected").exists())

if __name__ == "__main__":
    unittest.main()
