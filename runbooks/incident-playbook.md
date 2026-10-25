# NovaPay Incident Response Playbook

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

## 1. Severity classification
| Sev | Definition | Respond within | Escalation | Updates |
|---|---|---|---|---|
| SEV-1 | Complete outage, payments failing broadly, or data-integrity risk | <5 min | CTO + CISO + VP Eng (+Head of Compliance) | every 30 min |
| SEV-2 | Major degradation affecting >10% of users | <15 min | VP Eng + SRE Lead | hourly |
| SEV-3 | Minor degradation, workaround exists | <1 h | SRE on-call + Tech Lead | on change |
| SEV-4 | Cosmetic, no user impact | next business day | assigned engineer | – |
Security incident or suspected data breach → SEV-1 and **CERT-In (6 h) / RBI** reporting timelines apply — Compliance owns the call.

## 2. 7-step workflow
1. **Detect & declare** — alert/customer report; Incident Commander (IC) = on-call SRE; open #inc-<id> channel + incident doc; clock starts T+0.
2. **Triage & classify** — severity, scope, latest change (check Argo/Deploy history); recent release? → likely rollback.
3. **Communicate** — internal ack ≤2 min; status page ≤10 min if customer-visible; assign roles: IC, Ops lead, Comms lead, Scribe.
4. **Mitigate** — rollback/flag-off/failover/scale (prefer reversible actions); never debug in place while customers are failing.
5. **Verify recovery** — smoke + synthetic + metrics at baseline for 15 min; reconcile in-flight payments.
6. **Resolve & notify** — resolution message with impact summary; RBI/NPCI notification if criteria met (≥30 min customer-impacting outage or payment-system disruption — confirm thresholds with Compliance).
7. **Post-mortem** — blameless, within 5 business days; action items with owners/dates tracked to closure.

## 3. Communication templates
**Initial (internal Slack):** `[SEV-<n>] <service> – <symptom>. Started <time IST>. Impact: <who/what>. IC: <name>. Next update: <time>.`
**Initial (status page):** `We are investigating issues with <feature>. Some customers may be unable to <action>. Money in transit is safe and will be reconciled. Next update by <time>.`
**Update (every 30 min SEV-1 / hourly SEV-2):** `Update <hh:mm>: <what we know>. <mitigation in progress>. Next update <time>.`
**Resolution:** `Resolved <time>. Cause: <plain-language>. Duration: <min>. Impact: <txn count/%>. Failed transactions have been <reversed/reconciled>. Post-mortem to follow within 5 business days.`
**Regulatory (draft for Compliance):** `Incident <id>, <time>–<time>, systems affected, customer impact, root-cause summary, remedial actions, contact.`
**Executive (SEV-1):** 3 lines: impact, ETA, decision needed.


### 3a. Communication matrix — every stage × every severity
| Stage | SEV-1 (outage / data risk) | SEV-2 (>10 % users) | SEV-3 (minor) | SEV-4 |
|---|---|---|---|---|
| **Initial ack — internal** | Slack #inc + page CTO/CISO/VP Eng ≤2 min | Slack #inc, VP Eng + SRE Lead ≤5 min | Slack #release-watch ≤30 min | ticket |
| **Initial ack — external** | status page ≤10 min; in-app banner if payments affected | status page ≤30 min if customer-visible | none | none |
| **Updates** | every **30 min** (exec 3-liner every 60 min) | every **60 min** | on state change | – |
| **Resolution** | status page + email/SMS to impacted customers; exec summary | status page + support macro | Slack note | ticket close |
| **Regulatory** | Compliance drafts RBI/NPCI/CERT-In notice (CERT-In ≤6 h for cyber incidents); owner: Head of Compliance | assess within 1 h; notify if payments disrupted ≥30 min (confirm threshold) | log decision only | – |
| **Post-mortem** | mandatory ≤5 business days, reviewed at TRC | mandatory ≤5 days | optional (5-whys in ticket) | – |

**SEV-2 example (status page):** `We are seeing slower-than-usual <feature> for some customers. Transactions are processing; some may take longer. Next update by <time>.`
**SEV-3 example (Slack):** `[SEV-3] <service> p99 elevated since <time>; workaround: <x>. Owner: <name>. Next update on change.`

## 4. Post-mortem template
```
Title / ID / Severity / Date / Authors
Summary (3 lines) · Customer & business impact (numbers) · Detection (how/when; MTTD)
Timeline (IST, T+offsets): detect → triage → comms → mitigation → recovery → resolution
Root cause (5 whys) · Contributing factors · What went well / poorly / lucky
Pipeline/gate analysis: which gate should have caught this? bypassed? missing?
Action items: [ID] description · owner · priority · due · status
Regulatory notifications made (who/when)
```

## 5. Rollback quick reference
`kubectl argo rollouts abort <svc> -n novapay-prod` · `./pipeline/scripts/rollback.sh <svc>` · feature-flag kill: `flagctl off <flag>` · status page: `statuspage update`.
