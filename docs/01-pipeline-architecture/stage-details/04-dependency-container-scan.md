# Stage 4 — Dependency & container scan (+ licence, SBOM)

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Attribute | Specification |
|---|---|
| Tool & version | Trivy 0.5x (fs + image) · Syft → CycloneDX 1.5 · ScanCode Toolkit/FOSSA |
| Execution | ∥ with stages 3, 5 |
| SLA (est. duration) | **7 min** |
| Inputs | Image built locally from stage 2 artefact; Gradle lockfiles. |
| Outputs | Scan report (SARIF), CycloneDX SBOM, licence report. |
| Regulatory mapping | RBI 5.1, 7.2; PCI 6.3 |

## Configuration & thresholds (blocking)
- Block **any Critical**; block High if CVSS ≥8.0 **and** fix available (`--ignore-unfixed`)
- Licence deny-list: GPL-2/3, AGPL, SSPL (LGPL → Legal review)
- Base image only from `registry.novapay.internal/base/*`, digest-pinned, rebuilt weekly
- `.trivyignore` entries need `expires:` and approver (linted by CI)

## Failure mode
Critical CVE / denied licence / unapproved base image → blocked.

## Remediation guidance
PR comment shows fixed version + dependency path (`gradle dependencyInsight`); Renovate PR auto-raised.

## Retry / skip / exception logic
Exception: 72 h remediation window with Security Lead approval, auto-expires. Retry: 1× (registry flake). Skip: **never**.

## Reference configuration
```bash
trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 $IMAGE
syft $IMAGE -o cyclonedx-json=sbom.cdx.json
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
