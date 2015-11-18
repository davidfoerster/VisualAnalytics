#!/bin/bash
set -eu -o pipefail
printf -v series 'uebung-%02d' "$1"
series_file="pack/$series-abgabe.tar.bz2"
cd "${0/*}" 2>&- || true

find \
  src data/DateInDays.txt data/January.txt doc run.sh "screenshot/$series" "spec/$series" \
  \( -name __\* -prune -false \) -o \( -type f ! -name TODO\* -print0 \) |
xargs -r -0 -- git ls-files -z -- |
tar -vchaf "$series_file" --null -T -

echo "Created deliverable package »$series_file«." >&2
