#!/usr/bin/env python3
"""Sandbox: ML-assisted canary analysis (anomaly detection) — complements the statistical tests in canary-analysis.py.

Why: Welch/chi-squared look at ONE metric at a time. An IsolationForest trained on the stable fleet's recent
multivariate behaviour (error rate, p99, CPU, memory, DB-pool wait) flags canaries that are *jointly* unusual
even when every single metric is inside its threshold (a Category-C style slow burn).

Decision policy (advisory only — never overrides the hard Category-A/B rules):
    anomaly_ratio >= 0.5  -> 'rollback-advised'   |  >= 0.2 -> 'extend'  |  else 'promote'
Usage:  anomaly_canary.py --baseline baseline.csv --canary canary.csv      (columns: err,p99,cpu,mem,pool_wait)
"""
import argparse, json, sys
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURES = ["err", "p99", "cpu", "mem", "pool_wait"]


def fit(baseline: np.ndarray, seed: int = 7):
    scaler = StandardScaler().fit(baseline)
    model = IsolationForest(n_estimators=200, contamination=0.02, random_state=seed).fit(scaler.transform(baseline))
    return scaler, model


def assess(baseline: np.ndarray, canary: np.ndarray, seed: int = 7) -> dict:
    scaler, model = fit(baseline, seed)
    pred = model.predict(scaler.transform(canary))          # -1 = anomaly
    ratio = float((pred == -1).mean())
    decision = "rollback-advised" if ratio >= 0.5 else "extend" if ratio >= 0.2 else "promote"
    return {"anomaly_ratio": round(ratio, 3), "windows": int(len(canary)), "decision": decision}


def synthetic(n=720, seed=1, drift=None):
    """Stable fleet minute-level metrics (12 h). drift = dict of per-feature multipliers for the canary."""
    r = np.random.default_rng(seed)
    base = np.column_stack([
        r.normal(0.0005, 0.0001, n),      # error ratio
        r.normal(120, 12, n),             # p99 ms
        r.normal(0.55, 0.05, n),          # cpu utilisation
        r.normal(0.60, 0.03, n),          # memory utilisation
        r.normal(2, 1.0, n).clip(0),      # pgbouncer waiting clients
    ])
    if drift:
        for i, f in enumerate(FEATURES):
            base[:, i] *= drift.get(f, 1.0)
    return base


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline"); ap.add_argument("--canary"); ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        out = {"healthy": assess(synthetic(720, 1), synthetic(30, 2)),
               "slow_burn(p99 x1.35, cpu x1.3, pool x4; each below hard thresholds)": assess(synthetic(720, 1), synthetic(30, 3, {"p99": 1.35, "cpu": 1.3, "pool_wait": 4.0}))}
        print(json.dumps(out, indent=2)); sys.exit(0)
    b = np.loadtxt(a.baseline, delimiter=",", skiprows=1); c = np.loadtxt(a.canary, delimiter=",", skiprows=1)
    res = assess(b, c); print(json.dumps(res)); sys.exit({"promote": 0, "extend": 2, "rollback-advised": 1}[res["decision"]])
