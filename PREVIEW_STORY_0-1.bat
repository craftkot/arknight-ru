@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
 set "PY=py -3"
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo Python 3 was not found. Install Python, or run the commands in docs\STORY_0-1_v014_RU.md manually.
  pause
  exit /b 2
 )
 set "PY=python"
)
echo This tool ONLY downloads public source text for your review and builds a local story preview.
echo It does NOT change Arknights game files or load any DLL.
echo.
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-01_beg.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\fetch_story_pair.py obt/main/level_main_00-01_end.txt --out source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview --translations story\story_0-1_ru_v014.json
if errorlevel 1 goto fail
echo.
echo DONE. Find translated story in output\story_ru_preview\ru\obt\main\
pause
exit /b 0
:fail
echo.
echo ERROR: verify internet access and exact source revision. No game files were changed.
pause
exit /b 1
