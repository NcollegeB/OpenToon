param(
    [string[]]$Tokens = @('dev', 'dev2'),
    [string]$Minigame = 'maze',
    [string]$GameServer = '127.0.0.1',
    [string]$PythonExecutable = '',
    [int]$Width = 960,
    [int]$Height = 540
)

$ErrorActionPreference = 'Stop'
$gameRoot = Split-Path -Parent $PSScriptRoot

if (-not $PythonExecutable) {
    $pathFile = Join-Path $gameRoot 'PPYTHON_PATH'
    if (Test-Path -LiteralPath $pathFile) {
        $PythonExecutable = (
            Get-Content -LiteralPath $pathFile -Raw).Trim()
    }
}

if (-not $PythonExecutable) {
    $PythonExecutable = Join-Path (
        Split-Path -Parent $gameRoot
    ) 'runtime\Panda3D-1.11.0-x64\python\ppython.exe'
}

if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) {
    throw "Panda3D Python was not found: $PythonExecutable"
}

if ($Tokens.Count -lt 1 -or $Tokens.Count -gt 4) {
    throw 'Provide between one and four distinct local account tokens.'
}

if (($Tokens | Select-Object -Unique).Count -ne $Tokens.Count) {
    throw 'Every live client must use a distinct local account token.'
}

$processes = @()
$liveLogDirectory = Join-Path $gameRoot 'logs'
New-Item -ItemType Directory -Force -Path $liveLogDirectory | Out-Null
for ($index = 0; $index -lt $Tokens.Count; $index++) {
    $number = $index + 1
    $originX = ($index % 2) * $Width
    $originY = [math]::Floor($index / 2) * $Height
    $arguments = @(
        '-u',
        'tools\live_minigame_client.py',
        '--client-label', $number,
        '--title', "Open-Town-Live-$number",
        '--slot', '0',
        '--width', $Width,
        '--height', $Height,
        '--x', $originX,
        '--y', $originY,
        '--log-file', (
            Join-Path $liveLogDirectory "live-minigame-client-$number.log"
        )
    )
    if ($index -eq 0 -and $Minigame) {
        $arguments += @('--minigame', $Minigame)
    }

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $PythonExecutable
    $startInfo.WorkingDirectory = $gameRoot
    $startInfo.UseShellExecute = $false
    $startInfo.Arguments = (
        $arguments | ForEach-Object {
            '"' + ([string]$_).Replace('"', '\"') + '"'
        }) -join ' '
    $startInfo.EnvironmentVariables['LOGIN_TOKEN'] = $Tokens[$index]
    $startInfo.EnvironmentVariables['GAME_SERVER'] = $GameServer
    $startInfo.EnvironmentVariables['otp_client'] = "-live-$number"
    $startInfo.EnvironmentVariables['PYTHONUNBUFFERED'] = '1'
    $startInfo.EnvironmentVariables['PYTHONIOENCODING'] = 'utf-8'

    $process = [System.Diagnostics.Process]::Start($startInfo)
    $processes += [pscustomobject]@{
        Client = $number
        Token = $Tokens[$index]
        PID = $process.Id
    }
    Start-Sleep -Milliseconds 1200
}

$processes
