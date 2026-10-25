#!/usr/bin/env bash
# One-command validation of every machine-checkable artefact in this repository.
# Run from repo root:  bash pipeline/scripts/validate.sh        (missing optional tools are reported as SKIP, never silently ignored)
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || dirname "$(dirname "$(dirname "$0")")")" || exit 1
rc=0; pass=0; fail=0; skip=0
step() { local name=$1; shift; printf '== %-34s' "$name"; if out=$("$@" 2>&1); then echo "PASS"; pass=$((pass+1)); else echo "FAIL"; echo "$out" | tail -15; fail=$((fail+1)); rc=1; fi; }
opt()  { local tool=$1; shift; if command -v "$tool" >/dev/null; then step "$@"; else printf '== %-34sSKIP (%s not installed)\n' "$1" "$tool"; skip=$((skip+1)); fi; }

YL='{extends: relaxed, rules: {line-length: disable, colons: disable, braces: disable, truthy: disable, comments: disable}}'
opt yamllint "yamllint (workflows, k8s, rules)" yamllint -d "$YL" pipeline/.github pipeline/policies pipeline/helm/novapay/Chart.yaml pipeline/helm/novapay/values.yaml pipeline/argocd docs/06-rollback-specification docs/08-observability pipeline/scripts/blackout-calendar.yaml
step "JSON (dashboards)" bash -c 'find . -name "*.json" -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null'
step "Dashboards regenerate identically" bash -c 'cd dashboards/grafana && cp engineering-dashboard.json /tmp/e.json && python3 generate_dashboards.py >/dev/null && cmp /tmp/e.json engineering-dashboard.json'
opt shellcheck "shellcheck (scripts)" shellcheck pipeline/scripts/*.sh
opt opa "opa check (Rego v1)" opa check --v1-compatible pipeline/policies
opt opa "opa test (policy unit tests)" opa test --v1-compatible pipeline/policies -v
opt promtool "promtool check rules" bash -c 'promtool check rules docs/06-rollback-specification/rollback-alerts.yaml docs/08-observability/observability-rules.yaml'
opt promtool "promtool test rules (alerts)" bash -c '(cd docs/06-rollback-specification && promtool test rules rollback-alerts.test.yaml) && (cd docs/08-observability && promtool test rules observability-rules.test.yaml)'
opt python3 "pytest (canary, ML, fleet guard)" python3 -m pytest pipeline/scripts/tests -q
if command -v terraform >/dev/null; then TF=terraform; else TF=tofu; fi
opt "$TF" "terraform/tofu fmt -check" "$TF" fmt -check -recursive pipeline/terraform
opt helm "helm lint" helm lint pipeline/helm/novapay
if command -v helm >/dev/null; then CT=conftest; else CT=helm; fi
opt "$CT" "conftest (rendered chart vs policies)" bash -c 'helm template novapay pipeline/helm/novapay | conftest test - --policy pipeline/policies'
echo; echo "SUMMARY: $pass passed, $fail failed, $skip skipped"; exit $rc
