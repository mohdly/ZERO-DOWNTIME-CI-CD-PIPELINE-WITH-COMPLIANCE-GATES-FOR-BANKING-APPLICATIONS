# Post-Mortem — INC-0420: Payments degradation after hotfix 1.14.3

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Field | Value |
|---|---|
| Date / time | Fri 17:07–17:15 IST (simulated) · Severity: SEV-1 (declared), SEV-3 at resolution |
| Authors | Mohammad Sinan Ali |
| MTTD / MTTR | 0 min (automated) / ≈5 min |
| Customer impact | ≈10% of traffic for ≈2–3 min; payment failures in window reconciled; no data loss |

## Summary
A hotfix that bypassed staging introduced a DB connection leak. The canary exhausted the PgBouncer pool, causing 12% HTTP 500 and 35% gateway timeouts. Automated Category A rollback aborted the canary within ~20 s; manual actions cleaned up residual DB sessions and reconciled in-flight payments.

## Timeline
See [incident-simulation.md](incident-simulation.md#2-decision-timeline-ist--playbook-executed).

## Root cause (5 whys)
1. 5xx because requests timed out → 2. threads blocked on connections → 3. pool exhausted by leaked connections → 4. new transaction code path not load tested → 5. **staging and perf gates were bypassed for a "critical" hotfix and the pipeline allowed it.**

## What went well / poorly / lucky
- ✅ Auto-rollback in <60 s; ✅ roles assigned quickly; ✅ funds reconciled.
- ❌ Bypass path existed; ❌ deploy at peak hour on Friday; ❌ residual DB sessions needed manual cleanup.
- 🍀 Only 10% canary weight, not 100%.

## Action items
| ID | Action | Owner | Priority | Due |
|---|---|---|---|---|
| AI-1 | Remove admin bypass; require `staging-verified` attestation at admission | SRE Lead | P0 | +7 d |
| AI-2 | Add pool-saturation metric to AnalysisTemplate + Stage-5 soak test | Platform | P0 | +14 d |
| AI-3 | Enforce blackout check in deploy job | Platform | P1 | +7 d |
| AI-4 | Auto-terminate idle-in-transaction sessions of aborted release user | DBA | P1 | +14 d |
| AI-5 | Hotfix canary profile 1%→10%→100% (5 min each) | SRE | P2 | +21 d |
| AI-6 | Quarterly game day replaying this scenario | SRE Lead | P2 | next quarter |

## Regulatory
Compliance decision logged: impact <30 min → internal incident report; RBI notification not triggered (confirm criteria with Compliance).
