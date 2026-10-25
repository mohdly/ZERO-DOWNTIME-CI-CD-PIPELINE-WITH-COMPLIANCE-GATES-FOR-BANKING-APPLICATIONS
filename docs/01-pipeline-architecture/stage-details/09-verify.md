# Stage 9 — Post-deployment verification

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Attribute | Specification |
|---|---|
| Tool & version | `verify-fleet-version.sh` · `smoke-test.sh` · Prometheus synthetic probes (blackbox) |
| Execution | with stage 8 (each step) |
| SLA (est. duration) | **included in stage 8** |
| Inputs | Running pods, rollout state. |
| Outputs | Fleet inventory JSON, smoke results, SLO comparison. |
| Regulatory mapping | RBI 4.2, 6.3 |

## Configuration & thresholds (blocking)
- **All pods same image digest** and identical config hash (Knight Capital guard, [verification](../../02-deployment-strategies/knight-capital-verification.md))
- Smoke: login, balance, ₹1 sandbox transfer, UPI simulator pass
- Error rate and p99 ≤ pre-release baseline +5 %; probes ≥99.9 %

## Failure mode
Mismatch → kill-switch: flag off, Rollout abort, VirtualService → stable, SEV-1 page (≤30 s).

## Remediation guidance
Automatic; evidence kept in audit store.

## Retry / skip / exception logic
Retry: none. Skip: never.

## Reference configuration
```bash
ALLOW_MIXED=true ./pipeline/scripts/verify-fleet-version.sh novapay-prod payments-api $DIGEST   # during canary
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
