#!/bin/bash
# AirBeats — snap launcher
#
# WHY THIS FILE EXISTS
# --------------------
# electron-builder used to package the snap with the "snap-template-electron-4.0-2"
# template. That template shipped a `command.sh` which chained:
#
#     exec "$SNAP/desktop-init.sh" "$SNAP/desktop-common.sh" \
#          "$SNAP/desktop-gnome-specific.sh" "$SNAP/airbeats" --no-sandbox "$@"
#
# Modern snapcraft no longer extracts that template, so none of those three
# scripts end up inside the .snap. The published snap therefore dies instantly:
#
#     /snap/airbeats/6/command.sh: line 2:
#     /snap/airbeats/6/desktop-init.sh: No such file or directory
#
# `snapcraft.yaml` next to this file points the snap's `command:` here instead,
# which invokes the Electron binary directly and works on every base.

set -e

# Electron needs a writable temp dir; inside a snap $SNAP is read-only.
if [ -z "${TMPDIR:-}" ] || [ ! -w "${TMPDIR:-/nonexistent}" ]; then
    export TMPDIR="${XDG_RUNTIME_DIR:-/tmp}"
fi

APP_BIN="$SNAP/airbeats"

if [ ! -x "$APP_BIN" ]; then
    echo "AirBeats: executable not found at $APP_BIN" >&2
    exit 1
fi

# Chromium/Electron refuses to run as root inside snaps.
if [ "$(id -u)" = "0" ]; then
    echo "AirBeats: refusing to run as root." >&2
    exit 1
fi

exec "$APP_BIN" --no-sandbox "$@"