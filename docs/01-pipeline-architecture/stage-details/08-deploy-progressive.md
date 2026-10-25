# Stage 8 — Deployment (progressive delivery)

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Attribute | Specification |
|---|---|
| Tool & version | ArgoCD 2.x (GitOps) · Argo Rollouts 1.7 · Istio 1.2x · Helm 3.x |
| Execution | serial |
| SLA (est. duration) | **≈35 min std (+5 min to 100 %)** |
| Inputs | Approved image digest, change class, dual approval. |
| Outputs | New ReplicaSet, VirtualService weights, analysis runs, deploy audit record. |
| Regulatory mapping | RBI 4.2, 6.3; PCI 6.5 |

## Configuration & thresholds (blocking)
- Standard: 2 % (10 min) → 10 % (10) → 50 % (15) → 100 %; high-risk: 1-2 % (15) → 5-10 % (30) → 25-50 % (60) → 100 % + 24 h bake
- Analysis every 60 s: Welch t-test (latency), chi-squared (errors), ≥5,000 requests per phase
- Blackout check inside the deploy job; GitHub Environment approval (prevent self-review)

## Failure mode
Analysis breach → Argo abort + weight 0 (<60 s, Category A) — see [D6](../../06-rollback-specification/rollback-specification.md).

## Remediation guidance
Automatic. Humans investigate after revert.

## Retry / skip / exception logic
Retry: none (rollback instead). Skip: never.

## Reference configuration
```yaml
steps: [ {setWeight: 2}, {pause: {duration: 10m}}, {setWeight: 10}, {pause: {duration: 10m}}, {setWeight: 50}, {pause: {duration: 15m}}, {setWeight: 100} ]
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
