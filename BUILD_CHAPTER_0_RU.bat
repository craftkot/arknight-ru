@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 is required. Files of the game will NOT be edited.
    pause
    exit /b 2
  )
  set "PY=python"
)
echo Arknights RU v0.20: Chapter 0 -- 654 RU dialogue drafts across 12 files.
echo Downloads source CN/EN text from public community archives (24 files),
echo verifies pinned SHA1 revisions, then builds LOCAL text previews. No game changes.
%PY% scripts\fetch_story_chapter.py --translations story\story_main_selection_ru_v020.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview_chapter_0 --translations story\story_main_selection_ru_v020.json
if errorlevel 1 goto fail
echo SUCCESS: output\story_ru_preview_chapter_0\ru\obt\main\
echo These are NOT installed in the game.
pause
exit /b 0
:fail
echo FAILED: the source may have changed or the network is unavailable.
echo No game files were changed.
pause
exit /b 1
