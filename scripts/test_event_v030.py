# coding: utf-8
"""Offline checks for Darknights Memoir DM-2 after-battle draft v0.30."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as e
from apply_ru_story import git_blob_sha1

NEW = json.loads((ROOT / "events/darknights_memoir_dm2_after_ru_v030.json").read_text("utf8"))
BOTH = json.loads((ROOT / "events/darknights_memoir_dm1_dm2_ru_v030.json").read_text("utf8"))
OLD = json.loads((ROOT / "events/darknights_memoir_dm1_dm2_ru_v029.json").read_text("utf8"))
KEY = "activities/act9d0/level_act9d0_02_end.txt"

class DarknightsV030(unittest.TestCase):
    def test_new_complete_and_sequential(self):
        s = NEW["files"][KEY]
        self.assertEqual((s["dialogue_count"], s["plain_dialogue_count"]), (216, 22))
        self.assertEqual(set(s["dialogues"]), set(map(str, range(1, 217))))
        self.assertEqual(set(s["plain_dialogues"]), set(map(str, range(1, 23))))
        self.assertEqual(s["cn_git_blob_sha1"], "968822669957c22d9c4d7d0717cef94638a23078")
        self.assertEqual(s["en_git_blob_sha1"], "9ae65c962e245579bbba5c0245d24f604a954d26")
        self.assertIn("Кальцит", s["plain_dialogues"]["20"])
        self.assertIn("волосами", s["dialogues"]["216"])

    def test_old_scripts_unchanged_and_totals(self):
        self.assertEqual(len(BOTH["files"]), 4)
        for name, data in OLD["files"].items():
            self.assertEqual(BOTH["files"][name], data)
        self.assertEqual(BOTH["files"][KEY], NEW["files"][KEY])
        self.assertEqual(sum(v["dialogue_count"] for v in BOTH["files"].values()), 594)
        self.assertEqual(sum(v["plain_dialogue_count"] for v in BOTH["files"].values()), 58)
        self.assertEqual(BOTH["version"], "v0.30")

    def test_text_markup_and_new_speakers(self):
        self.assertEqual(e.SPEAKER_EVENT_RU["Sarkaz Warrior?"], "Воин-сарказ?")
        self.assertEqual(e.SPEAKER_EVENT_RU["Mercenary"], "Наёмник")
        for v in (list(NEW["files"][KEY]["dialogues"].values()) +
                  list(NEW["files"][KEY]["plain_dialogues"].values())):
            self.assertTrue(v.strip())
            self.assertNotIn("\n", v)
            self.assertNotIn("\t", v)
            self.assertEqual(e.quoted_tokens(v), [])

    def test_synthetic_full_script_and_commands(self):
        labels = ["W", "Ines", "Sarkaz Warrior", "Sarkaz Warrior?", "Mercenary", "Hoederer"]
        lines = ['[HEADER(key="test")]', '[stopmusic]']
        lines += ["NARRATIVE %s" % n for n in range(1, 23)]
        lines += ['[name="%s"]  SAMPLE %s' % (labels[(n-1) % len(labels)], n)
                  for n in range(1, 217)]
        lines += ['[playMusic(key="$mist_loop")]', '[Dialog]']
        original = ("\r\n".join(lines) + "\r\n").encode("utf8")
        converted = e.patch(original, NEW["files"][KEY])
        after = converted.decode("utf8").splitlines()
        self.assertEqual(len(after), len(lines))
        self.assertEqual(after[0], lines[0])
        self.assertEqual(after[-2:], lines[-2:])
        self.assertEqual(len(e.extract(converted)[0]), 216)
        self.assertEqual(len(e.extract(converted)[1]), 22)
        self.assertIn('Воин-сарказ?', converted.decode("utf8"))
        self.assertIn('Наёмник', converted.decode("utf8"))

    def test_build_rejects_wrong_revision_without_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            source = root / "source"
            for lang in ("en", "cn"):
                path = source / lang / KEY
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('[name="W"] TEST\n', "utf8")
            config = root / "draft.json"
            config.write_text(json.dumps(NEW, ensure_ascii=False), "utf8")
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                e.build(source, root / "output", config)
            self.assertFalse((root / "output").exists())

    def test_manifest_index_and_batch_file(self):
        manifest = json.loads((ROOT / "chronology/CHRONOLOGY_MANIFEST_v030.json").read_text("utf8"))
        self.assertEqual(manifest["next_file"], "activities/act9d0/level_act9d0_03_beg.txt")
        self.assertEqual(manifest["translation_integrity"]["darknights_completed_files"], 4)
        index = (ROOT / "events/DARKNIGHTS_MEMOIR_INDEX_v030.tsv").read_text("utf8")
        self.assertIn("level_act9d0_02_end.txt\tfirst_draft_complete\t216\t22", index)
        bat = (ROOT / "BUILD_DARKNIGHTS_DM1_DM2_PREVIEW_v030.bat").read_text("utf8")
        self.assertIn(r"events\darknights_memoir_dm1_dm2_ru_v030.json", bat)
        self.assertIn(r"scripts\apply_ru_event.py", bat)

if __name__ == "__main__":
    unittest.main()
