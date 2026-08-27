@echo off
title ITS Attendance System Launcher
echo Starting Attendance System in Native UI Mode...
cd /d "%~dp0"
python tk_attendance.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application closed with an error.
    pause
)
