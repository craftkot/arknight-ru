@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 required. No game files will be modified.
    pause
    exit /b 2
  )
  set "PY=python"
)
echo Arknights RU v0.21: Chapter 1 - 701 draft dialogues across 12 files.
echo Downloads Chinese and English sources, verifies Git hashes and generates local previews.
%PY% scripts\fetch_story_chapter.py --translations story\story_chapter_1_ru_v021.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview_chapter_1 --translations story\story_chapter_1_ru_v021.json
if errorlevel 1 goto fail
echo OK: output\story_ru_preview_chapter_1\ru\obt\main\
pause
exit /b 0
:fail
echo Preview failed. Game files have not been modified.
pause
exit /b 1
