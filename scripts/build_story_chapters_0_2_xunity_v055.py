#!/usr/bin/env python3
# coding: utf-8
"""Build XUnity/BepInEx test overlay from already translated chapters 0–2.

Never modifies the game, BepInEx, or previous user TXT files.
Original story source is downloaded only in CI/build memory, verified by Git blob SHA1;
it is NOT redistributed as an original game resource.
"""
import argparse
import base64
from collections import defaultdict, Counter
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent.parent
INPUT=ROOT/"story/story_main_selection_ru_v025.json"
LITERAL=ROOT/"translations/xunity_LITERAL_SAFE_PREVIEW.txt"
CURATED=ROOT/"translations/xunity_screen_labels_curated_v052.json"
FINGERPRINTS=ROOT/"release/USER_TEXT_489_KEY_FINGERPRINTS_v048.b64"
README=ROOT/"release/README_STORY_CHAPTERS_0_2_XUNITY_v055.md"
ARCHIVE="ArknightsRU_Story_Chapters_0-2_XUnity_TEST_v055.zip"
PREFIX="BepInEx/Translation/ru/Text/"
DESTS={
    "00":"ArknightsRU_20_Story_Chapter0_TEST.txt",
    "01":"ArknightsRU_21_Story_Chapter1_TEST.txt",
    "02":"ArknightsRU_22_Story_Chapter2_TEST.txt",
}
# An exact English dialog string can be used as an XUnity dictionary key
# only if it is sufficiently specific and identical wherever it occurs.
# 16 chars/2 words keeps common UI and authentication labels out.
MIN_LENGTH=16
MAX_SOURCE_LENGTH=400
MARKUP=re.compile(r'\{@[\w]+\}|\{\d+(?:[^{}]*)\}|<[^>]+>')
SPEAKER=re.compile(r'(\[\s*name\s*=\s*)(["\x27])(.*?)(\2)(\s*\])',re.I)
STORYPATH=re.compile(r'^obt/main/level_main_(00|01|02)-[0-9]{2}_(?:beg|end)\.txt$')
FETCH_URL=(
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/"
    "main/en_US/gamedata/story/"
)
DYNAMIC=re.compile(r'\{@[^}]+\}|\{\d+(?:[^{}]*)\}')
LETTERS=re.compile(r'[A-Za-z]{2,}')
SKIP_REASONS=(
    "too_short_or_generic","preexisting_ui_or_user_key",
    "unsafe_characters","conflicting_translations","dynamic_markup",
    "over_400_characters",
)

def blob_sha(payload):
    return hashlib.sha1(("blob "+str(len(payload))+"\0").encode("ascii")+payload).hexdigest()

def fetch_original(rel,sha,source_root=None):
    if source_root is not None:
        path=Path(source_root)/"en"/rel
        payload=path.read_bytes()
    else:
        url=FETCH_URL+rel
        last=None
        for attempt in range(3):
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"ArknightsRU-Story-TestPack-v055"})
                with urllib.request.urlopen(req,timeout=25) as response:
                    payload=response.read(2_000_001)
                break
            except Exception as e:
                last=e
                if attempt<2:time.sleep(1.5*(attempt+1))
        else:
            raise RuntimeError("Cannot retrieve pinned EN story source "+rel) from last
    if len(payload)>2_000_000:
        raise ValueError("Source too large: "+rel)
    actual=blob_sha(payload)
    if actual!=sha:
        raise ValueError("SOURCE REVISION MISMATCH: "+rel+" expected "+sha+" got "+actual)
    return payload

def english_dialogues(raw):
    result=[]
    for line in raw.decode("utf-8-sig").splitlines():
        match=SPEAKER.search(line)
        if match:
            text=line[match.end():].strip()
            if text and not text.startswith("//"):
                result.append(text)
    return result

def fingerprint(key):
    return hashlib.sha256(key.encode("utf-8")).digest()[:6]

def get_preexisting(fingerprint_path=FINGERPRINTS,literal_path=LITERAL,curated_path=CURATED):
    data=base64.b64decode(Path(fingerprint_path).read_text("ascii").strip(),validate=True)
    if len(data)!=489*6:raise ValueError("Expected 489 historical key fingerprints")
    fp={data[i:i+6] for i in range(0,len(data),6)}
    if len(fp)!=489:raise ValueError("Duplicate historical fingerprint")
    literal={}
    for line in Path(literal_path).read_text("utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):continue
        if "=" not in line:raise ValueError("Malformed repo XUnity line")
        key,value=line.split("=",1)
        if key in literal:raise ValueError("Duplicate repo literal key")
        literal[key]=value
    curated=json.loads(Path(curated_path).read_text("utf-8"))["translations"]
    return fp,set(literal)|set(curated)

def find_chapter(rel):
    match=STORYPATH.fullmatch(rel)
    if not match:raise ValueError("Unexpected main story source path: "+rel)
    return match.group(1)

def is_unsafe(source,translated):
    # Parsing '=' or escapes may change behavior in the current installed XUnity.
    if ("=" in source or "\n" in source or "\r" in source or "\t" in source
        or "\n" in translated or "\r" in translated or "\t" in translated
        or "\x00" in source+translated or source.startswith(("r:","sr:","#"))):
        return True
    if MARKUP.findall(source)!=MARKUP.findall(translated):
        # Keep official source placeholders / rich-text formatting exactly.
        return True
    return False

def generate(outdir,source_root=None,manifest=INPUT,require_full=True):
    data=json.loads(Path(manifest).read_text("utf-8"))
    files=data.get("files",{})
    if require_full and (
        len(files)!=44 or sum(x["dialogue_count"] for x in files.values())!=2377
    ):
        raise ValueError("Expected exact completed chapters 0–2: 44 files, 2377 dialogs")
    existing_fps,existing_literals=get_preexisting()
    seen=defaultdict(list)
    counts=Counter()
    counts_by_chapter={ch:Counter() for ch in DESTS}
    for rel,meta in files.items():
        chapter=find_chapter(rel)
        english=english_dialogues(fetch_original(
            rel,meta["en_git_blob_sha1"],source_root=source_root))
        translation=meta["dialogues"]
        n=meta["dialogue_count"]
        if len(english)!=n or set(translation)!={str(i) for i in range(1,n+1)}:
            raise ValueError("Dialogue ordinal mismatch "+rel)
        for i,source in enumerate(english,1):
            ru=translation[str(i)]
            if not isinstance(ru,str) or not ru.strip():raise ValueError("Missing RU "+rel+" #"+str(i))
            if MARKUP.findall(source)!=MARKUP.findall(ru):
                raise ValueError("Inline markup changed "+rel+" #"+str(i))
            counts["total_dialogues"]+=1
            counts_by_chapter[chapter]["source_dialogues"]+=1
            seen[source].append((ru,chapter,rel,i))
    conflicts={k for k,occur in seen.items() if len({t[0] for t in occur})>1}
    selected={}
    omissions=Counter()
    omissions_by_chapter={ch:Counter() for ch in DESTS}
    for source,occur in seen.items():
        ru,chapter,rel,index=occur[0]
        reason=None
        if source in conflicts:
            reason="conflicting_translations"
        elif len(source)>MAX_SOURCE_LENGTH:
            reason="over_400_characters"
        elif is_unsafe(source,ru):
            reason="unsafe_characters"
        elif DYNAMIC.search(source):
            reason="dynamic_markup"
        elif len(source)<MIN_LENGTH or len(LETTERS.findall(source))<2:
            reason="too_short_or_generic"
        elif source in existing_literals or fingerprint(source) in existing_fps:
            reason="preexisting_ui_or_user_key"
        if reason:
            omissions[reason]+=len(occur)
            for _,ch,_,_ in occur:omissions_by_chapter[ch][reason]+=1
        else:
            # If a dialogue recurs identically, keep only one XUnity translation.
            selected[source]=(ru,chapter)
            counts["covered_dialogue_occurrences"]+=len(occur)
            for _,ch,_,_ in occur:counts_by_chapter[ch]["covered_source_dialogues"]+=1
            counts_by_chapter[chapter]["distinct_keys_written"]+=1
    by_chapter={ch:[] for ch in DESTS}
    for source,(ru,ch) in selected.items():
        by_chapter[ch].append((source,ru))
    for ch in by_chapter:by_chapter[ch].sort(key=lambda p:p[0].casefold())
    assert len(selected)==sum(len(x) for x in by_chapter.values())
    assert all(source not in existing_literals and fingerprint(source) not in existing_fps for source in selected)
    assert counts["total_dialogues"]==sum(x["source_dialogues"] for x in counts_by_chapter.values())
    assert counts["total_dialogues"]==counts["covered_dialogue_occurrences"]+sum(omissions.values())
    if require_full and len(selected)<900:
        raise ValueError("Too few safe unique keys, suspicious mismatch: "+str(len(selected)))
    report={
        "version":"v0.55",
        "source_kind":"English exact spoken dialogue text -> existing reviewed Russian first drafts",
        "client_game_tested":False,
        "source_scripts_in_archive":False,
        "safest_install":"Overlay only: no DLL, no config edit, no game data replacement",
        "source_files":len(files),
        "source_dialogues":counts["total_dialogues"],
        "safe_unique_lookup_keys":len(selected),
        "dialogue_occurrences_potentially_covered":counts["covered_dialogue_occurrences"],
        "omitted_dialogue_occurrences":sum(omissions.values()),
        "omission_reasons":dict(omissions),
        "chapters":{ch:dict(counts_by_chapter[ch]) for ch in DESTS},
        "xunity_installed_config_default_max_length":200,
        "keys_longer_than_200":sum(len(source)>200 for source in selected),
        "warning":"Lookup coverage is NOT proof that a runtime text hook intercepts story dialogue. Dynamic names, short phrases and conflicting keys are conservatively excluded.",
    }
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)
    archive=out/ARCHIVE
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for ch,name in DESTS.items():
            text=("# Arknights original PC; chapter "+ch+
                  "; manually reviewed XUnity exact English->Russian dialogue mapping\n"+
                  "# Test only, generic/duplicate and legacy UI conflicts omitted.\n"+
                  "\n".join(a+"="+b for a,b in by_chapter[ch])+"\n")
            z.writestr(PREFIX+name,text.encode("utf-8"))
        z.writestr("README_STORY_RU_TEST_v055.md",README.read_bytes())
        z.writestr("AUDIT_STORY_0_2_v055.json",json.dumps(report,ensure_ascii=False,indent=2).encode("utf-8"))
        z.writestr("ROLLBACK_STORY_TEST_v055.cmd",rollback_command().encode("utf-8"))
    report["archive_sha256"]=hashlib.sha256(archive.read_bytes()).hexdigest()
    (out/(ARCHIVE+".sha256")).write_text(report["archive_sha256"]+"  "+ARCHIVE+"\n","utf-8")
    (out/"ArknightsRU_Story_Chapters_0-2_XUnity_TEST_v055_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
    return report

def rollback_command():
    lines=[
        "@echo off","setlocal",
        "set \"DIR=%~dp0BepInEx\\Translation\\ru\\Text\"",
        "set \"BACK=%~dp0BepInEx\\Translation\\ru\\Backup_Story_0_2_v055\"",
        "if not exist \"%BACK%\" mkdir \"%BACK%\"",
    ]
    for name in DESTS.values():
        lines.extend([
            "if exist \"%DIR%\\"+name+"\" (",
            "  if exist \"%BACK%\\"+name+"\" (",
            "    echo Backup exists; no overwrite: "+name,
            "  ) else (",
            "    move \"%DIR%\\"+name+"\" \"%BACK%\\"+name+"\" >nul",
            "  )",
            ")",
        ])
    return "\r\n".join(lines+[
        "echo Story test translations moved to backup (no original game files touched).",
        "echo Close and relaunch Arknights to verify rollback.",
        "pause"
    ])+"\r\n"

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="dist")
    p.add_argument("--source-root",default=None,help="Optional local source directory containing en/obt/main...")
    args=p.parse_args()
    print(json.dumps(generate(args.out,args.source_root),ensure_ascii=False,indent=2))
