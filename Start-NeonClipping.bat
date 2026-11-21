@echo off
title NeonClipping
cd /d "%~dp0"
echo NeonClipping start ho raha hai...
powershell -NoProfile -ExecutionPolicy Bypass -File run.ps1
pause
