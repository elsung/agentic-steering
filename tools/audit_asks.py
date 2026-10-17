#!/usr/bin/env python3
"""audit_asks.py [--since N] [--deep]: which owner messages have no card on the work board?

Default (every 30 min, CPU-only timer): pure Python, no model, no network. Each owner message from
tracks/owner_log.jsonl is matched against every card's words (title, next step, outcome); a message that shares too
few distinctive words with any card is listed in tracks/unmatched.md, and one board card counts them. It is a coarse
net on purpose: it never creates work by itself, it only points at messages for the orchestrator to file or dismiss.

--deep (on demand only, never on a timer): asks a small model to judge the unmatched messages properly.
Essential tracking must never depend on a remote model: the log (owner_intake hook) and this matcher run without one.
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

HANDOFFS_DIR = Path(os.environ.get("HANDOFFS_DIR", Path.home() / "handoffs"))
H = HANDOFFS_DIR
T = H / "tracks"
STOP = set("""about above after again also always another anything around because been before being below between both
could does doing done each even every from have here into just know like make more most much need only other over
really should some something still such than that their them then there these they thing things this those through
want were what when where which while will with would your yeah okay lets also maybe think going right yes able""".split())
MIN_OVERLAP = 2      # distinctive words a message must share with some card
MIN_WORDS = 6        # shorter messages ("ok keep going") are not asks


def words(t):
    return {w for w in re.findall(r"[a-z][a-z0-9-]{3,}", t.lower()) if w not in STOP}


def main():
    state_f = T / ".audit_state.json"
    state = json.loads(state_f.read_text()) if state_f.exists() else {"last_n": 0, "unmatched": []}
    if "--since" in sys.argv:
        state["last_n"] = int(sys.argv[sys.argv.index("--since") + 1]); state["unmatched"] = []
    msgs = [json.loads(l) for l in (T / "owner_log.jsonl").read_text().splitlines() if l.strip()]
    cards = [json.loads(f.read_text()) for f in sorted((H / "cards").glob("*.json"))]
    vocab = [words(" ".join(str(c.get(k, "")) for k in ("title", "next", "outcome"))) for c in cards]
    linked = {int(c["link"].split(":")[1]) for c in cards if str(c.get("link", "")).startswith("owner:")}
    keep = [n for n in state.get("unmatched", []) if n not in linked]
    for m in msgs:
        if m["n"] <= state["last_n"] or m["n"] in linked:
            continue
        w = words(m["text"])
        if len(w) < MIN_WORDS:
            continue
        if max((len(w & v) for v in vocab), default=0) < MIN_OVERLAP:
            keep.append(m["n"])
    state["last_n"] = max([m["n"] for m in msgs] + [state["last_n"]])
    # re-check earlier unmatched messages against today's cards: filing a card clears them
    by_n = {m["n"]: m for m in msgs}
    keep = sorted({n for n in keep if n in by_n and n not in linked
                   and max((len(words(by_n[n]["text"]) & v) for v in vocab), default=0) < MIN_OVERLAP})
    state["unmatched"] = keep; state["at"] = time.time()
    state_f.write_text(json.dumps(state))
    lines = [f"# Owner messages with no matching card ({len(keep)})", "",
             "File each as a card (`card_tool add ... --link owner:N`) or dismiss it with a card in done.", ""]
    lines += [f"- **#{n}** {by_n[n]['text'][:220].replace(chr(10), ' ')}" for n in keep]
    (T / "unmatched.md").write_text("\n".join(lines) + "\n")
    card = ["set" if (H / "cards/unmatched-asks.json").exists() else "add", "unmatched-asks", "--thread", "orch", "--who", "script",
            "--col", "next" if keep else "done", "--title", f"{len(keep)} owner messages without a card",
            "--next", "Triage tracks/unmatched.md: file or dismiss", "--outcome", "All owner messages have a card"]
    subprocess.run([sys.executable, str(H / "card_tool.py")] + card, capture_output=True)
    if "--deep" in sys.argv and keep:
        prompt = ("For each owner message below, say in one line whether it holds a concrete ask that is still open, "
                  "given these board cards. JSON lines only: {\"n\": N, \"open\": true|false, \"title\": \"<60 chars>\"}\n\nCARDS:\n"
                  + "\n".join(c.get("title", "") for c in cards) + "\n\nMESSAGES:\n"
                  + "\n".join(f"#{n}: {by_n[n]['text'][:800]}" for n in keep))
        r = subprocess.run(["claude", "-p", "--model", "haiku", prompt], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600)
        (T / "unmatched_deep.md").write_text(r.stdout)
    with (T / "audit_log.md").open("a") as f:
        f.write(f'{time.strftime("%m-%d %H:%M")} · checked to owner message #{state["last_n"]} · {len(keep)} without a card\n')
    print(len(keep), "owner messages without a card")


if __name__ == "__main__":
    main()
