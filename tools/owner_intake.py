#!/usr/bin/env python3
"""UserPromptSubmit hook: in the orchestrator pane (tmux session:0) only, log every owner message verbatim to
tracks/owner_log.jsonl and remind the orchestrator to file each ask or promise as a board card. Elsewhere it does nothing.
It never blocks a prompt: any error exits 0 silently."""
import json, os, subprocess, sys, time
from pathlib import Path
try:
    pane = os.environ.get("TMUX_PANE")
    session = os.environ.get("TMUX_SESSION", "work")
    where = subprocess.run(["tmux", "display", "-p", "-t", pane, "#{session_name}:#{window_index}"],
                           capture_output=True, text=True, timeout=3).stdout.strip() if pane else ""
    if where != f"{session}:0":
        sys.exit(0)
    d = json.load(sys.stdin)
    text = (d.get("prompt") or "").strip()
    if not text or text.startswith("<"):
        sys.exit(0)
    handoffs_dir = Path(os.environ.get("HANDOFFS_DIR", Path.home() / "handoffs"))
    log = handoffs_dir / "tracks" / "owner_log.jsonl"
    n = sum(1 for _ in log.open()) if log.exists() else 0
    with log.open("a") as f:
        f.write(json.dumps({"n": n + 1, "ts": time.time(), "text": text}) + "\n")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext":
        f"Owner message #{n + 1} logged in tracks/owner_log.jsonl. Before you finish this turn: every ask, decision or "
        "promise in it (including your own 'I'll do X') must be a card on the work board (using the card tool) with `--link owner:{n + 1}`. "
        f"The ask audit flags any that are not."}}))
except Exception:
    sys.exit(0)
