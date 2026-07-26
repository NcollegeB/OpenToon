@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%CD%\launcher\build_windows.ps1"
set "BUILD_EXIT=%ERRORLEVEL%"
echo.
if "%BUILD_EXIT%"=="0" (
    echo Windows launcher build completed.
) else (
    echo Windows launcher build failed with code %BUILD_EXIT%.
)
pause
exit /b %BUILD_EXIT%
