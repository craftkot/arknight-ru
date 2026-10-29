@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 required. Game will not be modified.
    pause
    exit /b 2
  )
  set "PY=python"
)
echo Arknights RU v0.22: chapter 2 initial 153 Russian dialogues, 3 scripts.
echo Downloads approved CN/EN files and generates local drafts. Does not modify game.
%PY% scripts\fetch_story_chapter.py --translations story\story_chapter_2_part_1_ru_v022.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview_chapter_2_part1 --translations story\story_chapter_2_part_1_ru_v022.json
if errorlevel 1 goto fail
echo Output: output\story_ru_preview_chapter_2_part1\ru\obt\main\
pause
exit /b 0
:fail
echo Preview failed; game files unchanged.
pause
exit /b 1
