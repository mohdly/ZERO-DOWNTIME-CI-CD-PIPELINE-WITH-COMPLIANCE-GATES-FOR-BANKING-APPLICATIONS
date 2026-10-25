#!/usr/bin/env bash
# Usage: blackout-check.sh <standard|high-risk|hotfix>   exit 0 = allowed, 1 = blocked
set -euo pipefail
PROFILE="${1:-standard}"; DIR="$(cd "$(dirname "$0")" && pwd)"
python3 - "$PROFILE" "$DIR/blackout-calendar.yaml" <<'PY'
import sys, datetime as dt, yaml
from zoneinfo import ZoneInfo
profile, cal = sys.argv[1], yaml.safe_load(open(sys.argv[2]))
now = dt.datetime.now(ZoneInfo(cal["timezone"])); hm = now.strftime("%H:%M")
def in_win(w): a, b = w.split("-"); return a <= hm < b
blocked = []
r = cal["recurring"]
sd = r["salary_days"]
if now.day in sd["days_of_month"] and sd["from"] <= hm <= sd["to"]: blocked.append("salary day")
if now.day in r["month_end"]["days_of_month"] and profile != "hotfix": blocked.append("month-end freeze")
if any(in_win(w) for w in r["daily_peak"]["windows"]) and profile != "hotfix": blocked.append("daily peak hours")
if now.weekday() == r["friday_late"]["weekday"] and hm >= r["friday_late"]["from"] and profile == "high-risk": blocked.append("Friday late high-risk")
for f in cal.get("fixed", []):
    if dt.date.fromisoformat(f["from"]) <= now.date() <= dt.date.fromisoformat(f["to"]): blocked.append(f["name"])
if blocked and not (profile == "hotfix" and blocked == ["daily peak hours"]):
    print("BLOCKED:", ", ".join(blocked), "- Emergency Change approval required"); sys.exit(1)
print("Deploy window OK", now.isoformat())
PY
