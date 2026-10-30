# coding: utf-8
"""v0.61: CN-primary first draft of all 70 lines in main story 3-6 after battle."""
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

REL = "obt/main/level_main_03-06_end.txt"
NEW = "story/story_chapter_3_stage_3-6_after_ru_v061.json"
CN_SHA = "eb92638f81f83d6f28a4e6b03a3ba56754fcee02"
EN_SHA = "e69574b297a03fc71abc9affe35a38c00da497e8"

def load(path):
    return json.loads((ROOT / path).read_text("utf-8"))

class Chapter3Stage36AfterV061(unittest.TestCase):
    def test_complete_source_pinned_draft(self):
        doc = load(NEW)
        self.assertEqual(doc["version"], "v0.61")
        self.assertEqual(set(doc["files"]), {REL})
        record = doc["files"][REL]
        self.assertEqual(record["dialogue_count"], 70)
        self.assertEqual(set(record["dialogues"]), set(map(str, range(1, 71))))
        self.assertEqual((record["cn_git_blob_sha1"], record["en_git_blob_sha1"]), (CN_SHA, EN_SHA))
        self.assertIsNotNone(re.fullmatch(ap.ALLOWED_PATH, REL))
        for item in record["dialogues"].values():
            self.assertTrue(isinstance(item, str) and item.strip())
            self.assertFalse(any(ch in item for ch in "\r\n\t"))
            self.assertFalse(ap.INLINE.findall(item))
        self.assertIn("прикрывать отход", record["dialogues"]["32"])
        self.assertIn("на произвол судьбы", record["dialogues"]["46"])
        self.assertEqual(record["dialogues"]["49"], "—")
        self.assertEqual(record["dialogues"]["68"], "Крушителя Черепов…")
        self.assertEqual(record["dialogues"]["69"], "…")
        self.assertEqual(record["dialogues"]["70"], "Я должна…")
        self.assertNotIn("наследи", record["dialogues"]["70"].lower())

    def test_previous_55_records_unchanged(self):
        old = load("story/story_main_selection_ru_v060.json")
        new = load("story/story_main_selection_ru_v061.json")
        self.assertEqual((len(old["files"]), len(new["files"])), (55, 56))
        self.assertEqual(sum(v["dialogue_count"] for v in new["files"].values()), 3259)
        self.assertEqual(set(new["files"]) - set(old["files"]), {REL})
        for key, value in old["files"].items():
            self.assertEqual(value, new["files"][key])
        self.assertEqual(new["files"][REL], load(NEW)["files"][REL])

    def test_preview_preserves_non_dialogue_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = copy.deepcopy(load(NEW))
            lines = [
                '[HEADER(key="title_test", is_skippable=true)]\n',
                '[Background(image="bg_wild_a")]\n',
                '[PlayMusic(key="$loading_loop")]\n',
            ]
            speakers = ["Reunion Member", "W", "Misha"]
            for i in range(70):
                lines.append('[Character(name="char_012_misa_1")]\n')
                lines.append('[name="' + speakers[i % 3] + '"] EN line ' + str(i + 1) + '\n')
                if i % 7 == 0:
                    lines.append("[Delay(time=0.1)]\n")
                if i % 9 == 0:
                    lines.append("[Dialog]\n")
            lines.extend(["[Blocker(block=true)]\n", "[Image]"])
            original = "".join(lines).encode("utf-8")
            for lang in ("cn", "en"):
                path = root / "source" / lang / REL
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(original)
                doc["files"][REL][lang + "_git_blob_sha1"] = ap.git_blob_sha1(original)
            draft = root / "draft.json"
            draft.write_text(json.dumps(doc, ensure_ascii=False), "utf-8")
            result = ap.build(root / "source", root / "preview", draft)
            self.assertEqual(result["lines_total"], 70)
            before = original.decode("utf-8").splitlines()
            after = (root / "preview" / "ru" / REL).read_text("utf-8").splitlines()
            self.assertEqual(len(before), len(after))
            for a, b in zip(before, after):
                if not ap.SPEAKER.search(a):
                    self.assertEqual(a, b)
            self.assertIn('[name="Боец Воссоединения"]', "\n".join(after))
            self.assertIn('[name="Миша"]', "\n".join(after))
            self.assertTrue(any("Я должна…" in x for x in after))
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                ap.build(root / "source", root / "rejected", ROOT / NEW)
            self.assertFalse((root / "rejected").exists())

    def test_index_chronology_audit_qa(self):
        with (ROOT / "story/CHAPTER_3_INDEX_v061.tsv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        self.assertEqual(len(rows), 13)
        self.assertEqual(sum(int(r["dialogues_ru_count"]) for r in rows), 882)
        self.assertEqual(rows[-2]["source_filename"], "level_main_03-06_end.txt")
        self.assertEqual((rows[-2]["ru_status"], rows[-2]["dialogues_ru_count"]), ("first_draft_complete", "70"))
        self.assertEqual((rows[-2]["cn_git_blob_sha1"], rows[-2]["en_git_blob_sha1"]), (CN_SHA, EN_SHA))
        self.assertEqual((rows[-1]["source_filename"], rows[-1]["ru_status"]), ("level_main_03-07_beg.txt", "not_translated"))
        m = load("chronology/CHRONOLOGY_MANIFEST_v061.json")
        self.assertEqual((m["translation_integrity"]["main_story_files"], m["translation_integrity"]["main_story_named_ru_lines"]), (56, 3259))
        self.assertEqual((m["translation_integrity"]["main_story_chapter_3_files"], m["translation_integrity"]["main_story_chapter_3_named_ru_lines"]), (12, 882))
        self.assertEqual(m["translation_integrity"]["main_story_chapter_3_stages_completed"], 6)
        self.assertEqual(m["next_file"], "obt/main/level_main_03-07_beg.txt")
        qa = load("reports/QA_MAIN_STORY_v061.json")
        self.assertEqual((qa["new_named_ru"], qa["total_named_ru"]), (70, 3259))
        self.assertFalse(qa["in_game_test"])
        audit = load("reports/CHAPTER_3_STAGE_3-6_AFTER_SOURCE_AUDIT_v061.json")
        self.assertTrue(audit["alignment"]["cn_en_dialogue_source_line_positions_equal"])
        self.assertTrue(audit["alignment"]["non_dialogue_source_lines_equal"])
        self.assertEqual((audit["alignment"]["cn_named"], audit["alignment"]["en_named"]), (70, 70))
        self.assertEqual((audit["alignment"]["source_line_count_cn"], audit["alignment"]["source_line_count_en"]), (123, 123))
        self.assertEqual((audit["sources"]["cn"]["git_blob_sha1"], audit["sources"]["en"]["git_blob_sha1"]), (CN_SHA, EN_SHA))
        self.assertEqual(audit["alignment"]["cn_decision_commands"], 0)
        self.assertEqual(audit["alignment"]["en_decision_commands"], 0)

if __name__ == "__main__":
    unittest.main()
