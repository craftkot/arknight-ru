@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 is required.
    pause
    exit /b 2
  )
  set "PY=python"
)
echo Arknights RU v0.23 - Chapters 0, 1 and first six scenes of chapter 2.
echo Source and output only; will NOT modify the game.
%PY% scripts\fetch_story_chapter.py --translations story\story_main_selection_ru_v023.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_v023 --translations story\story_main_selection_ru_v023.json
if errorlevel 1 goto fail
echo Completed: output\story_ru_v023\ru\obt\main
pause
exit /b 0
:fail
echo Failed - original game files unchanged.
pause
exit /b 1
