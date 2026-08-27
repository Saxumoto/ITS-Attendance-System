@echo off
cd /d "%~dp0"
"C:\DESKTOP FILES\ITS-Attendance-System\venv\Scripts\python.exe" tk_attendance.py > crash_report.txt 2>&1
