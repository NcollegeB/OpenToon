#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ASTRON_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../astron" && pwd)
ASTRON="$ASTRON_ROOT/darwin/astrond"
if [ ! -x "$ASTRON" ]; then
    echo "Target-native macOS Astron was not found: $ASTRON" >&2
    exit 1
fi

cd "$ASTRON_ROOT/darwin"
exec "$ASTRON" --loglevel info ../config/astrond.yml
