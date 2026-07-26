@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Open Town - Game Client
cd /d "%~dp0.."

rem Read the configured bundled Panda3D runtime.
set "GAME_RUNTIME="
if exist "%CD%\PPYTHON_PATH" set /p "GAME_RUNTIME="<"%CD%\PPYTHON_PATH"
set "GAME_RUNTIME=%GAME_RUNTIME:"=%"
if defined GAME_RUNTIME if not exist "%GAME_RUNTIME%" set "GAME_RUNTIME="
if not defined GAME_RUNTIME set "GAME_RUNTIME=%~dp0..\..\runtime\Panda3D-1.11.0-x64\python\ppython.exe"
if not exist "%GAME_RUNTIME%" (
    echo Panda3D PPython was not found:
    echo %GAME_RUNTIME%
    pause
    exit /b 1
)
"%GAME_RUNTIME%" -c "import panda3d.core, panda3d.otp, panda3d.toontown, pytz" >nul 2>&1
if errorlevel 1 (
    echo The selected Python runtime is missing the custom Open Town
    echo Panda3D modules: panda3d.otp and panda3d.toontown.
    pause
    exit /b 1
)

set "LOGIN_TOKEN=dev"
set "GAME_SERVER=127.0.0.1"

"%GAME_RUNTIME%" -u -m toontown.launcher.QuickStartLauncher
set "GAME_EXIT=%ERRORLEVEL%"
echo.
echo Open Town exited with code %GAME_EXIT%.
pause
exit /b %GAME_EXIT%
