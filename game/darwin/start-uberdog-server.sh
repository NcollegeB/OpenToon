#!/bin/sh
set -eu

MAX_CHANNELS=999999
STATE_SERVER=4002
MESSAGE_DIRECTOR_IP="127.0.0.1:7199"
EVENT_LOGGER_IP="127.0.0.1:7197"
BASE_CHANNEL=1000000

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
GAME_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
BUNDLE_ROOT=$(CDPATH= cd -- "$GAME_ROOT/.." && pwd)
. "$GAME_ROOT/tools/platform_runtime.sh"
GAME_PYTHON=$(find_open_toontown_python "$BUNDLE_ROOT")
cd "$GAME_ROOT"

exec "$GAME_PYTHON" -u -m toontown.uberdog.UDStart --base-channel ${BASE_CHANNEL} \
               --max-channels ${MAX_CHANNELS} --stateserver ${STATE_SERVER} \
               --messagedirector-ip ${MESSAGE_DIRECTOR_IP} \
               --eventlogger-ip ${EVENT_LOGGER_IP}
