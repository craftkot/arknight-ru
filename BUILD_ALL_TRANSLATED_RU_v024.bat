@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 required.
    pause
    exit /b 2
  )
  set "PY=python"
)
echo Arknights RU v0.24 -- Chapters 0, 1 and first 10 scripts of chapter 2.
echo Local preview only. This does NOT modify the game.
%PY% scripts\fetch_story_chapter.py --translations story\story_main_selection_ru_v024.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_v024 --translations story\story_main_selection_ru_v024.json
if errorlevel 1 goto fail
echo Saved to output\story_ru_v024\ru\obt\main
pause
exit /b 0
:fail
echo Failed. No original game files were modified.
pause
exit /b 1
