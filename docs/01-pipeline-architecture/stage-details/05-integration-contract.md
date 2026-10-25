# Stage 5 — Integration & contract testing

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

| Attribute | Specification |
|---|---|
| Tool & version | Testcontainers · Pact (broker `can-i-deploy`) · ephemeral namespace `pr-<n>` (TTL 2 h) · k6 smoke baseline |
| Execution | ∥ with stages 3, 4 |
| SLA (est. duration) | **15 min** |
| Inputs | Built image + migration scripts. |
| Outputs | Test reports, Pact verification, performance baseline JSON. |
| Regulatory mapping | RBI 4.2; PCI 6.5 |

## Configuration & thresholds (blocking)
- All integration tests + provider verification pass
- `can-i-deploy --to-environment staging` = OK
- Next DB migration applied to anonymised snapshot while **both** app N-1 and N run (compatibility matrix, [D4](../../04-database-migration/database-migration.md))
- Pool-soak test: HikariCP `pending` = 0 for 60 s; p99 regression ≤10 % vs baseline

## Failure mode
Any failure → blocked; contract break → consumer owners notified.

## Remediation guidance
Failing Pact interaction diff in PR; quarantine flaky tests only with ticket (expires in 7 days).

## Retry / skip / exception logic
Retry: 1× for infra. Skip: **never**.

## Reference configuration
```bash
./gradlew integrationTest pactVerify
./pipeline/scripts/migration-compat-test.sh
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
