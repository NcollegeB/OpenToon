@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
call "%CD%\game\win32\start_game.bat"
exit /b %ERRORLEVEL%
