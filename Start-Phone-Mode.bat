@echo off
title NeonClipping Phone Remote
cd /d "%~dp0"
echo ==============================================
echo  NeonClipping Phone Mode
echo  Make clips directly from your mobile phone!
echo ==============================================
set NEONCLIPPING_LAN=1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$env:NEONCLIPPING_LAN='1'; .\run.ps1"
pause
