[CmdletBinding()]
param(
    [string]$PythonExecutable = "",
    [string]$AstronExecutable = "",
    [switch]$SkipResources,
    [switch]$StartServerGui
)

$ErrorActionPreference = "Stop"
$bundleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$gameRoot = Join-Path $bundleRoot "game"
$resourceRoot = Join-Path $gameRoot "resources"
$resourceRepository = "https://github.com/open-toontown/resources.git"
$resourceRevision = "d8c73a9978633979ddf2ef8813f0152037a0d978"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command,
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage (exit code $LASTEXITCODE)"
    }
}

function Test-CompatiblePython {
    param([string]$Candidate)

    if (-not $Candidate) {
        return $false
    }
    $expanded = [Environment]::ExpandEnvironmentVariables($Candidate.Trim('"'))
    if (-not (Test-Path -LiteralPath $expanded -PathType Leaf)) {
        return $false
    }

    & $expanded -B -c `
        "import panda3d.core, panda3d.otp, panda3d.toontown, pytz" `
        *> $null
    return $LASTEXITCODE -eq 0
}

function Get-ConfiguredPythonCandidates {
    $candidates = [System.Collections.Generic.List[string]]::new()

    if ($PythonExecutable) {
        $candidates.Add($PythonExecutable)
    }
    if ($env:OPEN_TOONTOWN_PYTHON) {
        $candidates.Add($env:OPEN_TOONTOWN_PYTHON)
    }
    if ($env:PPYTHON_PATH) {
        $candidates.Add($env:PPYTHON_PATH)
    }

    $configPath = Join-Path $gameRoot "PPYTHON_PATH"
    if (Test-Path -LiteralPath $configPath -PathType Leaf) {
        $configuredLine = Get-Content -LiteralPath $configPath |
            Where-Object {
                $_.Trim() -and
                -not $_.TrimStart().StartsWith("#") -and
                -not $_.TrimStart().StartsWith(";")
        } |
            Select-Object -First 1
        if ($configuredLine) {
            $configuredCandidate = [Environment]::ExpandEnvironmentVariables(
                $configuredLine.Trim('"')
            )
            if (-not [System.IO.Path]::IsPathRooted($configuredCandidate)) {
                $configuredCandidate = Join-Path `
                    $gameRoot `
                    $configuredCandidate
            }
            $candidates.Add($configuredCandidate)
        }
    }

    $candidates.Add(
        (Join-Path $bundleRoot `
            "runtime\Panda3D-1.11.0-x64\python\ppython.exe")
    )

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $candidates.Add($pythonCommand.Source)
    }

    return $candidates | Select-Object -Unique
}

Write-Host ""
Write-Host "OpenToon local setup" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    throw "Git is required but was not found on PATH."
}

$resourcesReady = $false
if ($SkipResources) {
    $resourcesReady = Test-Path -LiteralPath $resourceRoot -PathType Container
    Write-Host "Resource download skipped."
} elseif (Test-Path -LiteralPath (Join-Path $resourceRoot ".git")) {
    [string]$currentRevision = & git -C $resourceRoot rev-parse HEAD 2>$null
    $currentRevision = $currentRevision.Trim()
    if ($LASTEXITCODE -ne 0 -or -not $currentRevision) {
        Write-Host "Resuming the incomplete resource checkout..."
        Invoke-Checked {
            git -C $resourceRoot fetch --depth 1 origin $resourceRevision
        } "Fetching the resource snapshot failed"
        Invoke-Checked {
            git -C $resourceRoot checkout --detach FETCH_HEAD
        } "Checking out the resource snapshot failed"
        [string]$currentRevision = & git -C $resourceRoot rev-parse HEAD
        $currentRevision = $currentRevision.Trim()
    }

    if ($currentRevision -eq $resourceRevision) {
        Write-Host "Resources are already at the compatible revision."
    } else {
        Write-Host (
            "An existing resource checkout is present at revision " +
            "$currentRevision; it was left unchanged."
        ) -ForegroundColor Yellow
    }
    $resourcesReady = $true
} elseif (
    (Test-Path -LiteralPath $resourceRoot -PathType Container) -and
    (Get-ChildItem -LiteralPath $resourceRoot -Force | Select-Object -First 1)
) {
    Write-Host (
        "An existing non-Git resource tree is present; it was left unchanged."
    ) -ForegroundColor Yellow
    $resourcesReady = $true
} else {
    Write-Host "Downloading the compatible resource snapshot..."
    New-Item -ItemType Directory -Path $resourceRoot -Force | Out-Null
    Invoke-Checked {
        git -C $resourceRoot init
    } "Initializing the resource checkout failed"
    Invoke-Checked {
        git -C $resourceRoot remote add origin $resourceRepository
    } "Configuring the resource remote failed"
    Invoke-Checked {
        git -C $resourceRoot fetch --depth 1 origin $resourceRevision
    } "Downloading the resource snapshot failed"
    Invoke-Checked {
        git -C $resourceRoot checkout --detach FETCH_HEAD
    } "Checking out the resource snapshot failed"
    $resourcesReady = $true
    Write-Host "Resource snapshot installed in game\resources."
}

Write-Host (
    "Resources remain a separate third-party download and are not covered " +
    "by OpenToon's MIT License."
) -ForegroundColor DarkYellow

$resolvedPython = $null
foreach ($candidate in Get-ConfiguredPythonCandidates) {
    if (Test-CompatiblePython $candidate) {
        $resolvedPython = (
            Resolve-Path -LiteralPath (
                [Environment]::ExpandEnvironmentVariables($candidate.Trim('"'))
            )
        ).Path
        break
    }
}

if ($resolvedPython) {
    Set-Content -LiteralPath (Join-Path $gameRoot "PPYTHON_PATH") `
        -Value $resolvedPython `
        -NoNewline
    Write-Host "Compatible game Python: $resolvedPython"
} else {
    Write-Host ""
    Write-Host "A compatible game Python was not found." -ForegroundColor Yellow
    Write-Host (
        "Rerun with -PythonExecutable pointing to Python 3.9/PPython " +
        "containing panda3d.otp and panda3d.toontown."
    )
}

$astronDestination = Join-Path $gameRoot "astron\win32\astrond.exe"
if ($AstronExecutable) {
    $astronSource = (
        Resolve-Path -LiteralPath $AstronExecutable -ErrorAction Stop
    ).Path
    New-Item -ItemType Directory `
        -Path (Split-Path $astronDestination -Parent) `
        -Force |
        Out-Null
    Copy-Item -LiteralPath $astronSource `
        -Destination $astronDestination `
        -Force
    Write-Host "Astron installed at game\astron\win32\astrond.exe."
}

$astronReady = Test-Path -LiteralPath $astronDestination -PathType Leaf
if (-not $astronReady) {
    Write-Host ""
    Write-Host "Astron is not installed." -ForegroundColor Yellow
    Write-Host (
        "Rerun with -AstronExecutable pointing to a compatible Windows " +
        "astrond.exe."
    )
}

$ready = $resourcesReady -and $resolvedPython -and $astronReady
if ($ready) {
    Write-Host ""
    Write-Host "OpenToon is ready for local startup." -ForegroundColor Green
    Write-Host "Run: 1 - Open Town Server GUI.bat"
    Write-Host "Then: 2 - Open Town Client.bat"

    if ($StartServerGui) {
        & (Join-Path $bundleRoot "1 - Open Town Server GUI.bat")
    }
    exit 0
}

Write-Host ""
Write-Host (
    "Resource setup is complete, but the missing native dependencies above " +
    "must be supplied before the client/server can start."
) -ForegroundColor Yellow
exit 2
