# Case Study 1 — Deployment verification that would have stopped Knight Capital

> **AI Attribution:** Drafted with Claude (Anthropic) on 23 Oct 2026 as an AI-accelerated first draft. Reviewed, edited, validated (linters, unit tests, source checks) and approved by **Mohammad Sinan Ali**.

**Failure recap (1 Aug 2012):** 7 of 8 servers got the new code; the 8th kept legacy code whose repurposed flag triggered the old "Power Peg" logic; ~$440M lost in ~45 minutes. No verification, no kill switch.

## Verification step (`pipeline/scripts/verify-fleet-version.sh`)
| Req. | Control | Implementation |
|---|---|---|
| (d) | **Pre-deployment inventory** of running versions vs target | Query every pod's image **digest** (`kubectl get pods -o jsonpath`) and `/actuator/info` build SHA; write inventory JSON to audit store; abort if any pod is neither old-known nor target |
| (a) | **All pods run the same image hash** | After each canary/switch step: set of distinct digests among *target-labelled* pods must equal exactly {target digest}; count must equal desired replicas |
| (b) | **Config consistency** across the fleet | Compare SHA-256 of rendered ConfigMap + effective feature-flag snapshot returned by `/actuator/configprops` hash on every pod |
| (c) | **Automated kill-switch** on mismatch | On any mismatch: (1) set feature flag `trading.kill = on` / payments ramp = 0, (2) `kubectl argo rollouts abort`, (3) VirtualService → stable, (4) page SEV-1. Target ≤30 s, no human in loop |

Plus structural preventions: no manual deploy credentials exist (SSH disabled, deploy only via ArgoCD service account); dead code removed via SAST "unused flag/dead code" rule; repurposing a flag name requires a new flag (Sonar custom rule + PR template item).

Why canary alone would have caught it: the first 2% step runs analysis against a *single* known version; a pod serving legacy behaviour fails the digest check before any money-moving traffic reaches it.
