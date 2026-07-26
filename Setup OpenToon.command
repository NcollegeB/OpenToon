#!/bin/sh

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
"$BUNDLE_ROOT/setup-opentoon.sh"
setup_exit=$?

printf '\nPress Return to close...'
read ignored
exit "$setup_exit"
