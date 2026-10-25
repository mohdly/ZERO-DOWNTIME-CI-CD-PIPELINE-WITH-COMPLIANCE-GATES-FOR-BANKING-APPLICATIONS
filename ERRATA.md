# ERRATA — Deliberate Errors Found in the Project Brief

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

The brief (Section A8) says there are exactly three deliberate errors: one each in Part A, C and D.

| # | Part / Location | What the brief says | Correct | Confidence |
|---|---|---|---|---|
| 1 | **Part A**, §A.4.2 PCI-DSS v4.0 table, row 11.3 | 11.3 = "Penetration Testing" | In PCI-DSS v4.0, **11.3 is vulnerability scanning** (internal/external scans, ASV). **Penetration testing is 11.4.** | High |
| 2 | **Part C**, Case Study 3 (Cloudflare), "What Happened" | Dropped "approximately **50%** of global HTTP traffic" | Cloudflare's post-mortem: CPU hit 100% on every core handling HTTP/S and **traffic dropped by 82% at its worst**. (The 27-minute duration is correct; the in-document note about "21 minutes" is a red herring — 27 is right.) | High |
| 3 | **Part D**, Day 6 | "Study **gh-ost trigger-based** replication approach" | **gh-ost is triggerless** — it tails the MySQL binary log. *pt-online-schema-change* is the trigger-based tool. Also: gh-ost is MySQL-only, and NovaPay runs **PostgreSQL 16**, so the right tool here is **pgroll** (see `docs/04-database-migration`). | High |

## Corrections applied in this repository
1. PCI mapping uses **11.3 → vulnerability scanning (DAST + dependency/container scans)** and **11.4 → penetration testing (periodic, outside the pipeline)**. See `docs/03-compliance-gates/`.
2. Cloudflare lesson cites **82% traffic loss / 27 minutes**.
3. Migration deliverable uses **pgroll + hand-rolled expand-contract**, not gh-ost.

## Additional observations (not counted among the three — verify before relying)
**Technical issues in the Appendix reference code (fixed in `pipeline/` and `docs/04`):**
- `V2.0` script runs `CREATE INDEX CONCURRENTLY` — this **cannot run inside a transaction**, and Flyway wraps PostgreSQL migrations in one by default. Needs `executeInTransaction=false`.
- `V2.1` backfill is one `DO $$` block = **one transaction**: batches never commit, locks/WAL accumulate, and `pg_sleep` throttles nothing useful. Use an external batch job (or a `PROCEDURE` with `COMMIT`). Also `LIMIT … FOR UPDATE SKIP LOCKED` without `ORDER BY` is non-deterministic, and keeping the encryption key in a session GUC is poor practice (use KMS/Vault client-side encryption).
- `aquasecurity/trivy-action@master` and an unqualified `sonarqube-quality-gate-action@v1` — **unpinned third-party action** contradicts the brief's own supply-chain rules; the real action is `SonarSource/sonarqube-quality-gate-action`. `container-scan` also scans an image no job has built.
- OPA example uses legacy Rego v0 syntax; OPA 1.x needs `import rego.v1`.
- ArgoCD manifest: `targetRevision: HEAD` + `automated` sync on **production** bypasses the dual-approval / SoD story. Production should sync from a pinned revision after approval.

**Internal inconsistencies:**
- Canary table (15 + 30 + 60 min, then 24 h bake) cannot coexist with the "<2 h commit-to-production" goal. Resolved in `docs/01` §Timing by defining a *standard-risk* accelerated profile and a *high-risk* full profile.
- Category A rollback "<60 s" but trigger is "5xx > 5% **for 60 s**" — detection alone consumes the budget. Resolved in `docs/06` with a 30 s window + 15 s evaluation.
- DORA "elite" lead time of "<1 hour" is the older (2018) threshold; the 2024 report's elite band is **<1 day**. Treat the brief's figure as a stretch target, not the benchmark.
- Repo name is `DOC5A-CICD-Pipeline-[Name]` in Part D but `Project1A-DevOps&CloudEngineer-[First]-[Last]` in Part F. **Confirm with your mentor**; Part F governs the transfer.
- Cross-case table maps YES Bank's monitoring stack to Deliverable 5 (environment promotion); observability is Deliverable **8**.
- "22 non-conformances" for YES Bank (Case Study 2) could not be verified from public sources.
- RBI "Section 4.2 / 4.3 …" numbers in §A.4.1 look illustrative; the 2023 Master Direction is organised by chapter/paragraph. Cite actual paragraph numbers from rbi.org.in in your TRC deck.

## Verification notes (sources checked 23 Oct 2026)
- **Cloudflare, 2 Jul 2019:** multiple independent reports quoting Cloudflare's own post-mortem confirm *27 minutes* and *"at its worst traffic dropped by 82%"*. Also note: the rules were deployed globally in one go (they ran in "simulate" mode, which is why the staged-rollout process was skipped), and recovery came from a **global kill** of the WAF managed rulesets — not from a rollback blocked by the deployment system, as the brief's root-cause bullet implies. NovaPay design response: config-as-code through the same pipeline, canary even for "log-only" rules, and a rollback path that does not depend on the primary deploy path.
- **DORA:** 2024 report bands — elite lead time **<1 day**, elite recovery **<1 hour**, elite change-failure ≈5 %. The brief's "<1 hour lead time" matches older reports.
- **PCI-DSS v4.0:** 11.3 = vulnerability scans, 11.4 = penetration testing.
- **Brief arithmetic:** "6–9 hours/day, 100–135 hours over 15 days" — 6 h × 15 = 90 h, so the lower bound is inconsistent (the three sessions add to 8–9 h/day).
- **Gate thresholds:** Part A §A.2.2 says "High = block if CVSS > 8.0" while the §A.4.3 table blocks "if CVSS ≥ 9.0". This repo uses **Critical = block; High with CVSS ≥ 8.0 and a fix available = block** (documented in stage 4).
