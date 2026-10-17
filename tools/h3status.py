#!/usr/bin/env python3
"""board_status.py: the work board. Gathers the tracks' state into one self-contained HTML page (and JSON) that the
owner can open at any time. Run every 2 minutes by a scheduler timer. Read-only: it never changes anything it looks at.

Sources:
- tracks/*.yaml, kept by the orchestrator and the track leads;
- windows (idle time);
- git worktrees with their REPORT.json and the review ledger;
- recent merges;
- live workers (processes);
- the owner queue;
- the dashboard's projects.
"""
import datetime
import html
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

import yaml

HANDOFFS_DIR = Path(os.environ.get("HANDOFFS_DIR", Path.home() / "handoffs"))
H = HANDOFFS_DIR
REPO = Path(os.environ.get("CODEBASE_ROOT", Path.home() / "codebase"))
OUT = Path(os.environ.get("BOARD_OUTPUT", Path.home() / "board" / "output"))
REVIEW = Path(os.environ.get("REVIEW_OUTPUT", Path.home() / "board" / "reviews"))
TMUX_SESSION = os.environ.get("TMUX_SESSION", "work")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://127.0.0.1:8080")
STALE_H = 2.0


def sh(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def ago(ts):
    if not ts:
        return "?"
    s = max(0, time.time() - ts)
    return f"{int(s // 60)} min ago" if s < 3600 else f"{s / 3600:.1f} h ago" if s < 86400 else f"{s / 86400:.1f} d ago"


def tracks():
    out = []
    for f in sorted((H / "tracks").glob("*.yaml")):
        try:
            t = yaml.safe_load(f.read_text()) or {}
        except yaml.YAMLError as e:   # one broken file must never take the whole board down
            t = {"name": f.stem, "goal": f"UNREADABLE track file {f.name}: {str(e).splitlines()[0]}; the lead must fix its YAML",
                 "metric": {"name": "", "now": "unknown", "target": ""}}
        t["_updated"] = f.stat().st_mtime
        t["_stale"] = time.time() - t["_updated"] > STALE_H * 3600
        out.append(t)
    order = ["Orchestrator", "Run operations", "Speed", "Creative", "Product", "R&D lab"]
    return sorted(out, key=lambda t: order.index(t.get("name")) if t.get("name") in order else 99)


def windows():
    rows = []
    for line in sh("tmux", "list-windows", "-t", TMUX_SESSION, "-F", "#{window_index}\t#{window_name}\t#{window_activity}").splitlines():
        i, n, a = (line.split("\t") + ["", "", "0"])[:3]
        rows.append({"index": i, "name": n, "idle": ago(int(a or 0))})
    return rows


def worktrees():
    ledger = {}
    lf = H / "ledger.tsv"
    if lf.is_file():
        for line in lf.read_text().splitlines():
            p = line.split("\t")
            if len(p) >= 5:
                ledger[p[2]] = (p[3], p[4], p[0])
    merged = set(sh("git", "-C", str(REPO), "branch", "--merged", "main").split())
    rows = []
    for block in sh("git", "-C", str(REPO), "worktree", "list", "--porcelain").split("\n\n"):
        d = dict(l.split(" ", 1) for l in block.splitlines() if " " in l)
        path = Path(d.get("worktree", ""))
        br = d.get("branch", "").replace("refs/heads/", "")
        if not br or path == REPO or br in merged:
            continue
        head = d.get("HEAD", "")
        last = sh("git", "-C", str(path), "log", "-1", "--format=%ct %s").strip().split(" ", 1)
        rep = {}
        try:
            rep = json.loads((path / "REPORT.json").read_text())
        except (OSError, ValueError):
            pass
        done = sum(1 for x in rep.get("deliverables", []) if x.get("status") == "done")
        total = len(rep.get("deliverables", []))
        v = ledger.get(head)
        rows.append({"branch": br, "last": ago(int(last[0])) if last and last[0].isdigit() else "?",
                     "subject": last[1] if len(last) > 1 else "", "report": f"{done}/{total} done" if total else "no report",
                     "review": f"{v[0]} ({v[1]})" if v else "not reviewed"})
    return rows


def merges():
    return [l for l in sh("git", "-C", str(REPO), "log", "main", "--merges", "-12", "--format=%cr\t%s").splitlines()]


def live_workers():
    rows = []
    for line in sh("ps", "-eo", "pid,etimes,args").splitlines():
        # Look for worker processes; exact pattern depends on your setup
        if "worker" in line and "grep" not in line:
            p = line.split(None, 2)
            if len(p) >= 3:
                cwd = sh("readlink", f"/proc/{p[0]}/cwd").strip()
                rows.append({"who": "Worker", "where": Path(cwd).name, "for": f"{int(p[1]) // 60} min"})
    return rows


def projects():
    try:
        with urllib.request.urlopen(f"{DASHBOARD_URL}/api/projects", timeout=5) as r:
            out = []
            for p in json.loads(r.read()):
                if p.get("kind") != "production" or p.get("archived"):
                    continue
                lr = p.get("latest_run") or {}
                out.append({"title": p.get("title") or p["name"], "stage": lr.get("stage") or "no run yet",
                            "status": f"{lr.get('state') or lr.get('status') or ''} · {lr.get('progress', 0)}%" if lr else "",
                            "pct": int(lr.get("progress") or 0) if lr else 0})
            return out
    except Exception:  # the board must still render when the dashboard is down
        return []


def owner_queue():
    f = H / "tracks" / "owner_queue.md"
    return [l[2:] for l in f.read_text().splitlines() if l.startswith("- ")] if f.is_file() else []


def inbox():
    f = H / "tracks" / "inbox.md"
    return [l for l in f.read_text().splitlines() if l.strip()][-12:] if f.is_file() else []


def failures():
    f = H / "AGENT_STEERING.md"
    return sum(1 for l in f.read_text().splitlines() if l.startswith("| ") and l[2:4].strip().isdigit()) if f.is_file() else 0


THREADS = {  # window, team name (what it does, in plain words), one-line job
    "orch": ("0", "Steering", "Plans, reviews and merges; talks to you"),
    "run": ("1", "Production runs", "Keeps the production's runs moving"),
    "speed": ("2", "Pipeline speed", "Pre-production in 15 minutes"),
    "creative": ("3", "Creative work", "Story and features, tested against off"),
    "product": ("4", "App & Dev desk", "The app and this development desk"),
    "rnd": ("5", "Research", "Models, recipes and quality work"),
}
KINDS = {"decide": "Decision", "fix": "Fix", "build": "Build", "test": "Test", "design": "Design", "run": "Production",
         "merge": "Review & merge", "docs": "Docs"}
COLS = [("you", "Waiting on you"), ("doing", "Doing"), ("review", "In review"), ("ready", "Ready to merge"),
        ("blocked", "Blocked"), ("next", "Up next"), ("done", "Done today")]
CARDS = H / "cards"


def cards():
    out = []
    for f in sorted(CARDS.glob("*.json")):
        try:
            c = json.loads(f.read_text())
        except ValueError:
            continue
        if c.get("col") == "done" and time.time() - c.get("done_at", 0) > 86400:
            continue
        pid = c.get("pid")
        c["_live"] = bool(pid) and Path(f"/proc/{pid}").exists()
        c["_ended"] = bool(pid) and not c["_live"] and c.get("col") == "doing"
        out.append(c)
    return sorted(out, key=lambda c: -c.get("updated", 0))


ICON = {  # Status glyphs
    "you": '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="6" fill="var(--you)"/><rect x="6.2" y="3.2" width="1.6" height="4.6" rx=".8" fill="#fff"/><circle cx="7" cy="10.2" r=".95" fill="#fff"/></svg>',
    "doing": '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="var(--doing)" stroke-width="1.6"/><path d="M7 3.5A3.5 3.5 0 0 1 7 10.5Z" fill="var(--doing)"/></svg>',
    "review": '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="var(--review)" stroke-width="1.6"/><path d="M7 3.5A3.5 3.5 0 1 1 3.5 7H7Z" fill="var(--review)"/></svg>',
    "ready": '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="6" fill="var(--ready)"/><path d="M4.4 7.2l1.8 1.8 3.4-3.6" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "blocked": '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="var(--blocked)" stroke-width="1.6"/><path d="M3.2 10.8l7.6-7.6" stroke="var(--blocked)" stroke-width="1.6"/></svg>',
    "next": '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="var(--next)" stroke-width="1.6" stroke-dasharray="2.2 1.6"/></svg>',
    "done": '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="6" fill="var(--done)"/><path d="M4.4 7.2l1.8 1.8 3.4-3.6" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}


STAGES = ["Script", "Look & style", "Shot list", "World & cast", "Music & sound", "Boards", "Dailies", "The cut"]


def page(d):
    e = html.escape
    cs = d["cards"]
    n = lambda col: sum(1 for c in cs if c.get("col") == col)
    tname = lambda k: THREADS.get(k, ("", k, ""))[1]

    def row(c):
        k = c.get("thread", "")
        nxt = c.get("outcome") if c.get("col") == "done" and c.get("outcome") else c.get("next", "")
        live = '<i class=live></i>' if c["_live"] else ""
        return (f'<li class=row data-t="{e(k)}" data-k="{e(c.get("kind", ""))}"><span class=ic>{ICON.get(c.get("col"), "")}</span><span class=main><span class=ti>{e(c.get("title", ""))}</span>'
                f'<span class=nx>{e(nxt)}</span></span><span class="kind k-{e(c.get("kind", ""))}">{e(KINDS.get(c.get("kind"), ""))}</span><span class="lab t-{e(k)}"><i></i>{e(tname(k))}</span>'
                f'<span class=who>{e(c.get("who", ""))}{live}</span><span class=age>{ago(c.get("updated")).replace(" ago", "")}</span></li>')

    # 1. one sentence on the whole system
    you, blocked = [c for c in cs if c.get("col") == "you"], [c for c in cs if c.get("col") == "blocked"]
    if blocked:
        state, tone = f"{len(blocked)} item{'s' if len(blocked) > 1 else ''} blocked.", "amber"
    else:
        state, tone = "Everything is moving.", "green"
    ask = f"{len(you)} decision{'s' if len(you) != 1 else ''} for you" + (", none of them stops a run." if you else ".") if you else "Nothing needs you."

    # 2. needs you: big cards
    def youcard(c):
        k = c.get("thread", "")
        return (f'<article class="ask t-{e(k)}" data-t="{e(k)}" data-k="{e(c.get("kind", ""))}"><div class=who2><i></i>{e(tname(k))}<span class="kind k-{e(c.get("kind", ""))}">{e(KINDS.get(c.get("kind"), ""))}</span></div><h3>{e(c.get("title", ""))}</h3>'
                f'<p>{e(c.get("next", ""))}</p></article>')
    asks = "".join(youcard(c) for c in you) or '<p class=calm>Nothing waiting on you.</p>'

    # 3. production: stage line
    def prodline(p):
        cur = STAGES.index(p["stage"]) if p["stage"] in STAGES else -1
        steps = "".join(f'<li class="{"done" if i < cur else "cur" if i == cur else ""}"><span></span>{e(st)}</li>' for i, st in enumerate(STAGES))
        return (f'<article class=prod><div class=ph><h3>{e(p["title"])}</h3><span>{e(p["stage"])} · {p.get("pct", 0)}% of this stage</span></div>'
                f'<ol class=steps>{steps}</ol></article>')
    prods = "".join(prodline(p) for p in d["projects"] if p["stage"] != "no run yet") or '<p class=calm>No production running.</p>'

    # 4. threads: one tile each with a state colour
    def tile(k):
        w, name, job = THREADS[k]
        mine = [c for c in cs if c.get("thread") == k and c.get("col") != "done"]
        cnt = lambda col: sum(1 for c in mine if c.get("col") == col)
        if cnt("blocked"):
            st, cls = "Blocked", "red"
        elif cnt("doing"):
            st, cls = "Moving", "green"
        elif cnt("review") or cnt("ready"):
            st, cls = "In review", "blue"
        else:
            st, cls = "Idle", "grey"
        pick = lambda *cols: next((c for c in mine if c.get("col") in cols), None)
        now = pick("doing") or pick("blocked") or pick("review", "ready") or pick("you") or pick("next")
        parts = [f"{cnt('doing')} in progress" if cnt("doing") else "", f"{cnt('review') + cnt('ready')} in review" if cnt("review") + cnt("ready") else "",
                 f"{cnt('next')} up next" if cnt("next") else ""]
        foryou = f'<span class="pill red">{cnt("you")} for you</span>' if cnt("you") else ""
        return (f'<article class="tile t-{k}" data-t="{k}"><div class=tt><b>{e(name)}</b><span class=pills>{foryou}<span class="pill {cls}">{st}</span></span></div>'
                f'<p class=now>{e(now["title"]) if now else "Nothing in progress"}</p><p class=job>{e(job)}</p>'
                f'<p class=cnt>{" · ".join(x for x in parts if x) or "&nbsp;"}</p></article>')

    landed = [c for c in cs if c.get("col") == "done"]
    wins = "".join(f'<li data-t="{e(c.get("thread", ""))}" data-k="{e(c.get("kind", ""))}">{ICON["done"]}<span>{e(c.get("title", ""))}</span></li>' for c in landed[:8])
    rest = [c for c in cs if c.get("col") != "you"]
    order = {k: i for i, (k, _) in enumerate(COLS)}
    rest.sort(key=lambda c: (order.get(c.get("col"), 9), -c.get("updated", 0)))
    return f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=120><title>Board</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel=stylesheet>
<style>
:root{{--bg:#f7f7f5;--panel:#fff;--ink:#141517;--muted:#5f636a;--faint:#9a9ea5;--line:#e8e8e4;--soft:#f1f1ee;
--red:#e5484d;--amber:#e38a00;--green:#1f9d55;--blue:#5e6ad2;--grey:#a3a7ae;
--you:var(--red);--doing:var(--amber);--review:var(--blue);--ready:var(--green);--blocked:var(--red);--next:#a8acb3;--done:var(--green);
--orch:#5e6ad2;--run:#1f9d55;--speed:#e38a00;--creative:#d6409f;--product:#0ea5b7;--rnd:#8e4ec6}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0e0f10;--panel:#16171a;--ink:#ececee;--muted:#a1a4ab;--faint:#6f737b;--line:#24262a;--soft:#1b1c1f}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
main{{max-width:1120px;margin:0 auto;padding:36px 20px 64px}}
.eyebrow{{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);display:flex;justify-content:space-between}}
.hero{{display:flex;align-items:flex-start;gap:14px;margin:10px 0 36px}}.dot{{width:14px;height:14px;border-radius:50%;flex:none;margin-top:10px;box-shadow:0 0 0 6px color-mix(in srgb,var(--c) 18%,transparent);background:var(--c)}}
.hero h1{{font-size:30px;line-height:1.2;font-weight:700;letter-spacing:-.02em;margin:0}}.hero h1 span{{color:var(--muted);font-weight:500}}
.filters{{display:grid;gap:8px;margin:-12px 0 32px}}.fg{{display:flex;gap:6px;flex-wrap:wrap;align-items:center}}.fg>span{{font-size:12px;font-weight:600;color:var(--faint);width:44px;text-transform:uppercase;letter-spacing:.06em}}
.chip{{font:inherit;font-size:13px;color:var(--muted);background:var(--panel);border:1px solid var(--line);border-radius:99px;padding:4px 12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}}.chip b{{font-weight:500;color:var(--faint)}}.chip i{{width:8px;height:8px;border-radius:50%;background:var(--c)}}
.chip.on{{color:var(--panel);background:var(--ink);border-color:var(--ink)}}.chip.on b{{color:inherit;opacity:.7}}.hide{{display:none!important}}
.kind{{font-size:11px;font-weight:600;border-radius:5px;padding:1px 7px;color:var(--kc);background:color-mix(in srgb,var(--kc) 13%,transparent);flex:none;margin-left:auto}}
.who2 .kind{{margin-left:auto}}.k-decide{{--kc:var(--red)}}.k-fix{{--kc:#d9480f}}.k-build{{--kc:var(--blue)}}.k-test{{--kc:#8e4ec6}}.k-design{{--kc:#d6409f}}.k-run{{--kc:var(--green)}}.k-merge{{--kc:#0ea5b7}}.k-docs{{--kc:#868e96}}
.green{{--c:var(--green)}}.amber{{--c:var(--amber)}}.red{{--c:var(--red)}}.blue{{--c:var(--blue)}}.grey{{--c:var(--grey)}}
h2{{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 12px;display:flex;gap:8px;align-items:center}}h2 b{{color:var(--faint);font-weight:500}}
section{{margin-bottom:40px}}
.asks{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
.ask{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
.ask h3{{font-size:17px;line-height:1.3;margin:6px 0 6px;font-weight:600}}.ask p{{margin:0;color:var(--muted);font-size:14px}}
.who2{{font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px}}.who2 i,.lab i{{width:8px;height:8px;border-radius:50%;background:var(--c)}}
.prod{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px}}.ph{{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}}
.ph h3{{margin:0;font-size:19px;font-weight:600}}.ph span{{color:var(--muted);font-size:14px}}
.steps{{list-style:none;padding:0;margin:18px 0 2px;display:grid;grid-template-columns:repeat(8,1fr);gap:4px}}
.steps li{{font-size:12px;color:var(--faint);padding-top:12px;position:relative}}.steps li span{{position:absolute;top:0;left:0;right:0;height:6px;border-radius:9px;background:var(--line)}}
.steps li.done{{color:var(--muted)}}.steps li.done span{{background:var(--green)}}.steps li.cur{{color:var(--ink);font-weight:600}}.steps li.cur span{{background:linear-gradient(90deg,var(--amber) 50%,var(--line) 50%)}}
.tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.tile{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;display:flex;flex-direction:column;gap:4px}}
.tt{{display:flex;justify-content:space-between;align-items:center;gap:8px}}.tt b{{font-size:16px}}.pills{{display:flex;gap:6px}}
.pill{{font-size:12px;font-weight:600;color:var(--c);background:color-mix(in srgb,var(--c) 12%,transparent);border-radius:99px;padding:2px 10px;white-space:nowrap}}
.now{{margin:6px 0 0;font-size:15px;font-weight:500;line-height:1.35}}.job{{margin:0;color:var(--faint);font-size:12.5px}}.cnt{{margin:8px 0 0;color:var(--muted);font-size:12.5px}}
.wins{{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}}.wins li{{display:flex;align-items:center;gap:7px;background:var(--panel);border:1px solid var(--line);border-radius:99px;padding:5px 12px 5px 8px;font-size:13.5px}}
.wins svg{{width:15px;height:15px}}.calm{{color:var(--muted);margin:0}}
details.all{{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden}}details.all summary{{cursor:pointer;padding:14px 18px;font-weight:600;color:var(--muted);list-style:none}}
ul.list{{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}}.row{{display:flex;align-items:center;gap:10px;padding:8px 18px;border-bottom:1px solid var(--line);font-size:13.5px}}
.ic{{display:inline-flex;width:14px;height:14px;flex:none}}.ic svg{{width:14px;height:14px}}.main{{flex:1;min-width:0;display:flex;gap:10px;align-items:baseline}}.row .kind{{margin-left:0;width:96px;text-align:center}}
.ti{{font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:50%}}.nx{{color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.lab{{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--muted);flex:none}}.who,.age{{font-size:12px;color:var(--faint);width:48px;text-align:right;flex:none}}
.live{{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--green);margin-left:4px}}
.t-orch{{--c:var(--orch)}}.t-run{{--c:var(--run)}}.t-speed{{--c:var(--speed)}}.t-creative{{--c:var(--creative)}}.t-product{{--c:var(--product)}}.t-rnd{{--c:var(--rnd)}}
@media(max-width:800px){{.tiles{{grid-template-columns:1fr 1fr}}.steps{{grid-template-columns:repeat(4,1fr);row-gap:14px}}}}
@media(max-width:560px){{main{{padding:24px 16px 48px}}.hero h1{{font-size:24px}}.tiles{{grid-template-columns:1fr}}.row{{flex-wrap:wrap}}.main{{flex-basis:calc(100% - 24px);flex-direction:column;gap:0}}.ti,.nx{{max-width:100%;white-space:normal}}.who,.age{{width:auto}}}}
</style></head><body><main>
<div class=eyebrow><span>Work board</span><span>updated {e(d['at'][11:])}</span></div>
<div class="hero {tone}"><span class=dot></span><h1>{e(state)} <span>{e(ask)}</span></h1></div>
<div class=filters><div class=fg><span>Type</span><button class="chip on" data-fk="">All</button>{''.join(f'<button class="chip k-{k}" data-fk="{k}">{v}<b>{sum(1 for c in cs if c.get("kind") == k and c.get("col") != "done")}</b></button>' for k, v in KINDS.items())}</div>
<div class=fg><span>Team</span><button class="chip on" data-ft="">All</button>{''.join(f'<button class="chip t-{k}" data-ft="{k}"><i></i>{e(v[1])}</button>' for k, v in THREADS.items())}</div></div>
<section><h2>Your decisions <b>{len(you)}</b></h2><div class=asks>{asks}</div></section>
<section><h2>Production</h2>{prods}</section>
<section><h2>Threads</h2><div class=tiles>{''.join(tile(k) for k in THREADS)}</div></section>
{f'<section><h2>Landed today <b>{len(landed)}</b></h2><ul class=wins>{wins}</ul></section>' if landed else ''}
<details class=all><summary>All work · {len(rest)} items</summary><ul class=list>{''.join(row(c) for c in rest)}</ul></details>
</main><script>
const F={{k:"",t:""}};
function apply(){{document.querySelectorAll('[data-t]').forEach(el=>{{const okT=!F.t||el.dataset.t===F.t;const okK=!F.k||!('k' in el.dataset)||el.dataset.k===F.k;el.classList.toggle('hide',!(okT&&okK)||(!!F.k&&el.classList.contains('tile')))}});
document.querySelectorAll('section,details.all').forEach(sec=>{{const items=sec.querySelectorAll('[data-t]');if(items.length)sec.classList.toggle('hide',![...items].some(i=>!i.classList.contains('hide')))}});
const all=document.querySelector('details.all');if(all&&(F.k||F.t))all.open=true;try{{localStorage.setItem('h3f2',JSON.stringify(F))}}catch(e){{}}}}
document.querySelectorAll('[data-fk]').forEach(b=>b.onclick=()=>{{F.k=b.dataset.fk;document.querySelectorAll('[data-fk]').forEach(x=>x.classList.toggle('on',x===b));apply()}});
document.querySelectorAll('[data-ft]').forEach(b=>b.onclick=()=>{{F.t=b.dataset.ft;document.querySelectorAll('[data-ft]').forEach(x=>x.classList.toggle('on',x===b));apply()}});
try{{const s=JSON.parse(localStorage.getItem('h3f2')||'{{}}');if(s.k)document.querySelector('[data-fk="'+s.k+'"]')?.click();if(s.t)document.querySelector('[data-ft="'+s.t+'"]')?.click()}}catch(e){{}}
</script></body></html>"""


def text(d):
    """The board as a text recap: counts, then each column's cards in one line each."""
    cs = d.get("cards", [])
    icon = {"you": "🔴", "doing": "🟡", "review": "🟡", "ready": "✅", "blocked": "⛔", "next": "⬜", "done": "✅"}
    n = lambda col: sum(1 for c in cs if c.get("col") == col)
    out = [f"Board · {d['at']} · {n('you')} waiting on you · {n('doing')} doing · {n('review') + n('ready')} in review · {n('blocked')} blocked"]
    for p in d["projects"]:
        if p["stage"] != "no run yet":
            out.append(f"🎬 {p['title']}: {p['stage']} {p.get('pct', 0)}%")
    for key, label in COLS:
        items = [c for c in cs if c.get("col") == key]
        if not items:
            continue
        out.append(f"\n{label}")
        for c in items:
            who = THREADS.get(c.get("thread"), ("", c.get("thread", "")))[1]
            nxt = c.get("outcome") if key == "done" and c.get("outcome") else c.get("next", "")
            out.append(f"{icon[key]} {c.get('title', '')} · {who}" + (f" — {nxt}" if nxt else ""))
    return "\n".join(out)


def main():
    d = {"at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "tracks": tracks(), "windows": windows(),
         "worktrees": worktrees(), "merges": merges(), "workers": live_workers(), "projects": projects(),
         "queue": owner_queue(), "inbox": inbox(), "failures": failures(), "cards": cards()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html.tmp").write_text(page(d))
    (OUT / "index.html.tmp").replace(OUT / "index.html")
    # The Dev desk serves only files inside a review's own folder (or the data roots), so the board's review gets a copy.
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / "board.html.tmp").write_text(page(d))
    (REVIEW / "board.html.tmp").replace(REVIEW / "board.html")
    (OUT / "status.json").write_text(json.dumps(d, default=str, indent=1))


if __name__ == "__main__":
    import sys
    main()
    if "--text" in sys.argv:
        print(text(json.loads((OUT / "status.json").read_text())))
