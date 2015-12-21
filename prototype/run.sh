#!/bin/sh
set -eu
RUNSCRIPT="`readlink -e -- "$0"`"
ROOTDIR="${RUNSCRIPT%/*}/.."
SRCDIR="$ROOTDIR/src"
[ $# -gt 0 ] || set -- "$ROOTDIR/data/dust-2014.dat"

make -C "$SRCDIR" all
exec python3.4 -O "$SRCDIR/main.py" "$@"
