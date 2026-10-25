# Screenshots / tool-configuration evidence

> **AI Attribution:** Terminal captures below were rendered from the real command outputs in `../test-results/` (Claude-assisted tooling). 

| File | Shows |
|---|---|
| 01-validate-all.png | `validate.sh` summary |
| 02-opa-policy-tests.png | 13 Rego unit tests passing |
| 03-promtool-rollback.png / 04-promtool-observability.png | alert-rule unit tests |
| 05-pytest.png | canary statistics, fleet guard, ML sandbox tests |
| 06-ml-sandbox.png | anomaly-canary demo + predictive test selection |

## Still to capture yourself (cannot be generated honestly) — add as `10-*.png` …
1. GitHub → Settings → Rules: `main` ruleset (signed commits, required checks, **no bypass**).
2. A real GitHub Actions run of `ci-pipeline.yml` (green graph with parallel jobs) on your repo or a demo app.
3. SonarCloud project + quality gate; Trivy scan output on any sample image.
4. (Optional bonus) `kind` + Argo Rollouts canary demo, Grafana dashboards imported from `dashboards/grafana/*.json`.
