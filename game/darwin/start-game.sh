#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
GAME_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
BUNDLE_ROOT=$(CDPATH= cd -- "$GAME_ROOT/.." && pwd)
. "$GAME_ROOT/tools/platform_runtime.sh"
GAME_PYTHON=$(find_open_toontown_python "$BUNDLE_ROOT")

cd "$GAME_ROOT"
export LOGIN_TOKEN=dev
export GAME_SERVER="${GAME_SERVER:-127.0.0.1}"

exec "$GAME_PYTHON" -u -m toontown.launcher.QuickStartLauncher
