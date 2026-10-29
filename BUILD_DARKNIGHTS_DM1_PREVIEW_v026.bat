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
echo Arknights RU v0.26 Darknights Memoir DM-1 BEFORE BATTLE (preview only).
echo This operation does not install any game patch.
%PY% scripts\fetch_story_chapter.py --translations events\darknights_memoir_dm1_before_ru_v026.json --output source\story
if errorlevel 1 goto fail
%PY% scripts\apply_ru_event.py --source source\story --output output\darknights_memoir_ru_v026 --translations events\darknights_memoir_dm1_before_ru_v026.json
if errorlevel 1 goto fail
echo Generated preview in output\darknights_memoir_ru_v026\ru\activities\act9d0
pause
exit /b 0
:fail
echo Preview failed. No game files were modified.
pause
exit /b 1
