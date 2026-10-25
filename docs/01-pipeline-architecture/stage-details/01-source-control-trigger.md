# Stage 1 — Source control & trigger

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

| Attribute | Specification |
|---|---|
| Tool & version | GitHub Enterprise Cloud rulesets; gitleaks 8.x; `git verify-commit` with org-managed SSH/GPG keys |
| Execution | serial (entry) |
| SLA (est. duration) | **2 min** |
| Inputs | PR opened / push to `main`, `release/*`, `hotfix/*` / tag. Path filters for monorepo: `services/<svc>/**`. |
| Outputs | Verified commit SHA, PR metadata, change-class label (standard / high-risk / hotfix). |
| Regulatory mapping | RBI 4.2 (change mgmt), 4.3 (SoD); PCI 6.5 |

## Configuration & thresholds (blocking)
- Require PR, linear history, no force-push, **no admin bypass**
- ≥1 approval (≥2 + CODEOWNER for `services/payments/**`, `db/**` needs DBA)
- All commits signed (SSH/GPG); required status checks = stages 2-5
- Branch lifetime <24 h (trunk-based); `main` always releasable

## Failure mode
Unsigned commit, <required approvals, secret detected, direct push → **merge blocked**.

## Remediation guidance
Rebase & re-sign (`git commit -S --amend`); rotate any leaked secret and record in audit log.

## Retry / skip / exception logic
Retry: none. Skip: **never**.

## Reference configuration
```yaml
# .github/rulesets/main.json (excerpt)
required_signatures: true
required_pull_request_reviews: { required_approving_review_count: 1, require_code_owner_review: true }
bypass_actors: []
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
