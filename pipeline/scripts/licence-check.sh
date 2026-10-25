#!/usr/bin/env bash
# Usage: licence-check.sh sbom.cdx.json  -> fail on GPL/AGPL/SSPL
set -euo pipefail
hits=$(jq -r '[.components[]? | {n:.name, l:([.licenses[]?.license.id // .licenses[]?.license.name] | join(","))} | select(.l | test("(^|,)(A?GPL|SSPL)"; "i"))] | .[] | "\(.n): \(.l)"' "$1")
if [[ -n "$hits" ]]; then echo "Forbidden licences:"; echo "$hits"; exit 1; fi
echo "Licence gate passed"
