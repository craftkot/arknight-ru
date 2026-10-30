# coding: utf-8
"""Offline tests of XUnity story pack; CI performs full pinned-source build."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import build_story_chapters_0_2_xunity_v055 as pack

class StoryXUnityV055(unittest.TestCase):
    def test_existing_44_translations_complete(self):
        d=json.loads(pack.INPUT.read_text("utf-8"))
        self.assertEqual(len(d["files"]),44)
        self.assertEqual(sum(x["dialogue_count"] for x in d["files"].values()),2377)
        for path,spec in d["files"].items():
            pack.find_chapter(path)
            self.assertEqual(set(spec["dialogues"]),set(map(str,range(1,spec["dialogue_count"]+1))))
            self.assertEqual(len(spec["en_git_blob_sha1"]),40)
        fp,literal=pack.get_preexisting()
        self.assertEqual(len(fp),489)
        self.assertGreaterEqual(len(literal),1300)

    def test_offline_realistic_english_duplicates_and_short_dialogues(self):
        sources={
            "obt/main/level_main_00-01_beg.txt":[
                "We have arrived at our location.",
                "Duplicated line in two places.",
                "Conflicting story line here.",
                "Doctor {@nickname}, here is text.",
                "No.",
                "An existing UI text that must remain.",
            ],
            "obt/main/level_main_01-01_beg.txt":[
                "Duplicated line in two places.",
                "Conflicting story line here.",
                "Another simple complete sentence.",
                "An existing UI text that must remain.",
            ],
        }
        texts={
            "obt/main/level_main_00-01_beg.txt":[
                "Мы прибыли на место.","Повторяется.","Перевод А",
                "Доктор {@nickname}, вот текст.","Нет.",
                "Предыдущий перевод интерфейса.",
            ],
            "obt/main/level_main_01-01_beg.txt":[
                "Повторяется.","Перевод Б","Ещё одно предложение.",
                "Предыдущий перевод интерфейса.",
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            data={"files":{}}
            for path,spoken in sources.items():
                raw=("\n".join('[name="Amiya"] '+v for v in spoken)+"\n").encode("utf-8")
                file=root/"sources"/"en"/path
                file.parent.mkdir(parents=True,exist_ok=True)
                file.write_bytes(raw)
                data["files"][path]={
                    "en_git_blob_sha1":pack.blob_sha(raw),
                    "dialogue_count":len(spoken),
                    "dialogues":{str(i+1):v for i,v in enumerate(texts[path])},
                }
            manifest=root/"manifest.json"
            manifest.write_text(json.dumps(data,ensure_ascii=False),"utf-8")
            with patch.object(pack,"get_preexisting",return_value=(set(),{"An existing UI text that must remain."})):
                report=pack.generate(root/"out",source_root=root/"sources",
                                     manifest=manifest,require_full=False)
            self.assertEqual(report["source_dialogues"],10)
            self.assertEqual(report["safe_unique_lookup_keys"],3)
            self.assertEqual(report["dialogue_occurrences_potentially_covered"],4)
            self.assertEqual(report["omitted_dialogue_occurrences"],6)
            self.assertEqual(report["omission_reasons"]["conflicting_translations"],2)
            self.assertEqual(report["omission_reasons"]["preexisting_ui_or_user_key"],2)
            self.assertEqual(report["omission_reasons"]["dynamic_markup"],1)
            self.assertEqual(report["omission_reasons"]["too_short_or_generic"],1)
            output=root/"out"/pack.ARCHIVE
            self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),report["archive_sha256"])
            with zipfile.ZipFile(output) as z:
                names=set(z.namelist())
                self.assertEqual(len(names),6)
                self.assertTrue({pack.PREFIX+x for x in pack.DESTS.values()}.issubset(names))
                self.assertIn("README_STORY_RU_TEST_v055.md",names)
                self.assertIn("AUDIT_STORY_0_2_v055.json",names)
                self.assertIn("ROLLBACK_STORY_TEST_v055.cmd",names)
                txts=[z.read(pack.PREFIX+x).decode("utf-8") for x in pack.DESTS.values()]
                self.assertEqual(sum(len([l for l in t.splitlines() if l and not l.startswith("#")]) for t in txts),3)
                self.assertEqual(sum(t.count("Duplicated line in two places.=") for t in txts),1)
                self.assertFalse(any("Conflicting story line here.=" in t for t in txts))
                self.assertFalse(any("An existing UI text that must remain.=" in t for t in txts))
                self.assertTrue(all(not p.startswith("/") and ".." not in p.split("/") for p in names))
                self.assertFalse(any(p.endswith((".dll",".exe",".apk")) for p in names))
                rollback=z.read("ROLLBACK_STORY_TEST_v055.cmd").decode("utf-8")
                self.assertNotIn(" del ",rollback.lower())
                for name in pack.DESTS.values():self.assertIn(name,rollback)

    def test_reject_wrong_source_revision_without_writing_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            rel="obt/main/level_main_00-01_beg.txt"
            path=root/"source"/"en"/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(b'[name="Amiya"] Hello, my friend from Rhodes Island!\n')
            data={"files":{rel:{
                "en_git_blob_sha1":"0"*40,
                "dialogue_count":1,
                "dialogues":{"1":"Привет, друг с Родос Айленда!"}
            }}}
            manifest=root/"manifest.json"
            manifest.write_text(json.dumps(data,ensure_ascii=False),"utf-8")
            with patch.object(pack,"get_preexisting",return_value=(set(),set())):
                with self.assertRaisesRegex(ValueError,"SOURCE REVISION MISMATCH"):
                    pack.generate(root/"out",source_root=root/"source",
                                  manifest=manifest,require_full=False)
            self.assertFalse((root/"out").exists())
if __name__=="__main__":unittest.main()
