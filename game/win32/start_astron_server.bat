@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Open Town - Astron Server
cd /d "%~dp0..\astron\win32"
astrond.exe --loglevel info ..\config\astrond.yml
set "SERVER_EXIT=%ERRORLEVEL%"
pause
exit /b %SERVER_EXIT%
