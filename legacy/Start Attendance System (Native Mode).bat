@echo off
title ITS Attendance System Launcher (Native Mode)
echo Starting Attendance System in Native UI Mode...
cd /d "%~dp0"
"C:\DESKTOP FILES\ITS-Attendance-System\venv\Scripts\python.exe" tk_attendance.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application closed with an error.
    pause
)
