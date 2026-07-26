@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
call "%CD%\game\win32\start_server_gui.bat" --self-test --timeout 45
set "TEST_EXIT=%ERRORLEVEL%"
echo.
if "%TEST_EXIT%"=="0" (
    echo Server lifecycle test passed.
) else (
    echo Server lifecycle test failed with code %TEST_EXIT%.
)
pause
exit /b %TEST_EXIT%
