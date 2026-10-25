# Stage 3 — Static analysis (SAST)

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Attribute | Specification |
|---|---|
| Tool & version | SonarQube 10.x LTS with quality gate **NovaPay-Banking** (SonarCloud for the free-tier demo) |
| Execution | ∥ with stages 4, 5 |
| SLA (est. duration) | **6 min** |
| Inputs | Source + JaCoCo report. |
| Outputs | Quality-gate verdict, SARIF, auto-ticket on failure. |
| Regulatory mapping | RBI 5.1; PCI 6.2 |

## Configuration & thresholds (blocking)
- 0 Blocker/Critical; ≤2 High (new code)
- Technical-debt ratio on new code ≤5 %; no coverage drop >1 pt (trend gate)
- 100 % security hotspots reviewed
- Custom rules: PII in logs, MD5/SHA-1/ECB/DES, string-built SQL, hard-coded secrets, missing `@PreAuthorize` on payment endpoints

## Failure mode
Gate FAIL → pipeline blocked.

## Remediation guidance
Rule link + secure-coding snippet in PR; owner = author; SLA 24 h.

## Retry / skip / exception logic
Exception: CISO approval ≤24 h, auto-expires in 14 days. Retry: none. Skip: **never**.

## Reference configuration
```properties
sonar.qualitygate.wait=true
sonar.coverage.jacoco.xmlReportPaths=build/reports/jacoco/test/jacocoTestReport.xml
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
