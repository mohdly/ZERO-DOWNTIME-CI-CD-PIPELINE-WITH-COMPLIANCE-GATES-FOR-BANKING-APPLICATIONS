# Stage 2 — Build & unit test

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

| Attribute | Specification |
|---|---|
| Tool & version | Gradle 8.x · JDK 21 (Temurin) · Docker BuildKit · JaCoCo 0.8.x |
| Execution | serial |
| SLA (est. duration) | **8 min (≈4 with cache)** |
| Inputs | Verified SHA from stage 1. |
| Outputs | Versioned jar + OCI image layers, JaCoCo XML, version `MAJOR.MINOR.PATCH+<sha7>.<UTC>.run<id>`. |
| Regulatory mapping | PCI 6.2 (secure development); RBI 4.2 |

## Configuration & thresholds (blocking)
- `--dependency-verification strict`; lockfiles enforced (drift fails)
- Unit tests 100% pass; coverage line ≥80 %, branch ≥70 %
- Multi-stage Dockerfile → distroless, non-root UID 10001; BuildKit registry cache
- Release matrix: linux/amd64 + arm64; images never tagged `latest`

## Failure mode
Test failure, coverage below threshold, lockfile or checksum drift.

## Remediation guidance
PR comment with failing report + JaCoCo diff; add tests or fix lockfile.

## Retry / skip / exception logic
Retry: 1× for infrastructure errors only. Skip: never.

## Reference configuration
```bash
./gradlew build test jacocoTestReport --dependency-verification strict
./pipeline/scripts/check-coverage.sh --min-line 80 --min-branch 70
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
