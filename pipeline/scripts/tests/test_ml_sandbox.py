import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from ml import anomaly_canary as ac, predictive_test_selection as pts

def test_healthy_canary_not_flagged():
    r = ac.assess(ac.synthetic(720, 1), ac.synthetic(30, 2))
    assert r["decision"] == "promote" and r["anomaly_ratio"] < 0.2

def test_slow_burn_below_hard_thresholds_is_flagged():
    drift = {"p99": 1.35, "cpu": 1.3, "pool_wait": 4.0}      # none individually breaches A/B rules
    r = ac.assess(ac.synthetic(720, 1), ac.synthetic(30, 3, drift))
    assert r["decision"] in ("extend", "rollback-advised") and r["anomaly_ratio"] >= 0.2

def test_severe_drift_advises_rollback():
    r = ac.assess(ac.synthetic(720, 1), ac.synthetic(30, 4, {"err": 20, "p99": 2.5}))
    assert r["decision"] == "rollback-advised"

def test_predictive_selection_beats_random_ordering():
    m, X, y = pts.train()
    assert pts.recall_at_k(m, X, y, 0.2) > 0.45          # random ordering would catch ~20 %
