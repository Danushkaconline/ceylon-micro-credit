@echo off
REM Send your local changes to GitHub, then click "Update Website" in the live Admin panel.
cd /d "%~dp0"
git add -A
set /p MSG="Describe your change (e.g. new logo): "
if "%MSG%"=="" set MSG=Website update
git commit -m "%MSG%"
git push origin main
if errorlevel 1 (
  echo.
  echo PUSH FAILED - check your internet or GitHub login.
  pause
  exit /b 1
)
echo.
echo Sent to GitHub. Opening the live Admin panel - click "Update from GitHub".
start https://ceylonmicrocredit.pythonanywhere.com/admin/update
pause
