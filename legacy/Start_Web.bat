@echo off
title ITS Attendance System (Web Mode)
echo Starting Standalone Web Interface...
cd /d "%~dp0"
"C:\DESKTOP FILES\ITS-Attendance-System\venv\Scripts\python.exe" "C:\DESKTOP FILES\ITS-Attendance-System\main.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application closed with an error.
    pause
)
