#!/usr/bin/env python3
"""make_brief.py <worktree> "D1|screenshot|text" "D2|test|text" ... — write BRIEF.json (the numbered deliverables)
into a worker's worktree before briefing, and print the lines to paste into the brief. proof is one of
test, screenshot, real-data, none. check_report.py compares the worker's REPORT.json against it."""
import json
import sys
from pathlib import Path

wt = Path(sys.argv[1]).resolve()
items = []
for arg in sys.argv[2:]:
    i, proof, text = (arg.split("|", 2) + ["", ""])[:3]
    if proof not in ("test", "screenshot", "real-data", "none"):
        sys.exit(f"bad proof {proof!r} in {arg!r}")
    items.append({"id": i, "proof": proof, "text": text})
(wt / "BRIEF.json").write_text(json.dumps({"deliverables": items}, indent=2) + "\n")
for d in items:
    print(f"{d['id']}. {d['text']} (proof: {d['proof']})")
print(f"\nBRIEF.json written to {wt}")
