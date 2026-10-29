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
echo Arknights RU v0.25 first editorial story drafts - local PREVIEW ONLY.
echo Does not install or change the game.
%PY% scripts\fetch_story_chapter.py --translations story\story_chapter_2_complete_ru_v025.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_v025 --translations story\story_chapter_2_complete_ru_v025.json
if errorlevel 1 goto fail
echo Created local Russian preview: output\story_ru_v025\ru\obt\main
pause
exit /b 0
:fail
echo Failed. Game files untouched.
pause
exit /b 1
