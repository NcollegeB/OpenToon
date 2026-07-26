param(
    [string]$PythonExecutable = ""
)

$ErrorActionPreference = "Stop"
$launcherRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$bundleRoot = Split-Path -Parent $launcherRoot
$source = Join-Path $launcherRoot "src\open_toontown_launcher.py"
$tools = Join-Path $launcherRoot ".build-tools\windows"
$work = Join-Path $launcherRoot ".build\windows"
$dist = Join-Path $launcherRoot "dist\windows"

if (-not $PythonExecutable) {
    $PythonExecutable = $env:OPEN_TOONTOWN_BUILD_PYTHON
}
if (-not $PythonExecutable) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $PythonExecutable = $pythonCommand.Source
    }
}
if (-not $PythonExecutable) {
    $PythonExecutable = Join-Path $bundleRoot `
        "runtime\Panda3D-1.11.0-x64\python\ppython.exe"
}
if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) {
    throw (
        "Python executable was not found. Pass -PythonExecutable or set " +
        "OPEN_TOONTOWN_BUILD_PYTHON."
    )
}

New-Item -ItemType Directory -Force -Path $tools, $work, $dist | Out-Null
& $PythonExecutable -m pip install `
    --disable-pip-version-check `
    --upgrade `
    --target $tools `
    -r (Join-Path $launcherRoot "requirements-build.txt")
if ($LASTEXITCODE -ne 0) {
    throw "Installing the launcher build tools failed."
}

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = if ($previousPythonPath) {
        "$tools;$previousPythonPath"
    } else {
        $tools
    }
    & $PythonExecutable -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --name OpenTownLauncher `
        --distpath $dist `
        --workpath $work `
        --specpath $work `
        $source
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed."
    }
} finally {
    $env:PYTHONPATH = $previousPythonPath
}

$executable = Join-Path $dist "OpenTownLauncher.exe"
if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "Expected launcher output was not created: $executable"
}
Write-Host "Built launcher: $executable"
