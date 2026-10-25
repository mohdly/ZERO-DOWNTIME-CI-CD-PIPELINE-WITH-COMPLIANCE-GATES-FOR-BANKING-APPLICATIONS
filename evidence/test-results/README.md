# Test results — real runs, reproducible

> **AI Attribution:** Test suites drafted with Claude (Anthropic) on 23 Oct 2026 and executed in the build environment that day (outputs below are the unedited results). **Re-run on your own machine before submitting:** `bash pipeline/scripts/validate.sh`.

| Check | Tool / version | Result | Output file |
|---|---|---|---|
| OPA policy unit tests (13: image digest, privileged, limits, non-root, plaintext secret, TLS 1.3, SoD ×5) | OPA 1.4.2 | **13/13 PASS** | [opa-policy-tests.txt](opa-policy-tests.txt) |
| Rego syntax/type check (Rego v1) | OPA 1.4.2 | PASS | validate-summary.txt |
| Rollback alert rules (D6) — 5 promtool unit tests incl. Section B5 scenario (12 % 5xx, pool exhaustion, 35 % gateway timeouts) | promtool 2.55.1 | **SUCCESS** (9 rules) | [promtool-rollback-alerts.txt](promtool-rollback-alerts.txt) |
| Observability rules (D8) — UPI TD% detected ≤30 s, probes, 30-min regulatory timer, audit chain | promtool 2.55.1 | **SUCCESS** (11 rules) | [promtool-observability-rules.txt](promtool-observability-rules.txt) |
| Canary statistics (Welch t / χ² / composite), Knight-Capital fleet guard (7-of-8 pods scenario), ML sandbox — 15 tests | pytest | **15 passed** | [pytest-canary-ml-fleet.txt](pytest-canary-ml-fleet.txt) |
| YAML lint — workflows, policies, Helm values, rules | yamllint | PASS (0 errors) | [yamllint-workflows.txt](yamllint-workflows.txt) |
| Shell scripts | ShellCheck 0.10 | PASS | [shellcheck.txt](shellcheck.txt) |
| Terraform formatting | OpenTofu 1.8.5 `fmt -check` | PASS | [terraform-fmt.txt](terraform-fmt.txt) |
| Grafana dashboards: valid JSON, regenerate byte-identically from code | python | PASS | validate-summary.txt |

## What was NOT run (honest limits)
- `helm lint` / `helm template | conftest` — Helm was not available in the build sandbox → reported as **SKIP**, not pass. Run `validate.sh` on a machine with Helm (install: https://helm.sh/docs/intro/install/).
- `terraform init/validate/plan` — provider registry unreachable in the sandbox; only formatting was checked.
- No live Kubernetes/Istio/Argo cluster test: policies, alerts and scripts are verified against fixtures/fake `kubectl`; end-to-end behaviour is a design claim until run on kind/minikube (see D2 §"Lab validation plan").
- ML sandbox trained on **synthetic** data only.
