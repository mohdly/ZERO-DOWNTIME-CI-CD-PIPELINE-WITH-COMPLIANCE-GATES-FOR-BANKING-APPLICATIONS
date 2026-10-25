import importlib.util, pathlib, subprocess, sys, json
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("canary_analysis", HERE / "canary-analysis.py")
ca = importlib.util.module_from_spec(spec); spec.loader.exec_module(ca)
rng = np.random.default_rng(42)


def data(c_mean=120, b_mean=120, c_err=10, b_err=100, c_req=24000, b_req=480000, c_cpu=0.5, b_cpu=0.5):
    return {"canary": {"latency_ms": list(rng.normal(c_mean, 12, 60)), "errors": c_err, "requests": c_req, "cpu": c_cpu},
            "baseline": {"latency_ms": list(rng.normal(b_mean, 12, 60)), "errors": b_err, "requests": b_req, "cpu": b_cpu}}


def test_healthy_canary_promotes():
    assert ca.analyse(data())["decision"] == "promote"

def test_latency_regression_is_not_promoted():
    r = ca.analyse(data(c_mean=160))             # +33 % latency, p << 0.05
    assert r["decision"] == "rollback" and r["score"] == 60

def test_latency_and_error_regression_rolls_back():
    r = ca.analyse(data(c_mean=160, c_err=120))  # 0.5 % vs 0.02 % errors
    assert r["decision"] == "rollback" and r["score"] == 20

def test_error_rate_regression_alone_blocks_promotion():
    r = ca.analyse(data(c_err=120))
    assert r["decision"] != "promote" and r["error_p"] < 0.05

def test_insufficient_sample_extends_never_promotes():
    r = ca.analyse(data(c_req=1200, c_err=0))
    assert r["decision"] == "extend" and "only 1200" in r["reason"]

def test_cpu_regression_penalised():
    assert ca.analyse(data(c_cpu=0.8))["score"] == 80

def test_cli_exit_codes(tmp_path):
    f = tmp_path / "in.json"; f.write_text(json.dumps(data(c_mean=170, c_err=150)))
    p = subprocess.run([sys.executable, str(HERE / "canary-analysis.py"), "--file", str(f)], capture_output=True)
    assert p.returncode == 1
