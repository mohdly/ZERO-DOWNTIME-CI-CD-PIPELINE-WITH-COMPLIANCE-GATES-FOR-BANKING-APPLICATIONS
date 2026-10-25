# Stage 6 — Dynamic analysis (DAST) + performance

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Attribute | Specification |
|---|---|
| Tool & version | OWASP ZAP 2.15 API scan (OpenAPI-driven, authenticated with scoped Vault test client, 1 h TTL) · k6 0.5x |
| Execution | ZAP ∥ k6 (matrix) |
| SLA (est. duration) | **15 min** |
| Inputs | Image deployed to **staging**; `openapi.yaml`. |
| Outputs | ZAP report, k6 summary, **`staging-verified` Cosign attestation** on success. |
| Regulatory mapping | RBI 5.1; PCI 6.4, 11.3 (vuln scanning) |

## Configuration & thresholds (blocking)
- 0 Critical/High (OWASP Top 10); Medium ≤5
- k6 at 2× expected load: p99 <500 ms, errors <0.1 %
- False positives only via `.zap/rules.tsv` with ticket + expiry
- Active scan **only** on staging

## Failure mode
Finding above threshold or perf regression → blocked.

## Remediation guidance
Request/response evidence + OWASP cheat-sheet link in PR.

## Retry / skip / exception logic
Exception: risk-acceptance form + TRC, ≤30 d. Retry: 1× on environment flake. Skip: **never** (hotfix included).

## Reference configuration
```yaml
- uses: zaproxy/action-api-scan@<sha>
  with: { format: openapi, target: https://staging.novapay.example/openapi.yaml, fail_action: true }
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
