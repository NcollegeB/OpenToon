@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"

set "BUILT_LAUNCHER=%CD%\launcher\dist\windows\OpenTownLauncher.exe"
if exist "%BUILT_LAUNCHER%" (
    start "" "%BUILT_LAUNCHER%"
    exit /b 0
)

set "LAUNCHER_PYTHON=%OPEN_TOONTOWN_PYTHON%"
if not defined LAUNCHER_PYTHON if exist "%CD%\game\PPYTHON_PATH" (
    set /p "LAUNCHER_PYTHON="<"%CD%\game\PPYTHON_PATH"
)
set "LAUNCHER_PYTHON=%LAUNCHER_PYTHON:"=%"
if defined LAUNCHER_PYTHON if not exist "%LAUNCHER_PYTHON%" set "LAUNCHER_PYTHON="
if not defined LAUNCHER_PYTHON (
    set "LAUNCHER_PYTHON=%CD%\runtime\Panda3D-1.11.0-x64\python\ppython.exe"
)
if not exist "%LAUNCHER_PYTHON%" (
    echo Compatible Python was not found: %LAUNCHER_PYTHON%
    echo Set OPEN_TOONTOWN_PYTHON or copy game\PPYTHON_PATH.example
    echo to game\PPYTHON_PATH and put the runtime path on its first line.
    pause
    exit /b 1
)
"%LAUNCHER_PYTHON%" "%CD%\launcher\src\open_toontown_launcher.py"
exit /b %ERRORLEVEL%
