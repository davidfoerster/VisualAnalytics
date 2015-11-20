#!/bin/sh
set -eu
RUNSCRIPT="`readlink -e -- "$0"`"
SCRIPTDIR="${RUNSCRIPT%/*}"
SRCDIR="$SCRIPTDIR/src"
[ $# -gt 0 ] || set -- "$SCRIPTDIR/data/data-j-m"

make -C "$SRCDIR" all
exec python3.4 -O "$SRCDIR/main.py" "$@"
