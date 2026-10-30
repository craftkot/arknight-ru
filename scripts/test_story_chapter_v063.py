# coding: utf-8
"""v0.63: 3-7 before-battle complete draft; preservation and preview safety."""
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

REL = "obt/main/level_main_03-07_beg.txt"
NEW = "story/story_chapter_3_stage_3-7_before_ru_v063.json"
OLD_PARTIAL = "story/story_chapter_3_stage_3-7_before_partial_ru_v062.json"
CN = "5d3bf7deb9bc1a286ee7f8b8f4817f6893a0eed3"
EN = "f682ae658542d594d0bcc474c0201e86d9a22ec7"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class Chapter3Stage37BeforeV063(unittest.TestCase):
    def test_complete_and_preserve_prior_partial(self):
        doc = load(NEW)
        partial = load(OLD_PARTIAL)["files"][REL]
        self.assertEqual(doc["version"], "v0.63")
        self.assertEqual(set(doc["files"]), {REL})
        record = doc["files"][REL]
        self.assertEqual(record["dialogue_count"], 55)
        self.assertEqual(set(record["dialogues"]), set(map(str, range(1, 56))))
        self.assertEqual((record["cn_git_blob_sha1"], record["en_git_blob_sha1"]), (CN, EN))
        for i in range(1, 21):
            self.assertEqual(record["dialogues"][str(i)], partial["dialogues"][str(i)])
        for i, text in record["dialogues"].items():
            self.assertTrue(isinstance(text, str) and text.strip())
            self.assertFalse(any(ch in text for ch in "\r\n\t"))
            if i != "53":
                self.assertFalse(ap.INLINE.findall(text))
        self.assertEqual(ap.INLINE.findall(record["dialogues"]["53"]), ["{@nickname}"])
        self.assertIn("по закону", record["dialogues"]["37"])
        self.assertIn("Пингвин Логистикс", record["dialogues"]["48"])
        self.assertTrue(re.fullmatch(ap.ALLOWED_PATH, REL))

    def test_full_selection_preserves_previous_56(self):
        old = load("story/story_main_selection_ru_v061.json")
        new = load("story/story_main_selection_ru_v063.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (56, 57))
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 3314)
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_index_chronology_qa_and_audit(self):
        with (ROOT / "story/CHAPTER_3_INDEX_v063.tsv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        self.assertEqual(len(rows), 13)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows), 937)
        self.assertEqual((rows[-1]["source_filename"], rows[-1]["ru_status"], rows[-1]["dialogues_ru_count"]),
                         ("level_main_03-07_beg.txt", "first_draft_complete", "55"))
        self.assertEqual((rows[-1]["cn_git_blob_sha1"], rows[-1]["en_git_blob_sha1"]), (CN, EN))
        m = load("chronology/CHRONOLOGY_MANIFEST_v063.json")
        stats = m["translation_integrity"]
        self.assertEqual((stats["main_story_files"], stats["main_story_named_ru_lines"]), (57, 3314))
        self.assertEqual((stats["main_story_chapter_3_files"], stats["main_story_chapter_3_named_ru_lines"]), (13, 937))
        self.assertEqual(stats["main_story_chapter_3_partial_named_ru_lines"], 0)
        self.assertEqual(stats["main_story_chapter_3_stages_completed"], 6)
        self.assertEqual(m["next_file"], "obt/main/level_main_03-07_end.txt")
        qa = load("reports/QA_MAIN_STORY_v063.json")
        self.assertEqual((qa["new_named_ru"], qa["source_named_total"]), (35, 55))
        self.assertEqual(qa["source_named_remaining"], 0)
        self.assertTrue(qa["included_in_complete_story_selection"])
        self.assertFalse(qa["in_game_test"])
        audit = load("reports/CHAPTER_3_STAGE_3-7_BEFORE_SOURCE_AUDIT_v063.json")
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (55, 55))
        self.assertTrue(audit["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["non_dialogue_source_lines_equal_after_ignoring_terminal_newline"])
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN, EN))

    def test_preview_preserves_commands_and_nickname(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = copy.deepcopy(load(NEW))
            speakers = ["Franka", "Hoshiguma", "Liskarm", "Reunion Member", "Amiya", "Texas"]
            lines = ['[HEADER(key="test", is_skippable=true)]\n', '[Background(image="bg_test")]\n']
            for i in range(1, 56):
                lines.append('[Character(name="char_test")]\n')
                text = "Doctor {@nickname}, scout ahead!" if i == 53 else "EN line " + str(i)
                lines.append('[name="' + speakers[(i-1) % len(speakers)] + '"]   ' + text + '\n')
                if i % 5 == 0:
                    lines.append('[Delay(time=0.1)]\n')
                if i % 7 == 0:
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
            self.assertEqual(result["lines_total"], 55)
            before = original.decode("utf-8").splitlines()
            after = (root / "preview" / "ru" / REL).read_text("utf-8").splitlines()
            self.assertEqual(len(before), len(after))
            for a, b in zip(before, after):
                if not ap.SPEAKER.search(a):
                    self.assertEqual(a, b)
            self.assertTrue(any("Доктор {@nickname}" in x for x in after))
            self.assertTrue(any('[name="Хосигума"]' in x for x in after))
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                ap.build(root / "source", root / "rejected", ROOT / NEW)
            self.assertFalse((root / "rejected").exists())

if __name__ == "__main__":
    unittest.main()
