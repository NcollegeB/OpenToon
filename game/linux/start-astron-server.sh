#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ASTRON_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../astron" && pwd)
ASTRON="$ASTRON_ROOT/linux/astrond"
if [ ! -x "$ASTRON" ]; then
    echo "Target-native Linux Astron was not found: $ASTRON" >&2
    echo "Build Astron on Linux and place it in game/astron/linux/." >&2
    exit 1
fi

cd "$ASTRON_ROOT/linux"
exec "$ASTRON" --loglevel info ../config/astrond.yml
