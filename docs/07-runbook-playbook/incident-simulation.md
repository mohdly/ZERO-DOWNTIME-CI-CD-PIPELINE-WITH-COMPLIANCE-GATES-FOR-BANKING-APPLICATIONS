# Level 5 — "The Incident": Friday 5:07 PM IST Simulation

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

**Scenario:** A developer pushed a "critical hotfix" that bypassed staging. Canary has run 8 min (**hotfix profile 1% → 10% → 100%, 5 min per step**, so it is currently inside the 10% step). Alerts fire together: HTTP 500 = 12% (threshold 5%, CRITICAL); PostgreSQL connection-pool exhaustion on primary (HIGH); downstream payment-gateway timeout 35% (CRITICAL).

## 1. Alert → pipeline mapping
| Alert | Category | Should have been caught by | Why not |
|---|---|---|---|
| 5xx 12% | A1 | Canary analysis (auto-rollback) **and** Stage 5/6 in staging | hotfix skipped staging → no integration/perf/DAST |
| Pool exhaustion | A5 | Stage 5 integration with pool-soak test; Stage 6 perf @2× load | same; change introduced a connection leak (see RCA) |
| Gateway timeouts 35% | A7 | Perf test + contract test vs gateway simulator | same; blocked threads cascaded |
| (Context) deploy at 17:07 Friday | – | **Blackout check** (daily peak 17:00–20:00; Friday ≥15:00) | hotfix path skipped `blackout-check.sh` |

## 2. Decision timeline (IST) — playbook executed
| Time | T+ | Actor | Decision / action | Rationale |
|---|---|---|---|---|
| 17:07:00 | T+0 | Prometheus | A1, A5, A7 alerts fire (3 critical in same window) | – |
| 17:07:20 | T+20s | rollback-bot | Correlates alerts to rollout `payments-api r:hotfix-1.14.3`; freezes pipeline; **aborts rollout**, canary weight 10→0 | Cat A automation, no human |
| 17:07:30 | T+30s | On-call SRE (IC) | Acks page; **classifies SEV-1** (payments failing, peak hour, >10% users plausible) | A7 35% gateway timeouts on payment path |
| 17:07:50 | T+50s | IC | Confirms weights 0% on canary in Argo/Istio; checks pool/gateway recovery | verify bot action, don't assume |
| 17:08:30 | T+1m30 | IC | Opens #inc-0420, assigns Ops lead, Comms lead, Scribe | roles |
| 17:09 | T+2m | Comms | **Internal Slack ack** sent; CTO + CISO + VP Eng paged (SEV-1) | playbook |
| 17:10 | T+3m | Ops | Pool still saturated (stuck connections from canary pods) → **restart PgBouncer client pools / terminate idle-in-transaction sessions from canary app user**; scale stable RS +30% | connection leak leaves server-side sessions |
| 17:12 | T+5m | IC | Smoke + synthetic ₹1 payments pass; 5xx 0.04%; gateway timeouts 2% falling | verify recovery |
| 17:12 | T+5m | Comms | **Status page** "degraded payments, investigating; funds safe" | customer visible (~5 min) |
| 17:17 | T+10m | Ops | Reconciliation job for in-flight payments (gateway timeouts) started; list of failed txns exported | RBI/customer-impact |
| 17:22 | T+15m | IC | Metrics at baseline 10 min; downgrade to SEV-3 monitoring; update #1 | stability |
| 17:37 | T+30m | Comms | **Resolution** posted; Compliance assesses RBI/NPCI notification (total impact ≈5 min → likely below 30-min threshold; log decision) | Compliance owns |
| next biz day | – | Team | Post-mortem scheduled ≤5 days | |
**Estimated customer impact window:** T+0 → T+≈2–3 min on 10% of traffic (rollback bot) → well within a 15-min MTTR (**actual MTTR ≈ 5 min vs. 4.5 h today**).

*Degraded-bot variant (practice):* if rollback-bot is down, the IC runs `./pipeline/scripts/rollback.sh payments-api` at T+1 min (independent path) — recovery by T+3 min.

## 3. Root cause
The hotfix changed the DB access layer (new transaction boundary + pool configuration) and **leaked connections under load**: pool exhausted → threads blocked → requests timed out → gateway calls exceeded timeouts → 5xx. Staging would have shown this within a 15-min k6 run at 2× load.
**Bypassed gates:** Stage 5 (integration/pool soak), Stage 6 (DAST + perf), staging promotion itself, and `blackout-check` (Friday 17:07 = peak).

## 4. Did the design prevent this? What was missing?
- **Prevented in design:** hotfix is *expedited, not bypassed* — the pipeline architecture makes staging mandatory. **The incident occurred because an exception path existed** (a bypass in the hotfix workflow / admin override on branch protection).
- **Missing gate(s) → fixes:**
  1. Remove bypass: GitHub ruleset has *no* admin bypass; CD job verifies the image digest has a staging pass attestation (Cosign attestation `staging-verified`) — Kyverno rejects images without it, **including hotfixes**.
  2. Add **DB pool-saturation** metric to the canary analysis and a soak test in Stage 5 (HikariCP pending > 0 for 60 s fails).
  3. Enforce blackout check inside the *deploy* job (not just the pipeline start), covering hotfix with Emergency Change approval.
  4. Pre-prod "connection budget" policy (Conftest): pool size × replicas ≤ 60% of `max_connections`.
  5. Cap canary blast radius for hotfix: 1% for 10 min before 10%.
