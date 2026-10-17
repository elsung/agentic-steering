#!/usr/bin/env python3
"""make_brief.py <worktree> --goal "..." --why "..." --scope "src/app/web/,tests/web/" --verify "cmd" [--timebox "45 min"]
                 "D1|screenshot|text" "D2|test|text" ...

Writes BRIEF.json (goal, scope, deliverables) into a worker's worktree and prints the brief skeleton to paste:
GOAL / WHY / SCOPE / VERIFY / TIMEBOX / DELIVERABLES / STANDING ORDERS (STANDING_ORDERS.md, verbatim).
A field you cannot fill means the unit is not scoped yet, so the script refuses (pstack orchestrate: "missing fields
are a refuse-to-spawn condition"). proof is one of test, screenshot, real-data, none. check_report.py checks the
worker's REPORT.json and the branch's changed files against this file."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("worktree")
ap.add_argument("deliverables", nargs="+", help='"ID|proof|text"')
ap.add_argument("--goal", required=True, help="one sentence: the outcome, for whom")
ap.add_argument("--why", required=True, help="why it matters now / what good looks like")
ap.add_argument("--scope", required=True, help="comma-separated path prefixes the worker may write")
ap.add_argument("--verify", required=True, help="exact command(s) that prove it")
ap.add_argument("--timebox", default="60 min", help="on expiry: commit what is done, report, stop")
a = ap.parse_args()

for k in ("goal", "why", "scope", "verify"):
    if len(getattr(a, k).strip()) < 8:
        raise SystemExit(f"refused: --{k} is empty or too thin; the unit is not scoped yet")
wt = Path(a.worktree).resolve()
items = []
for arg in a.deliverables:
    i, proof, text = (arg.split("|", 2) + ["", ""])[:3]
    if proof not in ("test", "screenshot", "real-data", "none"):
        raise SystemExit(f"bad proof {proof!r} in {arg!r}")
    if len(text.strip()) < 10:
        raise SystemExit(f"refused: deliverable {i} has no real text")
    items.append({"id": i, "proof": proof, "text": text})
scope = [s.strip() for s in a.scope.split(",") if s.strip()]
(wt / "BRIEF.json").write_text(json.dumps(
    {"goal": a.goal, "why": a.why, "scope": scope, "verify": a.verify, "timebox": a.timebox,
     "deliverables": items}, indent=2) + "\n")

standing = (HERE / "STANDING_ORDERS.md").read_text().strip()
print(f"""GOAL: {a.goal}
WHY: {a.why}
WORKTREE: {wt} (already created; work only here)
SCOPE (you may write only under): {', '.join(scope)}
VERIFY: {a.verify}
TIMEBOX: {a.timebox}. On expiry, commit what is done, write REPORT.json with the rest not_done, and stop.

DELIVERABLES""")
for d in items:
    print(f"{d['id']}. {d['text']} (proof: {d['proof']})")
print(f"\n{standing}\n\n(BRIEF.json written to {wt})")
