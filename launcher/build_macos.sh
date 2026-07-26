#!/bin/sh
set -eu

LAUNCHER_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${OPEN_TOONTOWN_BUILD_PYTHON:-python3}
VENV="$LAUNCHER_ROOT/.build-venv/macos"
DIST="$LAUNCHER_ROOT/dist/macos"
WORK="$LAUNCHER_ROOT/.build/macos"

"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install \
    -r "$LAUNCHER_ROOT/requirements-build.txt"
"$VENV/bin/python" -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --windowed \
    --name OpenTownLauncher \
    --distpath "$DIST" \
    --workpath "$WORK" \
    --specpath "$WORK" \
    "$LAUNCHER_ROOT/src/open_toontown_launcher.py"

printf 'Built launcher: %s\n' \
    "$DIST/OpenTownLauncher.app"
