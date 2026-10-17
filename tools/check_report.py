#!/usr/bin/env python3
"""check_report.py <worktree> [suite summary line] — does the worker's REPORT.json account for every deliverable in BRIEF.json?

The orchestrator writes BRIEF.json into the worktree before briefing (make_brief.py). The worker writes REPORT.json
there before replying. Both stay untracked. This check makes skipped work visible: every deliverable needs an entry,
"done" needs evidence, files named as evidence must exist, the commit must be HEAD, and the claimed test count must
match the suite the orchestrator ran. Prints FAIL/WARN lines; exit 1 on any FAIL. See STEERING.md.

BRIEF.json:  {"deliverables": [{"id": "D1", "text": "...", "proof": "test|screenshot|real-data|none"}]}
REPORT.json: {"status": "done|blocked", "commit": "<sha>", "tests": "<suite summary line>",
              "deliverables": [{"id": "D1", "status": "done|not_done", "evidence": "...", "files": ["_shots/a.png"]}],
              "decide": "..."}
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

wt = Path(sys.argv[1]).resolve()
suite = sys.argv[2] if len(sys.argv) > 2 else ""
fails, warns = [], []


def load(name):
    p = wt / name
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except ValueError as e:
        fails.append(f"{name} is not valid JSON: {e}")
        return None


brief, report = load("BRIEF.json"), load("REPORT.json")
if brief is None:
    warns.append("no BRIEF.json in the worktree: deliverables can't be checked")
if report is None:
    fails.append("no REPORT.json: the worker has not reported (silence is not success)")
if report is not None:
    if report.get("status") not in ("done", "blocked"):
        fails.append(f"status must be done or blocked, not {report.get('status')!r}")
    head = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    c = str(report.get("commit") or "")
    if not c or not head.startswith(c[:7]) or len(c) < 7:
        fails.append(f"commit {c or '(none)'} is not HEAD ({head[:8]})")
    claimed = re.search(r"(\d+) passed", str(report.get("tests") or ""))
    if not claimed:
        fails.append("tests: no pasted summary line with 'N passed'")
    elif re.search(r"\d+ (failed|error)", str(report.get("tests"))):
        fails.append(f"tests line reports failures: {report['tests']}")
    ran = re.search(r"(\d+) passed", suite)
    if claimed and ran and claimed.group(1) != ran.group(1):
        fails.append(f"claimed {claimed.group(1)} passed, the orchestrator's run gave {ran.group(1)}")
    got = {str(d.get("id")): d for d in report.get("deliverables") or [] if isinstance(d, dict)}
    for d in (brief or {}).get("deliverables", []):
        r = got.get(d["id"])
        if r is None:
            fails.append(f"{d['id']} ({d['text'][:60]}) has no entry in REPORT.json")
            continue
        if r.get("status") not in ("done", "not_done"):
            fails.append(f"{d['id']}: status must be done or not_done")
        elif r["status"] == "not_done":
            fails.append(f"{d['id']} not done: {str(r.get('evidence') or 'no reason given')[:120]}")
        elif len(str(r.get("evidence") or "").strip()) < 15:
            fails.append(f"{d['id']} marked done with no evidence")
        for f in r.get("files") or []:
            if not (wt / str(f).split("::")[0]).exists():   # "tests/x.py::test_name" names a test in a file
                fails.append(f"{d['id']}: evidence file {f} does not exist")
        if d.get("proof") == "screenshot" and r.get("status") == "done" and not any(
                str(f).lower().endswith((".png", ".jpg", ".webp")) for f in r.get("files") or []):
            fails.append(f"{d['id']} needs a screenshot in files")
    if report.get("status") == "done" and any(d.get("status") == "not_done" for d in got.values()):
        fails.append("status is done but some deliverables are not_done")

# files changed outside the brief's SCOPE (standing order 7); .gitignore and docs/ are always allowed
scope = (brief or {}).get("scope") or []
if scope:
    changed = subprocess.run(["git", "-C", str(wt), "diff", "--name-only", os.environ.get("BASE", "main") + "...HEAD"],
                             capture_output=True, text=True).stdout.split()
    allowed = tuple(scope) + (".gitignore", "docs/")
    outside = [f for f in changed if not f.startswith(allowed)]
    if outside:
        fails.append(f"files changed outside SCOPE {scope}: {', '.join(outside[:8])}")

for w in warns:
    print("WARN:", w)
for f in fails:
    print("FAIL:", f)
print("REPORT", "FAIL" if fails else "PASS")
sys.exit(1 if fails else 0)
