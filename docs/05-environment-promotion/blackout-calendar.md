# Case Study 4 (SBI YONO) — Deployment Blackout Calendar & Capacity Triggers

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

Enforced by `pipeline/scripts/blackout-check.sh` (reads `pipeline/scripts/blackout-calendar.yaml`) as the first step of every production deploy job.

| Window | Rule | Who can override |
|---|---|---|
| Salary days: **1st, 7th, 15th** (06:00–24:00 IST) | no prod deploys; hotfix-only with Emergency Change | CTO + SRE Lead |
| Month-end **28th–31st** | freeze for non-critical; no DB migrations | CTO |
| Festivals (Diwali ±3 d, Eid, Christmas, Holi ±1 d) | freeze 48 h before to 24 h after (calendar maintained yearly) | CTO |
| RBI/NPCI settlement windows (daily cut-offs; RTGS/NEFT peak) | no deploys ±30 min of cut-offs | SRE Lead |
| Regulatory filing deadlines (returns, quarter-end) | freeze 72 h before | Head of Compliance |
| Marketing campaigns / UPI promotions (registered in calendar by Marketing ≥7 d ahead) | freeze from campaign start to +12 h | VP Eng |
| Daily peak (10:00–12:00, 17:00–20:00 IST) | no standard deploys; hotfix canary only | SRE Lead |
| Fridays after 15:00 IST | std-risk only; no contract migrations (Friday 5 PM lesson) | SRE Lead |

## Pre-high-traffic performance requirement
Any deployment **within 48 h before** a high-traffic window must additionally pass: k6 load test at **5× normal** (salary-day profile 3–5× per case study) for 30 min on pre-prod; p99 <300 ms; error <0.1%; HPA scales without saturation; DB connection pool headroom ≥30%. Result attached to the change record.

## Auto-scaling triggers (HPA/KEDA in Helm `values.yaml`)
| Signal | Scale-out threshold | Notes |
|---|---|---|
| CPU | >70% avg | min replicas 6 prod; max 60 |
| RabbitMQ queue depth (KEDA) | >1,000 messages | per consumer group |
| p99 latency (Prometheus adapter) | >300 ms for 2 min | scale before saturation |
| Scale-in | stabilisation 10 min | avoid flapping at peak |
Pre-scaling: scheduled scale-up 30 min before known peaks (salary day, festival) from the same calendar.
