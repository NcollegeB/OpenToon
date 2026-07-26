#!/bin/sh
set -eu

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BUILT_LAUNCHER="$BUNDLE_ROOT/launcher/dist/macos/OpenTownLauncher.app/Contents/MacOS/OpenTownLauncher"
if [ -x "$BUILT_LAUNCHER" ]; then
    exec "$BUILT_LAUNCHER"
fi

. "$BUNDLE_ROOT/game/tools/platform_runtime.sh"
GAME_PYTHON=$(find_open_toontown_python "$BUNDLE_ROOT")
exec "$GAME_PYTHON" \
    "$BUNDLE_ROOT/launcher/src/open_toontown_launcher.py"
