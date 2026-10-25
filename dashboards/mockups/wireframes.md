# Dashboard wireframes (replace/export from Figma or Draw.io into this folder)

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

```
ENGINEERING — real-time ops
+----------------------+----------------------+----------------------+
| Active rollouts      | 5xx % by version     | p99 latency by ver.  |
| svc/ver/weight/state | (stable vs canary)   | (stable vs canary)   |
+----------------------+----------------------+----------------------+
| DB pool waiting      | Queue depth (RMQ)    | Alerts firing (A/B/C)|
+----------------------+----------------------+----------------------+
| Rollback bot log     | Pipeline stage heat  | Synthetic probes     |
+----------------------+----------------------+----------------------+

MANAGEMENT — weekly / monthly
| Deploy freq (trend) | Lead time p50/p90 | Change fail % | MTTR |
| Availability vs 99.999% SLO + error budget | Top 5 gate blockers   |

REGULATORY — audit-ready
| Gate pass/fail per release | Exceptions register (expiry) | RBI/PCI coverage matrix |
| SoD evidence per prod deploy | Audit hash-chain status    | Incidents + regulator notices |
```
