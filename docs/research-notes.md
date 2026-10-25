# Research notes (Day 1–2 foundation)

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

Learning resources identified per deliverable (≥3 each; all free). "Used for" states what I took from the source and where it shows up in the design.

| Deliverable | Resource | Used for |
|---|---|---|
| **D1 Pipeline architecture** | GitHub Actions docs — reusable workflows & OIDC (docs.github.com/en/actions) | `reusable-sast.yml`, keyless Cosign, least-privilege `permissions:` |
| | OWASP DevSecOps Guideline (owasp.org/www-project-devsecops-guideline) | stage ordering: fast checks first, scans in parallel |
| | SLSA specification v1.0 (slsa.dev) · Sigstore docs (docs.sigstore.dev) | provenance + signing stage 4b |
| | DORA State of DevOps (dora.dev) | metrics, lead-time benchmark critique |
| **D2 Deployment strategies** | Argo Rollouts docs — canary + Istio traffic routing (argo-rollouts.readthedocs.io) | `rollout.yaml`, AnalysisTemplate |
| | Istio traffic-management docs (istio.io/latest/docs/concepts/traffic-management) | VirtualService atomic switch, retries/timeouts |
| | Cloudflare post-mortem, 12 Jul 2019 (blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019) | independent rollback, config-as-code, CPU circuit breaker |
| | SEC order on Knight Capital (SEC Release 34-70694, Oct 2013) | fleet-verification requirements |
| **D3 Compliance gates** | PCI-DSS v4.0 (pcisecuritystandards.org document library) | req. 6.2–6.5, 10.2, 11.3/11.4 mapping — **corrected 11.3/11.4** |
| | RBI Master Direction on IT Governance, Risk, Controls & Assurance Practices, 2023 (rbi.org.in) | change mgmt, SoD, audit-trail controls |
| | OPA docs + Rego policy testing (openpolicyagent.org/docs) · Kyverno docs (kyverno.io/docs) | `pipeline/policies/` + 13 policy unit tests |
| **D4 DB migration** | pgroll (github.com/xataio/pgroll) | online schema change on PostgreSQL |
| | PostgreSQL docs: `CREATE INDEX CONCURRENTLY`, explicit locking, `lock_timeout` | lock-safe expand phase |
| | Flyway docs — `executeInTransaction` | fixes appendix V2.0 script problem |
| | gh-ost README (github.com/github/gh-ost) | confirmed **triggerless** binlog design → ERRATA #3 |
| **D5 Environment promotion** | HashiCorp Vault docs — dynamic secrets & rotation (developer.hashicorp.com/vault) | 90-day / 30-day rotation policy |
| | ArgoCD docs — drift detection & sync policies (argo-cd.readthedocs.io) | 3-min drift check, no auto-sync to prod |
| | Google SRE Book — Release engineering ch. 8 (sre.google/sre-book) | "same artefact, different config" |
| **D6 Rollback** | Prometheus alerting rules + promtool unit testing (prometheus.io/docs) | `rollback-alerts.test.yaml` (5 passing tests) |
| | Google SRE Workbook — alerting on SLOs, burn-rate (sre.google/workbook) | Category B burn-rate triggers |
| | Kubernetes probes docs (kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes) | A2 trigger, startup probe |
| **D7 Runbook & playbook** | Google SRE Book — Managing Incidents; Postmortem Culture (sre.google/sre-book) | roles (IC/Ops/Comms/Scribe), blameless template |
| | PagerDuty Incident Response docs (response.pagerduty.com) | severity tiers, comms cadence |
| | CERT-In Directions of 28 Apr 2022 (cert-in.org.in) | 6-hour incident reporting note |
| **D8 Observability** | Sloth (sloth.dev) / Pyrra (pyrra.dev) | SLO generation, 99.999 % objective |
| | Grafana dashboard JSON model (grafana.com/docs/grafana/latest/dashboards) | 3 dashboards generated from code |
| | NPCI UPI product & statistics pages (npci.org.in) | TD% concept for UPI detection rule |

## Key decisions made during research
1. **10 stages, not 8** — SBOM/signing and post-deploy verification are separate auditable controls.
2. **Canary profiles** — the brief's 15/30/60-min canary + 24 h bake contradicts the <2 h target; resolved with *standard* and *high-risk* profiles (D1 §3).
3. **Tool substitution** — gh-ost is MySQL-only → **pgroll** for PostgreSQL 16.
4. **Rollback budget** — "5xx >5 % for 60 s" cannot meet a <60 s rollback; detection window tightened to 30 s.
5. **Hotfix = expedited, never bypassed** — enforced cryptographically (staging-verified attestation checked at admission).
