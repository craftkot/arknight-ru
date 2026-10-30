#!/usr/bin/env python3
# coding: utf-8
"""Assemble a data-only preview ZIP; no game writes, originals or plugin binaries."""
import argparse
import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFIX = "Arknights_RU_TestPack_v047/"
FILES = (
    ("release/README_TESTPACK_RU.md", "README_FIRST_RU.md"),
    ("events/darknights_memoir_all_ru_v047.json", "events/darknights_memoir_all_ru_v047.json"),
    ("translations/ui_keyed_all_ru.json", "translations/ui_keyed_all_ru.json"),
    ("BUILD_DARKNIGHTS_ALL_PREVIEW_v047.bat", "BUILD_DARKNIGHTS_ALL_PREVIEW_v047.bat"),
    ("scripts/apply_ru_story.py", "scripts/apply_ru_story.py"),
    ("scripts/apply_ru_event.py", "scripts/apply_ru_event.py"),
    ("scripts/fetch_story_pair.py", "scripts/fetch_story_pair.py"),
    ("scripts/fetch_story_chapter.py", "scripts/fetch_story_chapter.py"),
)

def build(out_directory):
    selection=json.loads((ROOT/"events/darknights_memoir_all_ru_v047.json").read_text("utf-8"))
    scenes=selection["files"]
    if len(scenes)!=13:raise ValueError("Expected all thirteen Darknights scenes")
    named=plain=0
    for spec in scenes.values():
        if len(spec["dialogues"])!=spec["dialogue_count"] or len(spec["plain_dialogues"])!=spec["plain_dialogue_count"]:
            raise ValueError("Incomplete story spec")
        named+=spec["dialogue_count"]
        plain+=spec["plain_dialogue_count"]
    if (named,plain)!=(1902,160):raise ValueError("Unexpected scene counts")
    ui=json.loads((ROOT/"translations/ui_keyed_all_ru.json").read_text("utf-8"))
    if len(ui)!=2544 or not all(isinstance(v,str) and v.strip() for v in ui.values()):
        raise ValueError("Missing UI-keyed translations")
    literal=(ROOT/"translations/xunity_LITERAL_SAFE_PREVIEW.txt").read_bytes()
    if not literal.strip():raise ValueError("Empty experimental XUnity file")
    for source,_ in FILES:
        if not (ROOT/source).is_file():raise FileNotFoundError(source)
    output=pathlib.Path(out_directory)
    output.mkdir(parents=True,exist_ok=True)
    zipfile_path=output/"Arknights_RU_TestPack_v047.zip"
    with zipfile.ZipFile(zipfile_path,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for source,target in FILES:
            z.write(ROOT/source,arcname=PREFIX+target)
        z.writestr(PREFIX+"Translation/ru/Text/Arknights_RU_UI_EXPERIMENTAL.txt",literal)
    digest=hashlib.sha256(zipfile_path.read_bytes()).hexdigest()
    (output/"Arknights_RU_TestPack_v047.sha256").write_text(
        digest+"  "+zipfile_path.name+"\n",encoding="utf-8")
    report={"version":"v0.47","artifact":zipfile_path.name,"sha256":digest,
            "dm_scenes":13,"dm_lines":2062,"ui_keyed":2544,
            "status":"data-only prerelease, UI XUnity experimental, NOT game-tested"}
    (output/"Arknights_RU_TestPack_v047_manifest.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="dist")
    args=parser.parse_args()
    print(json.dumps(build(args.out),ensure_ascii=False,indent=2))
