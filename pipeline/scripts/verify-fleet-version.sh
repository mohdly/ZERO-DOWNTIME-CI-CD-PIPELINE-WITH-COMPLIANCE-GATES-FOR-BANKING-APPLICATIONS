#!/usr/bin/env bash
# Knight Capital guard. Usage: verify-fleet-version.sh <namespace> <app> <expected-digest>
# Checks: (a) single image digest on all pods (b) config hash identical (c) kill-switch on mismatch (d) inventory recorded.
set -euo pipefail
NS=$1; APP=$2; WANT=$3
inv=$(kubectl -n "$NS" get pods -l app="$APP" -o json | jq -c '[.items[] | {pod:.metadata.name, digest:(.status.containerStatuses[0].imageID | split("@")[1]), cfg:(.metadata.annotations["novapay/config-sha"] // "none")}]')
echo "$inv" > "inventory-$(date -u +%s).json"                         # (d) inventory for audit
digests=$(echo "$inv" | jq -r '[.[].digest] | unique | length'); cfgs=$(echo "$inv" | jq -r '[.[].cfg] | unique | length')
want_count=$(echo "$inv" | jq --arg w "$WANT" '[.[] | select(.digest==$w)] | length'); total=$(echo "$inv" | jq 'length')
# During a canary, two digests are expected (stable+canary); at 100% exactly one equal to target.
if [[ "${ALLOW_MIXED:-false}" == "true" ]]; then ok=$([[ $digests -le 2 && $cfgs -le 2 ]] && echo y || echo n)
else ok=$([[ $digests -eq 1 && $cfgs -eq 1 && $want_count -eq $total ]] && echo y || echo n); fi
if [[ $ok != y ]]; then
  echo "FLEET MISMATCH: digests=$digests configs=$cfgs target_pods=$want_count/$total -> KILL SWITCH"
  "$(dirname "$0")/rollback.sh" "$APP" "$NS" || true                                   # (c) automated kill-switch
  exit 1
fi
echo "Fleet verified: $total pods on $WANT"
