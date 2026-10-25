# Diagrams (Draw.io source + PNG exports)

> **AI Attribution:** Diagrams specified by the author's design and generated with Claude-assisted tooling on 23 Oct 2026 (Graphviz layout → PNG and editable diagrams.net XML). Reviewed by **Mohammad Sinan Ali**.

| # | Diagram | PNG | Editable (.drawio) |
|---|---|---|---|
| 1 | 10-stage pipeline architecture with timings, parallel jobs, failure paths | [png](01-pipeline-architecture.png) | [drawio](01-pipeline-architecture.drawio) |
| 2 | Blue-green topology (Istio, shared data namespace) | [png](02-bluegreen-topology.png) | [drawio](02-bluegreen-topology.drawio) |
| 3 | Canary progression + statistical analysis | [png](03-canary-flow.png) | [drawio](03-canary-flow.drawio) |
| 4 | Compliance-gate orchestration | [png](04-compliance-gate-orchestration.png) | [drawio](04-compliance-gate-orchestration.drawio) |
| 5 | Expand-contract migration | [png](05-expand-contract.png) | [drawio](05-expand-contract.drawio) |
| 6 | 8-step rollback workflow | [png](06-rollback-workflow.png) | [drawio](06-rollback-workflow.drawio) |
| 7 | Environment promotion | [png](07-environment-promotion.png) | [drawio](07-environment-promotion.drawio) |
| 8 | Observability & alerting stack | [png](08-observability-stack.png) | [drawio](08-observability-stack.drawio) |

Regenerate: `cd src && for f in *.dot; do python3 dot2drawio.py $f ..; done` (needs Graphviz). Open `.drawio` files at https://app.diagrams.net to restyle; layout is auto-generated, so tidy before presenting.
