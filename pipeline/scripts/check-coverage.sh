#!/usr/bin/env bash
# Usage: check-coverage.sh --min-line 80 --min-branch 70   (reads JaCoCo XML)
set -euo pipefail
MIN_LINE=80; MIN_BRANCH=70; REPORT="build/reports/jacoco/test/jacocoTestReport.xml"
while [[ $# -gt 0 ]]; do case $1 in --min-line) MIN_LINE=$2; shift 2;; --min-branch) MIN_BRANCH=$2; shift 2;; --report) REPORT=$2; shift 2;; *) echo "unknown $1"; exit 2;; esac; done
python3 - "$REPORT" "$MIN_LINE" "$MIN_BRANCH" <<'PY'
import sys, xml.etree.ElementTree as ET
rep, ml, mb = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
root = ET.parse(rep).getroot()
def pct(t):
    c = next(x for x in root.findall("counter") if x.get("type") == t)
    m, cv = int(c.get("missed")), int(c.get("covered"))
    return 100 * cv / (m + cv) if m + cv else 100.0
line, br = pct("LINE"), pct("BRANCH")
print(f"line={line:.1f}% (min {ml}) branch={br:.1f}% (min {mb})")
sys.exit(0 if line >= ml and br >= mb else 1)
PY
