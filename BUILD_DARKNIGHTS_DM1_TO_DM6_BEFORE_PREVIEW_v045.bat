@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  set "PY=python"
) else (
  set "PY=py -3"
)
echo Arknights RU local preview: Darknights Memoir DM-1 through DM-6 before battle (11 scenes).
echo This does NOT install or modify Arknights.
%PY% scripts\fetch_story_chapter.py --translations events\darknights_memoir_dm1_to_dm6_before_ru_v045.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_event.py --source source\story --output output\darknights_dm1_to_dm6_before_ru_v045 --translations events\darknights_memoir_dm1_to_dm6_before_ru_v045.json
if errorlevel 1 goto fail
echo Preview available in output\darknights_dm1_to_dm6_before_ru_v045\ru\activities\act9d0
pause
exit /b 0
:fail
echo Preview FAILED. No game files have been modified.
pause
exit /b 1
