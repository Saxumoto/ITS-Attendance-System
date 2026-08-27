@echo off
title ITS Attendance System Launcher
echo Starting ITS Attendance System...
cd /d "%~dp0"
.\venv\Scripts\python.exe main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application closed with an error.
    echo Press any key to see log details...
    pause > nul
)
