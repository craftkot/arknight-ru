#!/usr/bin/env python3
# coding: utf-8
"""Build safe, categorized XUnity TXT overlay for original Arknights EN PC.

No game resources or BepInEx DLLs distributed. 489 installed legacy keys
protected via fingerprints; original user's private TXT contents NOT uploaded.
"""
import argparse
import base64
import collections
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parent.parent
NAME="ArknightsRU_BepInEx_Unified_v052.zip"
PREFIX="BepInEx/Translation/ru/Text/"
LEGACY=(
    "ArknightsRU_ExpandedUI_v048.txt",
    "ArknightsRU_ScreenLabels_TEST_v049.txt",
    "ArknightsRU_ScreenFollowup_v050.txt",
    "ArknightsRU_ScreenFollowup_SAFE_v051.txt",
)
DESTS=(
    "ArknightsRU_01_MenuAndSettings.txt",
    "ArknightsRU_02_Base.txt",
    "ArknightsRU_03_Operators.txt",
    "ArknightsRU_04_Combat.txt",
    "ArknightsRU_05_ItemsAndShop.txt",
    "ArknightsRU_06_StoryAndEvents.txt",
    "ArknightsRU_07_Messages.txt",
    "ArknightsRU_08_Misc.txt",
)
SCREEN_CHECKS=(
    "Settings","Reset Settings","Game Settings","Notification",
    "Auto-Select Dialogue Option","Maintain 2x Speed","Terminal",
    "Squads","Operator","Management","Store","Recruit","Headhunt",
    "Missions","Friends","Archives","Base","Depot","Rarity",
    "Custom sort","Class","Potential","Mech-accord Caster",
    "Attack Range","Power Plant","Factory","Dormitory","Reception Room",
    "Workshop","Trading Post","Overview","Building Mode","Leave the Base?",
    "Welcome back to Rhodes Island, Doctor!","Current Squad","Sort by Level",
    "Sort by Rarity","RANK 2","Level Up","Attributes","DPS","Debuff",
    "User Center","Sanity",
)

def old_key_hashes():
    raw=base64.b64decode(
        (ROOT/"release/USER_TEXT_489_KEY_FINGERPRINTS_v048.b64").read_text("ascii").strip(),
        validate=True)
    if len(raw)!=489*6:raise ValueError("Incorrect historical key fingerprints")
    values={raw[i:i+6] for i in range(0,len(raw),6)}
    if len(values)!=489:raise ValueError("Duplicate historical key fingerprints")
    return values

def digest(key):
    return hashlib.sha256(key.encode("utf-8")).digest()[:6]

def load_original():
    content=(ROOT/"translations/xunity_LITERAL_SAFE_PREVIEW.txt").read_text("utf-8-sig")
    mapping={}
    for raw in content.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):continue
        if "=" not in raw:raise ValueError("Invalid XUnity pair")
        k,v=raw.split("=",1)
        if k in mapping or not k or not v.strip():raise ValueError("Invalid or repeated key "+k)
        mapping[k]=v
    if len(mapping)!=1312:raise ValueError("Expected 1312 reviewed repository pairs")
    return mapping

def load_curated():
    doc=json.loads((ROOT/"translations/xunity_screen_labels_curated_v052.json").read_text("utf-8"))
    if doc["version"]!="v0.52":raise ValueError("Unexpected UI version")
    mapping=doc["translations"]
    if len(mapping)<145:raise ValueError("Expected curated screen additions")
    return mapping

def bucket(key):
    k=key.lower()
    if any(x in k for x in (
        "factory","trading post","dormitor","power plant","reception room",
        "workshop","control center","building mode","infrastructure",
        "morale","manufacturing","clue","drones","overview","office",
        "training room","working","resting","room capacity",
        "assistant entran","outfit rotation","per visit")):
        return 1
    if any(x in k for x in (
        "operator","squad","roster","sort","rarity","potential","rank ",
        "elite","skill","talent","level up","level of","attribute","stats",
        "trust","class","outfit","equip","caster","promot","voice",
        "module","enhance","attack range","ranged","melee","experience",
        "level","dps","debuff","slow","alpha wolf")):
        return 2
    if any(x in k for x in (
        "battle","combat","enemy","wave","sanity","operation","deploy",
        "retreat","defeat","victory","damage","mission failed",
        "kill ","healing","defense","defence","attack","expedition")):
        return 3
    if any(x in k for x in (
        "item","lmd","credit","gold","currency","coin","shop","store",
        "voucher","permit","purchase","buy ","sell","exchange",
        "certificate","recruit","headhunt","resource","material","reward",
        "token","depot","originium")):
        return 4
    if any(x in k for x in (
        "story","dialogue","episode","chapter","event","cutscene",
        "archives","rhod","prologue","memorial","origin of","terra",
        "side story","relaunch","critical phase")):
        return 5
    if len(k)>65 or any(x in k for x in (
        "are you sure","confirm","failed","please","cannot ",
        "insufficient","not enough","do you want","you can ","when enabled",
        "warning","error","retry","available","permission","successfully")):
        return 6
    if any(x in k for x in (
        "settings","notification","menu","back","reset","options",
        "terminal","friends","mail","user center","home screen",
        "key","volume","game","login","on","off","current","missions",
        "welcome","leave the base")):
        return 0
    return 7

def assemble():
    original=load_original()
    custom=load_curated()
    old=old_key_hashes()
    combined=dict(original)
    combined.update(custom)
    excluded={k for k in combined if digest(k) in old}
    kept={k:v for k,v in combined.items() if k not in excluded}
    unsafe={"ON","OFF","Full","Free","HP","ATK","DEF","RES","EXP","UP","DOWN"}
    for k in unsafe:kept.pop(k,None)
    if not all(isinstance(k,str) and k and isinstance(v,str) and v.strip()
               and "\x00" not in k+v and "\r" not in k+v and "\n" not in k+v
               for k,v in kept.items()):raise ValueError("Unsafe key/value")
    folders=[[] for _ in DESTS]
    for k,v in sorted(kept.items(),key=lambda x:x[0].casefold()):
        folders[bucket(k)].append((k,v))
    if len(kept)<950:raise ValueError("Too few consolidated mappings")
    if sum(map(len,folders))!=len(kept):raise ValueError("Bucket count mismatch")
    coverage={}
    for k in SCREEN_CHECKS:
        coverage[k]=(
            "included_in_v052" if k in kept else
            "present_in_original_user_TXT" if k in excluded else
            "not_in_literal_dictionary"
        )
    return folders,coverage,{
        "base_literal_source_entries":len(original),
        "curated_screen_entries":len(custom),
        "exact_keys_after_merge":len(combined),
        "excluded_existing_user_keys":len(excluded),
        "additional_translation_keys":len(kept),
        "screen_terms_in_scope":len(SCREEN_CHECKS),
        "screen_terms_mapped_or_existing":sum(v!="not_in_literal_dictionary" for v in coverage.values()),
        "screen_terms_unmapped":[k for k,v in coverage.items() if v=="not_in_literal_dictionary"],
        "category_counts":dict(zip(DESTS,map(len,folders))),
    }

def cleanup_cmd():
    # File names fixed in code; only MOVEs legacy overlays, never deletes game data.
    lines=[
        "@echo off","setlocal",
        "set \"ROOT=%~dp0\"",
        "set \"TARGET=%ROOT%BepInEx\\Translation\\ru\\Text\"",
        "set \"BACKUP=%ROOT%BepInEx\\Translation\\ru\\Backup_before_v052\"",
        "if not exist \"%BACKUP%\" mkdir \"%BACKUP%\"",
    ]
    for name in LEGACY:
        lines.extend([
            f'if exist "%TARGET%\\{name}" (',
            f'  if exist "%BACKUP%\\{name}" (echo Backup already exists for {name}; skipping) else (move "%TARGET%\\{name}" "%BACKUP%\\{name}" >nul)',
            ')',
        ])
    lines.extend(["echo Saved old overlay files to %BACKUP%","echo Original seven user TXT files were not touched.","pause"])
    return "\r\n".join(lines)+"\r\n"

def build(output_dir):
    folders,coverage,stats=assemble()
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    path=out/NAME
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,entries in zip(DESTS,folders):
            text=("# Arknights EN / XUnity Russian UI v0.52 / "+name+"\n"
                  "# Not a client patch; preserved legacy original 7 TXT.\n"
                  +"\n".join(k+"="+v for k,v in entries)+"\n")
            z.writestr(PREFIX+name,text.encode("utf-8"))
        z.writestr("README_UNIFIED_RU.md",(ROOT/"release/README_UNIFIED_BEPINEX_v052.md").read_bytes())
        z.writestr("BACKUP_OLD_OVERLAYS_v052.cmd",cleanup_cmd().encode("utf-8"))
        z.writestr("AUDIT_SCREEN_LABELS_v052.json",json.dumps(coverage,ensure_ascii=False,indent=2).encode("utf-8"))
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    (out/(NAME+".sha256")).write_text(sha+"  "+NAME+"\n",encoding="utf-8")
    report={"version":"v0.52","archive":NAME,"sha256":sha,**stats,
            "game_tested":False,"user_original_files_overwritten":False,
            "install":"Extract into root Arknights_EN; run BACKUP_OLD_OVERLAYS_v052.cmd to move four experimental legacy overlays to separate backup"}
    (out/"ArknightsRU_BepInEx_Unified_v052_manifest.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="dist")
    args=ap.parse_args()
    print(json.dumps(build(args.out),ensure_ascii=False,indent=2))
