# Case Study 3 (Cloudflare) — Config-Change Pipeline for WAF / Security Rules

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

**Fact base (verified):** 2 July 2019, a WAF Managed Rule with a backtracking regex was deployed globally in one step; CPU hit 100% on every core handling HTTP/S; **traffic fell by up to 82%**; outage lasted **27 minutes**; global WAF kill took effect 14:07 UTC, recovery 14:09. (Brief says "~50%" — see ERRATA #2.)

## Pipeline for NovaPay WAF/security rule changes
Rules, feature flags, routing and rate-limit config are **code**: they live in Git (`policies/waf/`) and pass the same pipeline.
1. **PR + review** (security + SRE), signed commit, lint: regex linter rejects unbounded backtracking constructs (`(.*)*`, nested quantifiers), requires RE2-compatible syntax (linear-time engine) — the root-cause fix.
2. **Unit tests**: rule matches a malicious corpus and does **not** match a replay of 24 h sanitised production traffic (false-positive gate).
3. **Performance baseline gate**: replay traffic in an isolated WAF instance; fail if CPU >+10%, memory >+10%, p99 added latency >+5 ms vs baseline.
4. **Staged rollout (canary by scope):** shadow/log-only mode in 1 AZ → 5% of edge pods in one region → 25% → 100%; each step ≥10 min with Prometheus analysis (CPU, 5xx, latency, WAF block-rate anomaly).
5. **Circuit breaker:** if node CPU >80% for 30 s the WAF module **fails open for that rule set** (rule disabled via local config, not dependent on network/control plane) and alerts; limits blast radius in seconds. Per-rule CPU budget enforced (e.g. 200 ms/request cap, as with `rctl`/cgroup limits).
6. **Independent rollback path:** a signed "last-known-good" rule bundle is cached on every node; a node-local agent reverts to it when the breaker trips or a kill signal arrives via an out-of-band channel (separate control plane/queue, own credentials). Break-glass CLI tested monthly (game day), so a CPU-starved fleet cannot lock out recovery.
7. **Audit**: change record, approvals, rollout stages and verification written to the immutable store.
