#!/bin/sh
set -eu
RUNSCRIPT="`readlink -e -- "$0"`"
BINDIR="${RUNSCRIPT%/*}"
[ $# -gt 0 ] || set -- "$BINDIR/data/data-j-m"

make -C "$BINDIR" all
exec python3.4 -O "$BINDIR/main.py" "$@"
