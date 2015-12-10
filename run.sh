#!/bin/sh
set -eu
RUNSCRIPT="`readlink -e -- "$0"`"
SCRIPTDIR="${RUNSCRIPT%/*}"
SRCDIR="$SCRIPTDIR/src"
[ $# -gt 0 ] || set -- "$SCRIPTDIR/data/dust-2014.dat"

make -C "$SRCDIR" all
exec python3.4 -O "$SRCDIR/main.py" "$@"
