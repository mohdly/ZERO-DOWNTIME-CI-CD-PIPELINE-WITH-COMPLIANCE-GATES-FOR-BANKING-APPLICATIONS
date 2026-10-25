#!/usr/bin/env python3
"""Renders low-fidelity wireframe PNGs straight from the Grafana JSON (so wireframe == implemented layout)."""
import json, pathlib, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patches as P
G = pathlib.Path(__file__).resolve().parent.parent / "grafana"
COL = {"stat": "#DCEBFA", "gauge": "#FFF0D6", "timeseries": "#E6F4E4", "table": "#F1E8FA", "heatmap": "#FDE7E7", "bargauge": "#FFFBD6"}
ICON = {"stat": "▣ KPI", "gauge": "◔ gauge", "timeseries": "∿ time series", "table": "▤ table", "heatmap": "▦ heatmap", "bargauge": "▮ bars"}
for name, role in [("engineering", "real-time ops · SRE / on-call"), ("management", "weekly / monthly · CTO, VP Eng"), ("regulatory", "audit-ready · Head of Compliance, RBI auditor")]:
    d = json.load(open(G / f"{name}-dashboard.json")); ps = d["panels"]
    H = max(p["gridPos"]["y"] + p["gridPos"]["h"] for p in ps)
    fig, ax = plt.subplots(figsize=(16, max(6, H * 0.36))); ax.set_xlim(0, 24); ax.set_ylim(H + 2, -2); ax.axis("off")
    ax.text(0, -1.4, f"{d['title']}   —   {role}   |   refresh {d['refresh']} · range {d['time']['from']}", fontsize=13, weight="bold")
    for p in ps:
        g = p["gridPos"]
        if p["type"] == "row":
            ax.add_patch(P.Rectangle((0, g["y"]), 24, 0.9, fc="#333333", ec="none")); ax.text(0.3, g["y"] + 0.62, p["title"].upper(), color="white", fontsize=9, weight="bold"); continue
        ax.add_patch(P.FancyBboxPatch((g["x"] + 0.08, g["y"] + 0.08), g["w"] - 0.16, g["h"] - 0.16, boxstyle="round,pad=0.02,rounding_size=0.25", fc=COL.get(p["type"], "#EEE"), ec="#555555", lw=1))
        ax.text(g["x"] + 0.3, g["y"] + 0.6, p["title"], fontsize=8.5, weight="bold", va="center", wrap=True)
        ax.text(g["x"] + g["w"] / 2, g["y"] + g["h"] / 2 + 0.4, ICON.get(p["type"], p["type"]), fontsize=10, ha="center", color="#666666")
        thr = p["fieldConfig"]["defaults"].get("thresholds")
        if thr and len(thr["steps"]) > 1:
            ax.text(g["x"] + g["w"] - 0.3, g["y"] + g["h"] - 0.4, "thresholds: " + " / ".join(str(s["value"]) for s in thr["steps"][1:]), fontsize=6.5, ha="right", color="#7a0000")
    fig.savefig(pathlib.Path(__file__).parent / f"{name}-wireframe.png", dpi=130, bbox_inches="tight"); plt.close(fig); print("wireframe", name)
