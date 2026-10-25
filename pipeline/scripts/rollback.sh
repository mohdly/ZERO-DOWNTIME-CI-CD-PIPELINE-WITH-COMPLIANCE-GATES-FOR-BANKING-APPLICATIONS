#!/usr/bin/env bash
# Break-glass rollback; talks to the cluster directly (no CI/registry/ArgoCD dependency). Usage: rollback.sh <app> [namespace]
set -euo pipefail
APP=$1; NS=${2:-novapay-prod}
kubectl argo rollouts abort "$APP" -n "$NS" || true
kubectl argo rollouts undo "$APP" -n "$NS" || true
kubectl -n "$NS" patch virtualservice "$APP" --type=json -p='[{"op":"replace","path":"/spec/http/0/route/0/weight","value":100},{"op":"replace","path":"/spec/http/0/route/1/weight","value":0}]'
echo "$(date -u +%FT%TZ) rollback executed for $APP in $NS by ${USER:-unknown}" | tee -a "${ROLLBACK_LOG:-/var/log/novapay-rollback.log}" || true
