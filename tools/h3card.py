#!/usr/bin/env python3
"""h3card.py: the work board cards. One card = one piece of work, short enough to read at a glance.

  h3card.py add  <id> --title "..." --thread speed --col doing --next "..." [--aspect a,b] [--who model] [--pid N] [--branch b] [--link url]
  h3card.py set  <id> [any of the same options]
  h3card.py done <id> [--outcome "..."]
  h3card.py ls   [--col doing] [--thread speed]

Columns: you (waiting on the owner), doing, review, ready (to merge), blocked (stuck: someone must act), next (queued,
including work that simply waits for something else to finish), done.
Threads: orch, run, speed, creative, product, rnd.
Kinds (type of work): decide (owner decision), fix (something broken), build (new capability), test (research,
A/B, measurement), design (mockups, plans), run (production work), merge (review and merge), docs.
Title at most 70 characters and next at most 110: the board is for a busy person; detail belongs in the linked file.
Cards live one per file in $WORK_DIR/cards/<id>.json (default ~/handoffs/cards/), so leads never overwrite each other. Nothing is deleted:
a finished card moves to the done column and leaves the board after a day.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

HANDOFFS_DIR = Path(os.environ.get("HANDOFFS_DIR", Path.home() / "handoffs"))
DIR = HANDOFFS_DIR / "cards"
COLS = ["you", "doing", "review", "ready", "blocked", "next", "done"]
THREADS = ["orch", "run", "speed", "creative", "product", "rnd"]
KINDS = ["decide", "fix", "build", "test", "design", "run", "merge", "docs"]
WHO = ["Haiku", "Claude", "design-model", "GPU", "owner", "script"]
LIMITS = {"title": 70, "next": 110, "outcome": 110}

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("cmd", choices=["add", "set", "done", "ls"])
ap.add_argument("id", nargs="?")
ap.add_argument("--title")
ap.add_argument("--thread", choices=THREADS)
ap.add_argument("--col", choices=COLS)
ap.add_argument("--next")
ap.add_argument("--aspect", help="comma-separated aspect ids (aspects.yaml in your project)")
ap.add_argument("--who", choices=WHO)
ap.add_argument("--kind", choices=KINDS, help="type of work")
ap.add_argument("--pid", type=int)
ap.add_argument("--branch")
ap.add_argument("--link")
ap.add_argument("--outcome")
a = ap.parse_args()

for k, n in LIMITS.items():
    v = getattr(a, k)
    if v and len(v) > n:
        sys.exit(f"refused: --{k} is {len(v)} characters; keep it under {n} (put detail in the linked file)")

DIR.mkdir(parents=True, exist_ok=True)

if a.cmd == "ls":
    for f in sorted(DIR.glob("*.json")):
        c = json.loads(f.read_text())
        if (a.col and c.get("col") != a.col) or (a.thread and c.get("thread") != a.thread):
            continue
        print(f"{c['id']:28} {c.get('col',''):8} {c.get('thread',''):9} {c.get('title','')}")
    sys.exit()

if not a.id or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,47}", a.id):
    sys.exit("refused: id must be short kebab-case, e.g. face-skin-fix")
f = DIR / f"{a.id}.json"
c = json.loads(f.read_text()) if f.is_file() else {}
if a.cmd == "add" and c:
    sys.exit(f"refused: card {a.id} exists; use set")
if a.cmd in ("set", "done") and not c:
    sys.exit(f"refused: no card {a.id}; use add")
if a.cmd == "add" and not (a.title and a.thread and a.col):
    sys.exit("refused: add needs --title, --thread and --col")

c["id"] = a.id
for k in ("title", "thread", "col", "next", "who", "kind", "pid", "branch", "link", "outcome"):
    v = getattr(a, k)
    if v is not None:
        c[k] = v
if a.aspect is not None:
    c["aspect"] = [x for x in re.split(r"[\s,]+", a.aspect) if x]
if a.cmd == "done":
    c["col"] = "done"
if c.get("col") == "done":
    c.setdefault("done_at", time.time())
else:
    c.pop("done_at", None)
c.setdefault("created", time.time())
c["updated"] = time.time()
tmp = f.with_suffix(".tmp")
tmp.write_text(json.dumps(c, indent=1))
tmp.replace(f)
print(f"{a.id}: {c['col']} · {c.get('title','')}")
