@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass ^
    -File "%CD%\Setup OpenToon.ps1" %*
set "SETUP_EXIT=%ERRORLEVEL%"

echo.
if "%SETUP_EXIT%"=="0" (
    echo OpenToon setup completed.
) else (
    echo OpenToon setup needs attention. Exit code: %SETUP_EXIT%
)
pause
exit /b %SETUP_EXIT%
