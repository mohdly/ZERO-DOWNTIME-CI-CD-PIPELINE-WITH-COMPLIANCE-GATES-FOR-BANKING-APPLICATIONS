#!/usr/bin/env bash
# Fails if any commit in range lacks a verified signature (GPG/SSH). Requires allowed signers configured.
set -euo pipefail
RANGE="${1:-origin/main}..${2:-HEAD}"; bad=0
for c in $(git rev-list "$RANGE"); do
  st=$(git log -1 --format='%G?' "$c")
  if [[ "$st" != "G" && "$st" != "U" ]]; then echo "UNSIGNED/INVALID: $c ($st)"; bad=1; fi
done
exit $bad
