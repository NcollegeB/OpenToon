#!/bin/sh

# Locate a target-native Python that contains Open Town's custom Panda3D
# modules.  Stock Panda3D does not provide panda3d.otp or panda3d.toontown.
find_open_toontown_python() {
    bundle_root=$1

    for candidate in \
        "${OPEN_TOONTOWN_PYTHON:-}" \
        "$bundle_root/runtime/macos-arm64/bin/python3" \
        "$bundle_root/runtime/macos-x86_64/bin/python3" \
        "$bundle_root/runtime/linux-x86_64/bin/python3" \
        "$bundle_root/runtime/python/bin/python3" \
        "$(command -v python3.9 2>/dev/null || true)" \
        "$(command -v python3 2>/dev/null || true)"
    do
        if [ -n "$candidate" ] && [ -x "$candidate" ] &&
            "$candidate" -c \
                "import panda3d.core, panda3d.otp, panda3d.toontown, pytz" \
                >/dev/null 2>&1
        then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    printf '%s\n' \
        "No compatible target-native Python was found." \
        "Set OPEN_TOONTOWN_PYTHON to a Python 3.9 executable containing" \
        "the custom panda3d.otp and panda3d.toontown modules." >&2
    return 1
}
