#!/usr/bin/env python3
"""Canary statistical analysis: Welch t-test (latency), chi-squared (errors), composite score.
Inputs (JSON on stdin or --file): {"canary":{"latency_ms":[...],"errors":int,"requests":int,"cpu":float},
 "baseline":{...same...}}   Exit 0=promote, 2=extend (insufficient data / borderline), 1=rollback."""
import argparse, json, sys
from scipy import stats

def analyse(d, alpha=0.05, min_samples=5000):
    c, b = d["canary"], d["baseline"]
    if c["requests"] < min_samples:
        return {"decision": "extend", "reason": f"only {c['requests']} requests (<{min_samples})"}
    t, p = stats.ttest_ind(c["latency_ms"], b["latency_ms"], equal_var=False)       # Welch
    mc, mb = sum(c["latency_ms"]) / len(c["latency_ms"]), sum(b["latency_ms"]) / len(b["latency_ms"])
    lat_bad = p < alpha and mc > mb * 1.10
    table = [[c["errors"], c["requests"] - c["errors"]], [b["errors"], b["requests"] - b["errors"]]]
    chi2, pe, _, _ = stats.chi2_contingency(table)
    er_c, er_b = c["errors"] / c["requests"], b["errors"] / b["requests"]
    err_bad = pe < alpha and er_c > er_b and (er_c - er_b) > 0.0005
    res_bad = c.get("cpu", 0) > 1.2 * b.get("cpu", 1e9)
    score = 100 - (40 if lat_bad else 0) - (40 if err_bad else 0) - (20 if res_bad else 0)
    decision = "promote" if score >= 90 else "extend" if score >= 70 else "rollback"
    return {"decision": decision, "score": score, "latency_p": p, "error_p": pe, "mean_ms": [mc, mb], "error_rate": [er_c, er_b]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--file"); ap.add_argument("--alpha", type=float, default=0.05); ap.add_argument("--min-samples", type=int, default=5000)
    a = ap.parse_args(); data = json.load(open(a.file) if a.file else sys.stdin)
    out = analyse(data, a.alpha, a.min_samples); print(json.dumps(out))
    sys.exit({"promote": 0, "extend": 2, "rollback": 1}[out["decision"]])
