@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  set "PY=python"
) else (
  set "PY=py -3"
)
echo Russian preview Darknights Memoir DM-1 BEFORE AND AFTER BATTLE.
echo This does NOT install any patch or change the Arknights game files.
%PY% scripts\fetch_story_chapter.py --translations events\darknights_memoir_dm1_both_ru_v028.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_event.py --source source\story --output output\darknights_dm1_ru_v028 --translations events\darknights_memoir_dm1_both_ru_v028.json
if errorlevel 1 goto fail
echo Preview generated in output\darknights_dm1_ru_v028\ru\activities\act9d0
pause
exit /b 0
:fail
echo Preview failed. No game files were modified.
pause
exit /b 1
