# Stage 7 — Policy & compliance gates

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Attribute | Specification |
|---|---|
| Tool & version | OPA 1.x + Conftest · Kyverno 1.12 (admission) · Checkov 3.x · SoD script (GitHub API) |
| Execution | serial |
| SLA (est. duration) | **3 min** |
| Inputs | Rendered Helm manifests, Terraform plan, PR approvals. |
| Outputs | Policy verdicts, SoD verdict, hash-chained audit record. |
| Regulatory mapping | RBI 4.2, 4.3, 5.4; PCI 2.2, 6.5 |

## Configuration & thresholds (blocking)
- No privileged containers; CPU/memory limits; non-root; no `:latest`; images by digest
- TLS 1.3 minimum on gateways; no plaintext secrets in env
- Checkov: 0 High; no `0.0.0.0/0`, encryption at rest on
- SoD: author ≠ approver ≠ deployer; 2 distinct approvers (Release Manager + SRE Lead)

## Failure mode
Any `deny` → deployment rejected (also at admission).

## Remediation guidance
Exact failing field + corrected YAML in PR; policy tests in `pipeline/policies/tests/`.

## Retry / skip / exception logic
Exceptions: per gate in [D3](../../03-compliance-gates/compliance-gates.md); SoD has **no** exception (break-glass logged, reviewed ≤24 h). Retry: none. Skip: never.

## Reference configuration
```bash
helm template novapay pipeline/helm/novapay -f values-production.yaml | conftest test - --policy pipeline/policies
opa test --v1-compatible pipeline/policies -v   # 13 policy unit tests
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
