@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
 set "PY=py -3"
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo ERROR: Python 3 is required. Game files unchanged.
  pause
  exit /b 2
 )
 set "PY=python"
)
echo Arknights RU v0.17 story preview: 413 draft lines, 8 selected scenes.
echo This tool creates LOCAL PREVIEWS ONLY. It does NOT change the game.
echo Internet connection is needed to fetch version-pinned CN and EN scene texts.
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-01_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-01_end.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-02_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-02_end.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-04_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-06_end.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-07_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-07_end.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview_v017 --translations story\story_main_selection_ru_v017.json
if errorlevel 1 goto fail
echo SUCCESS: output\story_ru_preview_v017\ru\obt\main\
echo No game file was modified.
pause
exit /b 0
:fail
echo ERROR: source unavailable, changed revision, or invalid translation. No game file was modified.
pause
exit /b 1
