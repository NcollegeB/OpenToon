@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0.."

rem Prefer a normal Python installation with Tkinter for the GUI itself.
where py.exe >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import tkinter" >nul 2>&1
    if not errorlevel 1 (
        py -3 "%CD%\tools\server_gui.py" %*
        if errorlevel 1 exit /b 1
        exit /b 0
    )
)

where python.exe >nul 2>&1
if not errorlevel 1 (
    python -c "import tkinter" >nul 2>&1
    if not errorlevel 1 (
        python "%CD%\tools\server_gui.py" %*
        if errorlevel 1 exit /b 1
        exit /b 0
    )
)

rem Fall back to the configured Panda3D Python if it includes Tkinter.
set "GUI_RUNTIME="
if exist "%CD%\PPYTHON_PATH" set /p "GUI_RUNTIME="<"%CD%\PPYTHON_PATH"
set "GUI_RUNTIME=%GUI_RUNTIME:"=%"
if defined GUI_RUNTIME if not exist "%GUI_RUNTIME%" set "GUI_RUNTIME="
if not defined GUI_RUNTIME set "GUI_RUNTIME=%~dp0..\..\runtime\Panda3D-1.11.0-x64\python\ppython.exe"
if defined GUI_RUNTIME if exist "%GUI_RUNTIME%" (
    "%GUI_RUNTIME%" -c "import tkinter" >nul 2>&1
    if not errorlevel 1 (
        "%GUI_RUNTIME%" "%CD%\tools\server_gui.py" %*
        if errorlevel 1 exit /b 1
        exit /b 0
    )
)

echo.
echo Unable to find a Python 3 installation with Tkinter.
echo Install no resources from this launcher. Configure an existing Python or
echo Panda3D PPython runtime, then run this file again.
echo See tools\SERVER_GUI.md for details.
echo.
pause
exit /b 1
