#!/usr/bin/env bash
# Usage: emit-audit.sh <GATE> <PASS|FAIL|EXCEPTION> ; appends a hash-chained JSON record (schema: docs/03).
set -euo pipefail
GATE=$1; RESULT=$2; FILE=${AUDIT_FILE:-audit.jsonl}
prev=$(tail -n1 "$FILE" 2>/dev/null | jq -r .hash 2>/dev/null || echo "GENESIS")
rec=$(jq -cn --arg g "$GATE" --arg r "$RESULT" --arg run "${GITHUB_RUN_ID:-local}" --arg sha "${GITHUB_SHA:-0}" --arg ts "$(date -u +%FT%TZ)" --arg prev "$prev" --arg actor "${GITHUB_ACTOR:-local}" \
  '{event_id:(now|tostring), timestamp:$ts, pipeline_run_id:$run, git_sha:$sha, gate:$g, result:$r, actor:{deployer:$actor}, prev_hash:$prev}')
hash=$(printf '%s%s' "$rec" "$prev" | sha256sum | cut -d' ' -f1)
echo "$rec" | jq -c --arg h "$hash" '. + {hash:$h}' >> "$FILE"
# in CI: aws s3 cp --object-lock-mode COMPLIANCE ... ; ship to Loki
