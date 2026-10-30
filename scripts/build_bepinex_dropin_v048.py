#!/usr/bin/env python3
# coding: utf-8
"""Build non-overwriting BepInEx/XUnity translation-only overlay for Arknights EN PC.

User's seven uploaded TXT files are intentionally NOT distributed or overwritten.
Their 489 unique English lookup keys are represented by 48-bit SHA256 fingerprints.
No game content assets, patchers, DLLs, executable mods or automation of game files.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parent.parent
LITERAL=ROOT/"translations/xunity_LITERAL_SAFE_PREVIEW.txt"
FINGERPRINTS=ROOT/"release/USER_TEXT_489_KEY_FINGERPRINTS_v048.b64"
README=ROOT/"release/README_BEPINEX_RU_v048.md"
ZIP_NAME="ArknightsRU_BepInEx_DropIn_v048.zip"
DEST="BepInEx/Translation/ru/Text/ArknightsRU_ExpandedUI_v048.txt"

def get_existing_hashes():
    raw=base64.b64decode(FINGERPRINTS.read_text("ascii").strip(),validate=True)
    if len(raw)!=489*6:
        raise ValueError("Expected 489 existing XUnity keys in fingerprint set")
    return {raw[i:i+6] for i in range(0,len(raw),6)}

def build(output_dir):
    originals=get_existing_hashes()
    content=LITERAL.read_text("utf-8-sig")
    entries=[]
    seen=set()
    overlap=0
    for raw in content.splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        if "=" not in raw:
            raise ValueError("Invalid XUnity literal line without equals")
        key,value=raw.split("=",1)
        if not key or not value.strip() or "\0" in raw:
            raise ValueError("Invalid empty key/value or NUL")
        if key in seen:
            raise ValueError("Duplicate source key in repository literal file")
        seen.add(key)
        fingerprint=hashlib.sha256(key.encode("utf-8")).digest()[:6]
        if fingerprint in originals:
            overlap+=1
            continue
        entries.append(raw)
    if len(seen)!=1312:
        raise ValueError("Expected fixed v0.47 source of 1312 literal translations")
    if len(entries)<500:
        raise ValueError("Too few new translations after excluding existing files")
    ru_text=(
        "# Arknights RU v0.48 — additional XUnity translations only.\n"
        "# Preserves user's original seven TXT files, skips duplicate keys by fingerprint.\n"
        "# Unverified in Yostar Global PC, remove this file to revert.\n"
        + "\n".join(entries)+"\n"
    )
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    path=output/ZIP_NAME
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr(DEST,ru_text.encode("utf-8"))
        z.writestr("README_BEPINEX_RU_v048.md",README.read_bytes())
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    (output/(ZIP_NAME+".sha256")).write_text(sha+"  "+ZIP_NAME+"\n",encoding="utf-8")
    manifest={
        "version":"v0.48",
        "artifact":ZIP_NAME,
        "sha256":sha,
        "install_at":"Arknights_EN game root (folder containing BepInEx)",
        "translation_target":DEST,
        "existing_translations_preserved":True,
        "existing_uploaded_txt_count":7,
        "existing_unique_key_fingerprints":len(originals),
        "available_repository_literal_keys":len(seen),
        "skipped_existing_keys":overlap,
        "additional_xunity_literal_mappings":len(entries),
        "status":"experimental UI translation overlay; not verified inside game",
        "warning":"No DLL, game file modifications or Arknights narrative injection included"
    }
    (output/"ArknightsRU_BepInEx_DropIn_v048_manifest.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="dist")
    args=p.parse_args()
    print(json.dumps(build(args.out),ensure_ascii=False,indent=2))
