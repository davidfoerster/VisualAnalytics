#!/bin/bash
set -eu -o pipefail
printf -v series 'uebung-%02d' "$1"
series_file="pack/$series-abgabe.tar.bz2"
case "$0" in
  */*) cd "${0%/*}";;
esac

find \
  src data/* doc prototype "screenshot/$series" "spec/$series" \
  \( -name __\* -prune -false \) -o \( -type f ! -name TODO\* -print0 \) |
xargs -r -0 -- git ls-files -z -- |
tar -vchaf "$series_file" --null -T -

echo "Created deliverable package »$series_file«." >&2
