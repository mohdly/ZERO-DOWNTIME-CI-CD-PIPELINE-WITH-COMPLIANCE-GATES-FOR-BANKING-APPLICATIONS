# Sandbox extensions (Innovation Pioneer) — ML pipeline intelligence, compliance drift, chaos, DX metrics

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

Four Sandbox-mode topics from Part B §B3.3 are designed here; **ML Pipeline Intelligence is implemented and unit-tested** (code in `pipeline/scripts/ml/`, tests in `pipeline/scripts/tests/`).

## 1. ML pipeline intelligence (implemented)
### 1a. Anomaly-based canary analysis — `pipeline/scripts/ml/anomaly_canary.py`
- **Problem:** Welch/chi-squared tests judge one metric at a time. A release that nudges p99 +35 %, CPU +30 % and DB-pool waiters ×4 can stay under every single hard threshold yet be clearly unhealthy (a Category C "slow burn").
- **Method:** IsolationForest (200 trees, contamination 2 %) trained on the last 12 h of the **stable fleet's** per-minute vector (error ratio, p99, CPU, memory, PgBouncer waiters); canary minutes scored against it. `anomaly_ratio ≥0.5 → rollback-advised`, `≥0.2 → extend`, else promote.
- **Safety design:** advisory only — it can *extend or advise*, never auto-promote, and never overrides Category A/B rules or the statistical gate. Model + training window are logged to the audit record (explainability for the RBI auditor; fixed random seed → reproducible verdicts).
- **Result on synthetic data (seeded, see tests):** healthy canary → 0 % anomalous windows (*promote*); slow-burn canary → 100 % (*rollback-advised*) while no single metric breached its A/B threshold.
- **Limitation (honest):** trained and tested on *synthetic* data. Before production use it needs back-testing on real NovaPay history, seasonality handling (salary days) and a false-positive budget.

### 1b. Predictive test selection — `pipeline/scripts/ml/predictive_test_selection.py`
- LogisticRegression on (path-overlap, historic fail rate, recency, flaky flag) → ranks tests by failure probability so the **risky tests run first**, shortening developer feedback (target <10 min).
- On the seeded synthetic set, the top 20 % of tests ranked by the model contain **≈67 % of failures** (random order ≈20 %). **Rule: ordering only — the full suite still runs before staging.**

## 2. Compliance drift detection (design)
Deployment-time checks are not enough: a running pod can become non-compliant later (new CVE, policy change, manual `kubectl edit`).
- Kyverno **background scan** + PolicyReports exported to Prometheus (`kyverno_policy_results_total{rule_result="fail"}`); alert if any production workload fails a policy for >10 min.
- Nightly **Trivy operator** rescan of running image digests against fresh CVE data → Category C warning ("retroactive compliance failure") with 72 h remediation SLA.
- ArgoCD drift check every 3 min; manual-change events written to the audit store.
- Dashboard: Regulatory → "control coverage" panel shows live pass/fail per control, not just release-time snapshots.

## 3. Chaos engineering (design)
Litmus experiments run in **pre-prod** as a scheduled pipeline (weekly) and before any high-risk release: `pod-delete` on payments-api (expect zero failed payments, recovery <30 s), `pod-network-latency` to the payment gateway simulator (+500 ms → circuit breaker opens, A7 alert fires), `pod-cpu-hog` at 90 % (HPA scales, B4 alert), PgBouncer `network-loss` 30 s (A5 alert, rollback-bot dry-run). Pass criteria are the rollback thresholds in [D6](../06-rollback-specification/rollback-specification.md); results go to the evidence store. This also meets the YES-Bank lesson that DR must be *tested*.

## 4. Developer-experience metrics (design)
Track alongside DORA: PR→green time (p50/p90), queue time per job, re-run rate, flaky-test rate, "gate friction" = % of PRs blocked by each gate on first run, time-to-fix after a gate failure, and a quarterly 3-question developer survey (clarity of failure message, trust in gates, self-service ability). Targets: first-run gate failure rate <15 %, fix time <30 min, satisfaction ≥4/5 — addressing the Dev-Team persona's friction concern.
