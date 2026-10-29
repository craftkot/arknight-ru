@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
 set "PY=py -3"
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo ERROR: Python 3 required. Game files untouched.
  pause
  exit /b 2
 )
 set "PY=python"
)
echo Arknights RU v0.18: 491 draft story lines across 9 scenes.
echo Download community scene scripts and create local preview. This does NOT modify the game.
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
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-08_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview_v018 --translations story\story_main_selection_ru_v018.json
if errorlevel 1 goto fail
echo SUCCESS: output\story_ru_preview_v018\ru\obt\main\
echo Game files untouched.
pause
exit /b 0
:fail
echo ERROR: download, version mismatch or validation failure. No game files changed.
pause
exit /b 1
