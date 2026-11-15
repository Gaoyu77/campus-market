@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0setup_env.bat"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" "%~dp0start_market.py"
if errorlevel 1 goto failed
exit /b 0
:failed
echo Start failed. See the message above.
pause
exit /b 1
