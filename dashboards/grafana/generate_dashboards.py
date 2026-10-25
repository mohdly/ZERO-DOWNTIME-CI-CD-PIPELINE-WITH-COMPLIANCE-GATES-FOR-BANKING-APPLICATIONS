#!/usr/bin/env python3
"""Generates the three NovaPay Grafana dashboards (import-ready JSON, schemaVersion 39).
Run:  python3 generate_dashboards.py   ->  engineering-dashboard.json, management-dashboard.json, regulatory-dashboard.json
Metric names are defined in docs/08-observability/observability.md §7 (catalogue) and recording-rules.yaml."""
import json, pathlib
OUT = pathlib.Path(__file__).parent
DS = {"type": "prometheus", "uid": "${DS_PROMETHEUS}"}
_id = [0]

def _t(exprs):
    return [{"refId": chr(65 + i), "datasource": DS, "expr": e[0], "legendFormat": e[1] if len(e) > 1 else "", **({"format": e[2], "instant": True} if len(e) > 2 else {})} for i, e in enumerate(exprs)]

def panel(kind, title, x, y, w, h, exprs, unit=None, steps=None, desc="", mappings=None, thresholds_mode="absolute"):
    _id[0] += 1
    d = {"id": _id[0], "type": kind, "title": title, "description": desc, "datasource": DS, "gridPos": {"x": x, "y": y, "w": w, "h": h}, "targets": _t(exprs),
         "fieldConfig": {"defaults": {}, "overrides": []}}
    if unit: d["fieldConfig"]["defaults"]["unit"] = unit
    if steps: d["fieldConfig"]["defaults"]["thresholds"] = {"mode": thresholds_mode, "steps": [{"color": c, "value": v} for c, v in steps]}
    if mappings: d["fieldConfig"]["defaults"]["mappings"] = mappings
    return d

def row(title, y):
    _id[0] += 1
    return {"id": _id[0], "type": "row", "title": title, "collapsed": False, "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}, "panels": []}

def dash(title, uid, desc, panels, refresh, rng, tags, extra_vars=()):
    return {"__inputs": [{"name": "DS_PROMETHEUS", "label": "Prometheus", "type": "datasource", "pluginId": "prometheus", "pluginName": "Prometheus"}],
            "title": title, "uid": uid, "description": desc, "tags": ["novapay"] + tags, "schemaVersion": 39, "version": 1, "editable": True,
            "refresh": refresh, "time": {"from": rng, "to": "now"}, "timezone": "Asia/Kolkata",
            "annotations": {"list": [{"name": "Deployments", "datasource": DS, "enable": True, "iconColor": "blue", "expr": "changes(novapay_deploy_finished_total{env=\"production\"}[1m]) > 0", "titleFormat": "Prod deploy"}]},
            "templating": {"list": [{"name": "service", "type": "query", "datasource": DS, "query": "label_values(istio_requests_total, destination_service_name)", "includeAll": True, "multi": True, "current": {"text": "All", "value": "$__all"}}, *extra_vars]},
            "panels": panels}

G, Y, R = "green", "yellow", "red"
# ------------------------------------------------------------------ ENGINEERING (real-time ops)
_id[0] = 0
e = [row("Release health — canary vs stable", 0),
 panel("timeseries", "5xx % by version (stable vs canary)", 0, 1, 8, 8, [('sum by (version)(rate(istio_requests_total{destination_service_name=~"$service",response_code=~"5.."}[1m])) / sum by (version)(rate(istio_requests_total{destination_service_name=~"$service"}[1m]))', "{{version}}")], "percentunit", [(G, None), (R, 0.05)], "Category-A rollback trigger at 5%"),
 panel("timeseries", "p99 latency by version (ms)", 8, 1, 8, 8, [('histogram_quantile(0.99, sum by (le, version)(rate(istio_request_duration_milliseconds_bucket{destination_service_name=~"$service"}[1m])))', "{{version}}")], "ms", [(G, None), (Y, 200), (R, 500)]),
 panel("stat", "Active rollouts / canary weight", 16, 1, 4, 8, [('max by (rollout)(rollout_info_canary_weight)', "{{rollout}}")], "percent", [(G, None), (Y, 1), (R, 100)]),
 panel("stat", "Alerts firing (A/B/C)", 20, 1, 4, 8, [('count(ALERTS{alertstate="firing",category="A"}) or vector(0)', "A"), ('count(ALERTS{alertstate="firing",category="B"}) or vector(0)', "B")], None, [(G, None), (R, 1)]),
 row("Saturation & dependencies", 9),
 panel("stat", "DB pool waiting clients (PgBouncer)", 0, 10, 6, 6, [('max(pgbouncer_pools_client_waiting_connections{database="novapay"})', "waiting")], "none", [(G, None), (Y, 20), (R, 50)], "A5 trigger: >50 for 20 s"),
 panel("timeseries", "RabbitMQ queue depth", 6, 10, 6, 6, [('sum by (queue)(rabbitmq_queue_messages_ready)', "{{queue}}")], "none", [(G, None), (R, 1000)], "HPA custom metric at 1000"),
 panel("timeseries", "Payment gateway timeout ratio", 12, 10, 6, 6, [('sum(rate(gateway_requests_total{outcome="timeout"}[1m])) / sum(rate(gateway_requests_total[1m]))', "timeout %")], "percentunit", [(G, None), (R, 0.2)]),
 panel("timeseries", "UPI technical decline rate (TD%)", 18, 10, 6, 6, [('sum(rate(upi_txn_total{outcome="technical_decline"}[30s])) / sum(rate(upi_txn_total[30s]))', "TD %")], "percentunit", [(G, None), (R, 0.02)], "NPCI-style TD%; page at >2% for 30 s"),
 row("Automation & pipeline", 16),
 panel("table", "Rollback-bot activity (last 24 h)", 0, 17, 12, 8, [('sum by (category, trigger, service)(increase(novapay_deploy_rollback_total[24h]))', "", "table")]),
 panel("heatmap", "Pipeline stage duration (s)", 12, 17, 6, 8, [('sum by (le)(rate(novapay_stage_duration_seconds_bucket[15m]))', "{{le}}")], "s"),
 panel("stat", "Synthetic probe success (UPI collect/pay)", 18, 17, 6, 8, [('avg(probe_success{job="upi-synthetic"})', "success")], "percentunit", [(R, None), (Y, 0.99), (G, 0.999)])]
(OUT / "engineering-dashboard.json").write_text(json.dumps(dash("NovaPay Engineering — Release & Reliability (real-time)", "novapay-eng-release", "Real-time ops view for SRE/on-call: canary health, saturation, rollback bot, synthetic probes.", e, "15s", "now-1h", ["engineering", "ops"]), indent=2))

# ------------------------------------------------------------------ MANAGEMENT (weekly / monthly)
_id[0] = 0
m = [row("DORA four keys", 0),
 panel("stat", "Deployment frequency (prod / day)", 0, 1, 6, 6, [('sum(increase(novapay_deploy_finished_total{env="production",result="success"}[1d]))', "deploys/day")], "none", [(R, None), (Y, 1), (G, 3)], "Elite: multiple per day"),
 panel("stat", "Lead time commit→prod (p50, min)", 6, 1, 6, 6, [('histogram_quantile(0.5, sum by (le)(rate(novapay_pipeline_commit_to_prod_seconds_bucket[7d]))) / 60', "p50")], "m", [(G, None), (Y, 90), (R, 120)], "SLO ≤120 min (≈105 budgeted)"),
 panel("stat", "Change failure rate", 12, 1, 6, 6, [('sum(increase(novapay_deploy_rollback_total[30d])) / sum(increase(novapay_deploy_finished_total{env="production"}[30d]))', "CFR")], "percentunit", [(G, None), (Y, 0.03), (R, 0.05)], "Target <5%"),
 panel("stat", "MTTR (p50, min)", 18, 1, 6, 6, [('histogram_quantile(0.5, sum by (le)(rate(novapay_incident_mttr_seconds_bucket[30d]))) / 60', "MTTR")], "m", [(G, None), (Y, 15), (R, 60)], "Was 4.5 h; target <15 min"),
 row("Trends", 7),
 panel("timeseries", "Deployments per day", 0, 8, 12, 8, [('sum(increase(novapay_deploy_finished_total{env="production"}[1d]))', "production")], "none"),
 panel("timeseries", "Lead time p50 / p90 (min)", 12, 8, 12, 8, [('histogram_quantile(0.5, sum by (le)(rate(novapay_pipeline_commit_to_prod_seconds_bucket[1d]))) / 60', "p50"), ('histogram_quantile(0.9, sum by (le)(rate(novapay_pipeline_commit_to_prod_seconds_bucket[1d]))) / 60', "p90")], "m", [(G, None), (R, 120)]),
 row("Reliability & efficiency", 16),
 panel("gauge", "Availability — payment path (30 d)", 0, 17, 6, 8, [('novapay:availability:ratio_30d', "availability")], "percentunit", [(R, None), (Y, 0.9999), (G, 0.99999)], "Five-nines design target = 99.999 %"),
 panel("stat", "Error budget remaining (30 d)", 6, 17, 6, 8, [('1 - (novapay:error_ratio:rate30d / 0.00001)', "budget left")], "percentunit", [(R, None), (Y, 0.25), (G, 0.5)]),
 panel("bargauge", "Top gate blockers (7 d)", 12, 17, 6, 8, [('topk(5, sum by (gate)(increase(novapay_gate_result_total{result="FAIL"}[7d])))', "{{gate}}")], "none"),
 panel("stat", "Build success rate", 18, 17, 3, 8, [('sum(rate(novapay_build_total{result="success"}[7d])) / sum(rate(novapay_build_total[7d]))', "success")], "percentunit", [(R, None), (Y, 0.9), (G, 0.95)]),
 panel("stat", "Feedback loop p50 (min)", 21, 17, 3, 8, [('histogram_quantile(0.5, sum by (le)(rate(novapay_feedback_loop_seconds_bucket[7d]))) / 60', "p50")], "m", [(G, None), (R, 10)], "Target <10 min")]
(OUT / "management-dashboard.json").write_text(json.dumps(dash("NovaPay Management — Delivery & Reliability (weekly / monthly)", "novapay-mgmt-dora", "Executive view: DORA metrics, availability vs five-nines SLO, error budget, top blockers.", m, "5m", "now-30d", ["management", "dora"]), indent=2))

# ------------------------------------------------------------------ REGULATORY (audit-ready)
_id[0] = 0
g = [row("Control evidence", 0),
 panel("table", "Gate results per release (last 7 d)", 0, 1, 12, 9, [('sum by (service, gate, result)(increase(novapay_gate_result_total[7d]))', "", "table")], desc="RBI 4.2 / 5.1; PCI 6.2–6.5. Source: immutable audit store."),
 panel("table", "Exceptions register (with expiry)", 12, 1, 12, 9, [('novapay_exception_expires_timestamp_seconds * 1000', "", "table"), ('novapay_exception_active', "", "table")], desc="Time-boxed approvals; expired exceptions re-block the gate automatically."),
 row("Integrity & segregation of duties", 10),
 panel("stat", "Audit hash-chain valid", 0, 11, 4, 6, [('min(novapay_audit_chain_valid)', "chain")], None, [(R, None), (G, 1)], "RBI 6.1 / PCI 10.2", [{"type": "value", "options": {"0": {"text": "BROKEN", "color": "red"}, "1": {"text": "VALID", "color": "green"}}}]),
 panel("stat", "Releases with complete audit record", 4, 11, 4, 6, [('novapay_release_audit_complete_ratio', "complete")], "percentunit", [(R, None), (Y, 0.99), (G, 1)], "Target 100 %"),
 panel("stat", "SoD violations (30 d)", 8, 11, 4, 6, [('sum(increase(novapay_gate_result_total{gate="G7-SOD",result="FAIL"}[30d]))', "blocked")], "none", [(G, None), (Y, 1)], "Blocked attempts are evidence the control works"),
 panel("stat", "Deploys inside blackout (30 d)", 12, 11, 4, 6, [('sum(increase(novapay_blackout_violation_total[30d])) or vector(0)', "violations")], "none", [(G, None), (R, 1)], "Target 0"),
 panel("stat", "Active / expired-unclosed exceptions", 16, 11, 4, 6, [('count(novapay_exception_active == 1) or vector(0)', "active"), ('count(novapay_exception_expired_open == 1) or vector(0)', "expired")], "none", [(G, None), (R, 1)]),
 panel("stat", "Critical CVE remediation (p90, h)", 20, 11, 4, 6, [('histogram_quantile(0.9, sum by (le)(rate(novapay_cve_remediation_seconds_bucket{severity="critical"}[90d]))) / 3600', "p90")], "h", [(G, None), (R, 72)], "SLA 72 h"),
 row("Coverage & incidents", 17),
 panel("table", "RBI / PCI control coverage", 0, 18, 12, 8, [('max by (control, gate)(novapay_control_coverage)', "", "table")], desc="Matrix from docs/03-compliance-gates §7"),
 panel("table", "Incident log & regulator notification status", 12, 18, 12, 8, [('novapay_incident_info', "", "table")], desc="SEV, duration, RBI/CERT-In notification state")]
(OUT / "regulatory-dashboard.json").write_text(json.dumps(dash("NovaPay Regulatory — Audit-Ready Compliance Evidence", "novapay-reg-audit", "For RBI auditor / Head of Compliance: control evidence, exceptions, SoD, audit integrity, incidents.", g, "1m", "now-30d", ["regulatory", "audit"]), indent=2))
print("generated 3 dashboards")
