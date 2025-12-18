@echo off
REM One-click backup for SANZAD project

cd /d "C:\Users\ADMIN\OneDrive\Desktop\sanzad_global_dashboard"

echo Running PowerShell backup script...
powershell -ExecutionPolicy Bypass -File ".\backup_sanzad.ps1"

echo.
echo Backup finished. Press any key to close this window.
pause >nul
