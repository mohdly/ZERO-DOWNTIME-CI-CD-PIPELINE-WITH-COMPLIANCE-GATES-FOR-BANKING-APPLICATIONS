#!/usr/bin/env python3
"""Sandbox: predictive test selection. Ranks tests by probability of failing for a given change so that the
fast-feedback stage (target <10 min) runs the riskiest tests FIRST and the rest in parallel afterwards.
Safety rule: this only *orders* tests; the full suite still runs before staging promotion (no skipped gates).

Features per (change, test): path-overlap score between changed files and test's covered files, historic fail rate,
days since last failure, test is flaky flag.  Model: LogisticRegression (interpretable for auditors)."""
import numpy as np
from sklearn.linear_model import LogisticRegression


def make_dataset(n=4000, seed=11):
    r = np.random.default_rng(seed)
    overlap = r.beta(1.2, 6, n); hist = r.beta(1, 25, n); recency = r.exponential(20, n); flaky = (r.random(n) < 0.08).astype(float)
    logit = -5.2 + 7.5 * overlap + 9 * hist - 0.02 * recency + 1.2 * flaky
    y = (r.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    return np.column_stack([overlap, hist, recency, flaky]), y


def train(seed=11):
    X, y = make_dataset(seed=seed); split = int(len(y) * 0.75)
    m = LogisticRegression(max_iter=500).fit(X[:split], y[:split])
    return m, X[split:], y[split:]


def recall_at_k(model, X, y, frac=0.2):
    """Share of all failures that fall in the top `frac` of tests ranked by predicted risk."""
    order = np.argsort(-model.predict_proba(X)[:, 1]); k = int(len(y) * frac)
    return float(y[order[:k]].sum() / max(1, y.sum()))


if __name__ == "__main__":
    m, Xt, yt = train()
    print({"recall_in_top_20pct": round(recall_at_k(m, Xt, yt, 0.2), 3), "failures_in_test_set": int(yt.sum()), "tests": int(len(yt))})
