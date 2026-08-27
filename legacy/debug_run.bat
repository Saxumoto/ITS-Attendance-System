@echo off
cd /d "%~dp0"
echo Logging start time: %date% %time% > error_log.txt
"C:\DESKTOP FILES\ITS-Attendance-System\venv\Scripts\python.exe" "C:\DESKTOP FILES\ITS-Attendance-System\main.py" >> error_log.txt 2>&1
echo Exit code: %errorlevel% >> error_log.txt
