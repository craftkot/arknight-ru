# coding: utf-8
"""v0.62: CN-primary first draft of 55 named lines, main story 3-7 before battle."""
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
NEW = "story/story_chapter_3_stage_3-7_before_ru_v062.json"
CN_SHA = "5d3bf7deb9bc1a286ee7f8b8f4817f6893a0eed3"
EN_SHA = "f682ae658542d594d0bcc474c0201e86d9a22ec7"
def load(path):
    return json.loads((ROOT / path).read_text("utf-8"))
class Chapter3Stage37BeforeV062(unittest.TestCase):
    def test_complete_pinned_draft(self):
        d = load(NEW)["files"][REL]
        self.assertEqual(d["dialogue_count"], 55)
        self.assertEqual(set(d["dialogues"]), set(map(str, range(1, 56))))
        self.assertEqual((d["cn_git_blob_sha1"], d["en_git_blob_sha1"]), (CN_SHA, EN_SHA))
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH, REL))
        self.assertIn("камешками", d["dialogues"]["18"])
        self.assertIn("по закону", d["dialogues"]["37"])
        self.assertIn("Пингвин Логистикс", d["dialogues"]["48"])
        self.assertEqual(ap.quoted_tokens(d["dialogues"]["53"]), ["{@nickname}"])
        for v in d["dialogues"].values():
            self.assertTrue(isinstance(v, str) and v.strip())
            self.assertFalse(any(ch in v for ch in "\r\n\t"))
    def test_previous_56_unchanged(self):
        old = load("story/story_main_selection_ru_v061.json")
        new = load("story/story_main_selection_ru_v062.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (56, 57))
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 3314)
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])
    def test_preview_preserves_non_dialogue_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = copy.deepcopy(load(NEW))
            lines = ['[HEADER(key="title_test", is_skippable=true)]\n', '[Background(image="bg_wild_a")]\n']
            names = ["Franka", "Liskarm", "Hoshiguma", "Reunion Member", "Amiya", "Texas"]
            for i in range(55):
                lines.append('[Character(name="char_107_liskam_1")]\n')
                en_line = "EN line " + str(i + 1) + (" {@nickname}" if i == 52 else "")
                lines.append('[name="' + names[i % len(names)] + '"] ' + en_line + '\n')
                if i % 7 == 0:
                    lines.append("[Delay(time=0.1)]\n")
            lines.extend(["[Blocker(block=true)]\n", "[Image]"])
            raw = "".join(lines).encode("utf-8")
            for lang in ("cn", "en"):
                path = root / "source" / lang / REL
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                doc["files"][REL][lang + "_git_blob_sha1"] = ap.git_blob_sha1(raw)
            draft = root / "draft.json"
            draft.write_text(json.dumps(doc, ensure_ascii=False), "utf-8")
            result = ap.build(root / "source", root / "preview", draft)
            self.assertEqual(result["lines_total"], 55)
            before = raw.decode("utf-8").splitlines()
            after = (root / "preview" / "ru" / REL).read_text("utf-8").splitlines()
            self.assertEqual(len(before), len(after))
            for a, b in zip(before, after):
                if not ap.SPEAKER.search(a):
                    self.assertEqual(a, b)
            self.assertTrue(any("Доктор {@nickname}" in x for x in after))
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                ap.build(root / "source", root / "rejected", ROOT / NEW)
    def test_index_chronology_and_audit(self):
        with (ROOT / "story/CHAPTER_3_INDEX_v062.tsv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        self.assertEqual(len(rows), 14)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows), 937)
        self.assertEqual((rows[-2]["ru_status"], rows[-2]["dialogues_ru_count"]), ("first_draft_complete", "55"))
        self.assertEqual((rows[-1]["source_filename"], rows[-1]["ru_status"]), ("level_main_03-07_end.txt", "not_translated"))
        m = load("chronology/CHRONOLOGY_MANIFEST_v062.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (57, 3314))
        self.assertEqual((m["translation_integrity"]["main_story_chapter_3_files"], m["translation_integrity"]["main_story_chapter_3_named_ru_lines"]), (13, 937))
        self.assertEqual(m["translation_integrity"]["main_story_chapter_3_stages_completed"], 6)
        self.assertEqual(m["next_file"], "obt/main/level_main_03-07_end.txt")
        qa = load("reports/QA_MAIN_STORY_v062.json")
        self.assertEqual((qa["new_named_ru"], qa["total_named_ru"]), (55, 3314))
        self.assertFalse(qa["in_game_test"])
        a = load("reports/CHAPTER_3_STAGE_3-7_BEFORE_SOURCE_AUDIT_v062.json")
        self.assertTrue(a["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertTrue(a["alignment"]["non_dialogue_source_lines_equal"])
        self.assertEqual((a["alignment"]["cn_named"], a["alignment"]["en_named"]), (55, 55))
        self.assertEqual((a["alignment"]["source_line_count_cn"], a["alignment"]["source_line_count_en"]), (125, 125))
        self.assertEqual((a["sources"]["cn"]["git_blob_sha1"], a["sources"]["en"]["git_blob_sha1"]), (CN_SHA, EN_SHA))
if __name__ == "__main__":
    unittest.main()
