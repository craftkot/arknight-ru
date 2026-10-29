@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
 set "PY=py -3"
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo ERROR: Python 3 is required. No game files were changed.
  pause
  exit /b 2
 )
 set "PY=python"
)
echo Arknights RU 0-1 + 0-2 story review: 237 lines, CN primary, EN cross-check.
echo The original game folder is NOT touched. Requires access to GitHub raw content.
echo.
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-01_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-01_end.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-02_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-02_end.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview_v015 --translations story\story_main_0-1_0-2_ru_v015.json
if errorlevel 1 goto fail
echo.
echo SUCCESS: open output\story_ru_preview_v015\ru\obt\main\
echo No game files were edited or injected.
pause
exit /b 0
:fail
echo.
echo ERROR: source not available or changed. No game files were edited.
pause
exit /b 1
