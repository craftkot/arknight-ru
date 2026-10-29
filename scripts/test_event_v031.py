# coding: utf-8
"""Offline checks for the explicitly partial Darknights Memoir DM-3 draft."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import apply_ru_event as event
from apply_ru_story import git_blob_sha1

PARTIAL_PATH = ROOT / "events/darknights_memoir_dm3_before_partial_ru_v031.json"
KEY = "activities/act9d0/level_act9d0_03_beg.txt"


class DarknightsV031(unittest.TestCase):
    def test_partial_progress_is_not_a_complete_scene(self):
        doc = json.loads(PARTIAL_PATH.read_text(encoding="utf8"))
        self.assertEqual(doc["source_file"], KEY)
        self.assertEqual(doc["status"].split(";")[0], "partial_first_draft_needs_editorial_review")
        self.assertFalse(doc["progress"]["complete"])
        self.assertEqual(doc["progress"]["named_ru_lines"], 0)
        self.assertEqual(doc["progress"]["plain_ru_lines"], 12)
        self.assertEqual(doc["progress"]["next_plain_ordinal"], 13)
        self.assertEqual(doc["dialogues"], {})
        self.assertEqual(set(doc["plain_dialogues"]), {str(i) for i in range(1, 13)})
        self.assertEqual(doc["source"]["named_dialogue_count"], 152)
        self.assertEqual(doc["source"]["plain_dialogue_count"], 35)
        self.assertEqual(doc["source"]["cn_git_blob_sha1"], "538c852f8a64981df34f7699be9f73dfe00873ea")
        self.assertEqual(doc["source"]["en_git_blob_sha1"], "37dcf8c721efd0fa5068d18146caae45ba200b70")
        self.assertTrue(doc["source"]["dialogue_kind_sequence_matches"])
        for line in doc["plain_dialogues"].values():
            self.assertTrue(line.strip())
            self.assertNotIn("\n", line)
            self.assertNotIn("\t", line)
            self.assertEqual(event.quoted_tokens(line), [])

    def test_new_speakers_and_earlier_mappings(self):
        expected = {
            "Kal'tsit": "Кальцит", "???": "???",
            "Small Cautus": "Невысокая каутус",
            "Closure": "Клоужер", "Theresa": "Терезия",
            "Ines": "Инес", "Hoederer": "Хёдерер", "W": "W",
        }
        for en, ru in expected.items():
            self.assertEqual(event.SPEAKER_EVENT_RU[en], ru)

    def test_order_signature_detects_named_plain_swap(self):
        en = b'[name="W"] Hello\nNarration\n'
        cn = '旁白\n[name="W"] 你好\n'.encode("utf8")
        self.assertEqual((len(event.extract(en)[0]), len(event.extract(en)[1])), (1, 1))
        self.assertEqual((len(event.extract(cn)[0]), len(event.extract(cn)[1])), (1, 1))
        self.assertEqual(event.dialogue_kinds(en), ["named", "plain"])
        self.assertEqual(event.dialogue_kinds(cn), ["plain", "named"])
        self.assertNotEqual(event.dialogue_kinds(en), event.dialogue_kinds(cn))

    def test_build_rejects_same_counts_in_different_order(self):
        en = b'[name="W"] Hello\nNarration\n'
        cn = '旁白\n[name="W"] 你好\n'.encode("utf8")
        spec = {
            "version": "test",
            "event": "Darknights Memoir",
            "files": {KEY: {
                "cn_git_blob_sha1": git_blob_sha1(cn),
                "en_git_blob_sha1": git_blob_sha1(en),
                "dialogue_count": 1, "plain_dialogue_count": 1,
                "dialogues": {"1": "Привет"},
                "plain_dialogues": {"1": "Повествование"},
            }}
        }
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            for lang, raw in (("en", en), ("cn", cn)):
                p = root / "sources" / lang / KEY
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(raw)
            config = root / "config.json"
            config.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf8")
            with self.assertRaisesRegex(ValueError, "CN EN dialogue order mismatch"):
                event.build(root / "sources", root / "output", config)
            self.assertFalse((root / "output").exists())

    def test_build_accepts_matching_order_with_different_commands(self):
        en = b'[Dialog]\n[name="W"] Hello\nNarration\n'
        cn = '[stopmusic]\n[name="W"] 你好\n旁白\n'.encode("utf8")
        spec = {
            "version": "test", "event": "Darknights Memoir",
            "files": {KEY: {
                "cn_git_blob_sha1": git_blob_sha1(cn),
                "en_git_blob_sha1": git_blob_sha1(en),
                "dialogue_count": 1, "plain_dialogue_count": 1,
                "dialogues": {"1": "Привет"}, "plain_dialogues": {"1": "Повествование"},
            }}
        }
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            for lang, raw in (("en", en), ("cn", cn)):
                p = root / "sources" / lang / KEY
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(raw)
            config = root / "config.json"
            config.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf8")
            report = event.build(root / "sources", root / "output", config)
            self.assertEqual((report["named_ru_lines"], report["plain_ru_lines"]), (1, 1))
            output = (root / "output" / "ru" / KEY).read_text(encoding="utf8")
            self.assertIn("[Dialog]", output)
            self.assertIn('[name="W"] Привет', output)
            self.assertIn("Повествование", output)


if __name__ == "__main__":
    unittest.main()
