"""Knight Capital guard: verify-fleet-version.sh against a fake kubectl (no cluster needed)."""
import json, os, pathlib, stat, subprocess, tempfile
HERE = pathlib.Path(__file__).resolve().parent.parent
GOOD = "sha256:" + "a" * 64
OLD = "sha256:" + "b" * 64


def pods(digests, cfg="c1"):
    return {"items": [{"metadata": {"name": f"p{i}", "annotations": {"novapay/config-sha": cfg if not isinstance(cfg, list) else cfg[i]}},
                       "status": {"containerStatuses": [{"imageID": f"registry/x@{d}"}]}} for i, d in enumerate(digests)]}


def run(items, expected=GOOD, mixed="false"):
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        k = d / "kubectl"
        # fake kubectl: 'get pods' prints fixture, anything else is logged (rollback/patch/argo calls)
        k.write_text("#!/usr/bin/env bash\nif [[ \"$*\" == *'get pods'* ]]; then cat \"$FIXTURE\"; else echo \"$*\" >> \"$CALLS\"; fi\n")
        k.chmod(k.stat().st_mode | stat.S_IEXEC)
        (d / "fx.json").write_text(json.dumps(items))
        env = dict(os.environ, PATH=f"{d}:{os.environ['PATH']}", FIXTURE=str(d / "fx.json"), CALLS=str(d / "calls.log"), ALLOW_MIXED=mixed)
        p = subprocess.run(["bash", str(HERE / "verify-fleet-version.sh"), "ns", "payments-api", expected], cwd=d, env=env, capture_output=True, text=True)
        calls = (d / "calls.log").read_text() if (d / "calls.log").exists() else ""
        return p.returncode, p.stdout + p.stderr, calls


def test_all_pods_same_digest_passes_and_no_rollback():
    rc, out, calls = run(pods([GOOD] * 8))
    assert rc == 0 and "Fleet verified: 8 pods" in out and calls == ""

def test_seven_of_eight_updated_triggers_killswitch():          # the exact Knight Capital failure
    rc, out, calls = run(pods([GOOD] * 7 + [OLD]))
    assert rc == 1 and "FLEET MISMATCH" in out and "argo rollouts abort" in calls

def test_config_drift_triggers_killswitch():
    rc, out, calls = run(pods([GOOD] * 4, cfg=["c1", "c1", "c1", "c2"]))
    assert rc == 1 and "FLEET MISMATCH" in out

def test_canary_mixed_state_allowed_only_when_flag_set():
    mix = pods([GOOD, GOOD, OLD, OLD, OLD, OLD])
    assert run(mix, mixed="true")[0] == 0
    assert run(mix, mixed="false")[0] == 1
