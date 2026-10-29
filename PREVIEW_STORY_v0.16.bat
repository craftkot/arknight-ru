@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
 set "PY=py -3"
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo ERROR: Python 3 is required. Original game files were not changed.
  pause
  exit /b 2
 )
 set "PY=python"
)
echo Arknights RU v0.16 story: 315 draft lines; selected scenes 0-1, 0-2, 0-4, 0-6.
echo Only local previews. Your game installation is NOT touched.
echo Internet needed to fetch version-checked CN and EN originals.
echo.
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
%PY% scripts\apply_ru_story.py --source source\story --output output\story_ru_preview_v016 --translations story\story_main_selection_ru_v016.json
if errorlevel 1 goto fail
echo SUCCESS. The translated scripts are in output\story_ru_preview_v016\ru\obt\main\
echo Nothing was installed into Arknights.
pause
exit /b 0
:fail
echo ERROR: fetch failed or source revision changed. No game files were modified.
pause
exit /b 1
