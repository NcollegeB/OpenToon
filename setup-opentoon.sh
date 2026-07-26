#!/bin/sh
set -eu

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
GAME_ROOT="$BUNDLE_ROOT/game"
RESOURCE_ROOT="$GAME_ROOT/resources"
RESOURCE_REPOSITORY="https://github.com/open-toontown/resources.git"
RESOURCE_REVISION="d8c73a9978633979ddf2ef8813f0152037a0d978"

printf '\nOpenToon local setup\n'
printf '%s\n' '==================='

if ! command -v git >/dev/null 2>&1; then
    printf '%s\n' 'Git is required but was not found on PATH.' >&2
    exit 1
fi

if [ -d "$RESOURCE_ROOT/.git" ]; then
    current_revision=$(
        git -C "$RESOURCE_ROOT" rev-parse HEAD 2>/dev/null || true
    )
    if [ -z "$current_revision" ]; then
        printf '%s\n' 'Resuming the incomplete resource checkout...'
        git -C "$RESOURCE_ROOT" fetch --depth 1 origin "$RESOURCE_REVISION"
        git -C "$RESOURCE_ROOT" checkout --detach FETCH_HEAD
        current_revision=$(git -C "$RESOURCE_ROOT" rev-parse HEAD)
    fi

    if [ "$current_revision" = "$RESOURCE_REVISION" ]; then
        printf '%s\n' 'Resources are already at the compatible revision.'
    else
        printf '%s\n' \
            "Existing resources at $current_revision were left unchanged."
    fi
elif [ -d "$RESOURCE_ROOT" ] &&
    [ -n "$(ls -A "$RESOURCE_ROOT" 2>/dev/null)" ]
then
    printf '%s\n' \
        'An existing non-Git resource tree was left unchanged.'
else
    printf '%s\n' 'Downloading the compatible resource snapshot...'
    mkdir -p "$RESOURCE_ROOT"
    git -C "$RESOURCE_ROOT" init
    git -C "$RESOURCE_ROOT" remote add origin "$RESOURCE_REPOSITORY"
    git -C "$RESOURCE_ROOT" fetch --depth 1 origin "$RESOURCE_REVISION"
    git -C "$RESOURCE_ROOT" checkout --detach FETCH_HEAD
    printf '%s\n' 'Resource snapshot installed in game/resources.'
fi

printf '%s\n' \
    "Resources remain a separate third-party download and are not covered" \
    "by OpenToon's MIT License."

. "$GAME_ROOT/tools/platform_runtime.sh"
if game_python=$(find_open_toontown_python "$BUNDLE_ROOT"); then
    printf 'Compatible game Python: %s\n' "$game_python"
    python_ready=1
else
    python_ready=0
fi

case "$(uname -s)" in
    Darwin)
        astron="$GAME_ROOT/astron/darwin/astrond"
        ;;
    Linux)
        astron="$GAME_ROOT/astron/linux/astrond"
        ;;
    *)
        printf '%s\n' \
            'This setup script supports macOS and Linux.' >&2
        exit 1
        ;;
esac

if [ -x "$astron" ]; then
    printf 'Astron: %s\n' "$astron"
    astron_ready=1
else
    printf '%s\n' \
        "Astron is missing: $astron" \
        'Build or obtain a target-native Astron executable and place it there.'
    astron_ready=0
fi

if [ "$python_ready" -eq 1 ] && [ "$astron_ready" -eq 1 ]; then
    printf '\n%s\n' 'OpenToon is ready for local startup.'
    exit 0
fi

printf '\n%s\n' \
    'Resource setup is complete, but the missing native dependencies above' \
    'must be supplied before the client/server can start.'
exit 2
