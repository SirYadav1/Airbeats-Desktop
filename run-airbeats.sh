#!/usr/bin/env bash
# AirBeats — Linux AppImage launcher with a FUSE fallback.
#
# WHY THIS FILE EXISTS
# --------------------
# The official AppImage is type-2 FUSE: it dlopen()s `libfuse.so.2`.
# That library is gone from current distributions:
#
#   * Ubuntu 24.04+ (noble)      -> only libfuse3, `apt install libfuse2t64`
#   * Debian 12+ (bookworm)      -> only libfuse3
#   * Fedora 39+                 -> only fuse3
#
# Result on a fresh Ubuntu 24.04 install:
#
#     $ ./Airbeats-v6.3.0-linux.AppImage
#     dlopen(): error loading libfuse.so.2
#     AppImages require FUSE to run.
#
# The AppImage supports a built-in escape hatch — `--appimage-extract-and-run` —
# which unpacks it into $TMPDIR instead of mounting it. This wrapper picks that
# automatically so the AppImage just works, while staying a normal double-click
# target when FUSE 2 *is* available.
#
# Usage:  ./run-airbeats.sh [path/to/Airbeats-*.AppImage]

set -euo pipefail

has_fuse2() {
    ldconfig -p 2>/dev/null | grep -q 'libfuse\.so\.2' && return 0
    # libfuse2 on newer distros may ship under a slightly different soname
    [ -e /usr/lib/*/libfuse.so.2 ] && return 0
    [ -e /usr/lib/libfuse.so.2 ] && return 0
    return 1
}

APPIMAGE="${1:-}"
if [ -z "$APPIMAGE" ]; then
    APPIMAGE="$(dirname "$0")"/Airbeats-*.AppImage
    # shellcheck disable=SC2086
    set -- $APPIMAGE
    APPIMAGE="${1:-}"
fi

if [ ! -f "$APPIMAGE" ]; then
    echo "airbeats: AppImage not found." >&2
    echo "usage: $0 /path/to/Airbeats-*.AppImage" >&2
    exit 1
fi

chmod +x "$APPIMAGE" 2>/dev/null || true

if has_fuse2; then
    echo "airbeats: FUSE 2 present — mounting AppImage." >&2
    exec "$APPIMAGE" --no-sandbox "$@"
fi

echo "airbeats: libfuse.so.2 not found (Ubuntu 24.04+ / Debian 12+ / Fedora 39+)." >&2
echo "airbeats: falling back to --appimage-extract-and-run." >&2
echo "airbeats: to silence this, either install FUSE 2 or run the .deb package:" >&2
echo "            sudo apt install libfuse2t64     # Ubuntu 24.04+" >&2
echo "            sudo apt install ./Airbeats-*-linux.deb" >&2

exec "$APPIMAGE" --appimage-extract-and-run --no-sandbox "$@"