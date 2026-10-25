# Per-stage specifications (Deliverable 1)

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

Each file defines: **tool & version · inputs/outputs · configuration & thresholds · failure mode & remediation · retry/skip logic · SLA · regulatory mapping**. Timing totals and parallelism: [architecture.md](../architecture.md).

| # | Stage | Runs | SLA | File |
|---|---|---|---|---|
| 1 | Source control & trigger | serial (entry) | 2 min | [01-source-control-trigger.md](01-source-control-trigger.md) |
| 2 | Build & unit test | serial | 8 min (≈4 with cache) | [02-build-unit-test.md](02-build-unit-test.md) |
| 3 | Static analysis (SAST) | ∥ with stages 4, 5 | 6 min | [03-sast.md](03-sast.md) |
| 4 | Dependency & container scan (+ licence, SBOM) | ∥ with stages 3, 5 | 7 min | [04-dependency-container-scan.md](04-dependency-container-scan.md) |
| 4b | Sign & attest (supply-chain provenance) | after stage 4; ∥ with 3, 5 | 2 min | [04b-sign-attest.md](04b-sign-attest.md) |
| 5 | Integration & contract testing | ∥ with stages 3, 4 | 15 min | [05-integration-contract.md](05-integration-contract.md) |
| 6 | Dynamic analysis (DAST) + performance | ZAP ∥ k6 (matrix) | 15 min | [06-dast-performance.md](06-dast-performance.md) |
| 7 | Policy & compliance gates | serial | 3 min | [07-policy-compliance.md](07-policy-compliance.md) |
| 8 | Deployment (progressive delivery) | serial | ≈35 min std (+5 min to 100 %) | [08-deploy-progressive.md](08-deploy-progressive.md) |
| 9 | Post-deployment verification | with stage 8 (each step) | included in stage 8 | [09-verify.md](09-verify.md) |
