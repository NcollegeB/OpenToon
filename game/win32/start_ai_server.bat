@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Open Town - AI (District) Server
cd /d "%~dp0.."

set "GAME_RUNTIME="
if exist "%CD%\PPYTHON_PATH" set /p "GAME_RUNTIME="<"%CD%\PPYTHON_PATH"
set "GAME_RUNTIME=%GAME_RUNTIME:"=%"
if defined GAME_RUNTIME if not exist "%GAME_RUNTIME%" set "GAME_RUNTIME="
if not defined GAME_RUNTIME set "GAME_RUNTIME=%~dp0..\..\runtime\Panda3D-1.11.0-x64\python\ppython.exe"
if not exist "%GAME_RUNTIME%" (
    echo Compatible Panda3D PPython was not found.
    echo Expected: %GAME_RUNTIME%
    pause
    exit /b 1
)

:main
"%GAME_RUNTIME%" -u -m toontown.ai.AIStart --base-channel 401000000 ^
               --max-channels 999999 --stateserver 4002 ^
               --messagedirector-ip 127.0.0.1:7199 ^
               --eventlogger-ip 127.0.0.1:7197 ^
               --district-name "Toon Valley"
echo AI server exited with code %ERRORLEVEL%. Restarting...
goto main
