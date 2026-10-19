# The aggressive method: many agents, no test gates, owned code areas

Status: **live experiment, started 2026-10-18 23:40 PDT.** This page is kept up to date as evidence comes in, including
why if it fails. The rest of this repo describes the gated method that came before it (tests and review scripts decide
when work is done). This page is what we switched to and why.

## The owner's intent (#313, #321)

The project is a video production engine built by about ten AI builders at once, with five leads and one
orchestrator. The owner wants it to:

- run flat-out toward the owner's intent, with no tests, no evals, no TDD and no spec-driven gates;
- keep agents out of each other's code areas, so there are no merge conflicts;
- keep the architecture modular, like lego blocks, and reshape it when areas collide;
- drive progress forward without stops;
- measure success by branches merged and missions moved, not by checks passed.

## What we tried, in order

| When | Setup | What happened |
|---|---|---|
| to 2026-10-18 23:40 | **Gated** (STEERING.md): every finished worker ran the full suite twice (its own report, then the orchestrator's review); merge only on a PASS row for that exact commit | 6 merges in 3 h 40 min (1.6 per hour). About 22 pytest processes queued on one suite lock. A background suite inherited the merge lock's file descriptor, so every merge waited up to 15 minutes behind it. A worker's plain `pytest` run started real paid agent calls through a test. |
| 23:40 | **land.sh**: a branch merges if it merges cleanly and the code starts (import + app build, about 20 s); no suite before or after | Main moved again: 16 merges in the first 10 minutes, from a backlog. |
| 23:49 | **Loop v1**: autopilot lands a builder when its process exits; a work queue starts the next job when a slot frees; inbox events for progress, stalls (20 min with no commit) and silent deaths; after every land, an outcome check starts the merged app on the real projects and loads 34 views | The old gated review in autopilot (two full suites per finished worker) was removed, because it duplicated land.sh. |
| 00:25 | **Missions** (see below): intent, then an inferred purpose, then living milestones; a cheap judge looks at the real output each round and writes the next area-owned jobs | Round 1 of the UI mission took about 2 minutes. It found phone-width clipping, label collisions and a 404 on every page, and queued 2 jobs that wait for the lead's own builder to free those areas. |
| 00:14 | **Areas** (this page): `AREAS.yaml` maps the engine into 24 owned areas; a brief names its areas; the queue never gives one area to two running builders; the watcher posts a collision when two running builders touch one area anyway; every gate and suite step is gone from briefs, standing orders and scripts | Running: see Results. |

## The method

1. **Intent first, in the brief.** Goal, why, what good looks like, the areas the builder owns, and how to look at the
   real output. No acceptance tests, and no suite command.
2. **Own areas, never overlap.**
   - The engine is cut into areas along its seams: UI shell, styles, pages, API, crew, render, finish, checks, edit
     and sound, previs, library, methods, docs.
   - Files that nearly every change touches get a single-owner area of their own, so they don't serialise everything
     else. Examples: the 4,500-line `app.js`, `app.py`, `creative.py`, `CHANGELOG.md`.
   - Catch-all areas (core, docs) are claimed file by file.
   - Tests and per-branch change notes are shared paths, never an area conflict.
3. **A collision means the map is wrong.** When two builders touch one area, the area gets split or the seam gets one
   owner, and the later job waits in the queue. The conflict itself is not just resolved and forgotten.
4. **Land on exit, no gate.** Clean merge plus "the code starts" means merged and pushed. Fix forward. A bad merge is
   fixed by the next commit, not blocked at the door.
5. **Look at the real thing.**
   - The builder opens what it changed (page and screenshot, clip, shot list) and says what it saw.
   - After every land, the merged app runs against the real projects, and the result goes to the inbox.
6. **Never wait.**
   - Completions are events.
   - A freed slot pulls the next queued job whose areas are free.
   - Stalls and silent deaths are posted, and the lead takes an unsticking move (split, smaller proof, fresh worker,
     a default decision).
7. **Code pastes the facts.** Status lines (merged, conflict, progress, stall, collision, outcome) are written by
   scripts, never typed by a model.

8. **Missions, not metrics** (owner, 00:25). The owner gives an intent, often loose ("a UI that helps us make
   hits from scripts").
   - The orchestrator infers the purpose from it: who it's for, why it matters, what it takes (what makes a hit),
     the outcomes wanted.
   - The path is a list of milestones, each a *visible* result.
   - Each round a cheap judge (Haiku) opens the real output and says whether the current milestone is met *as it
     serves the purpose*. "A page with no errors that doesn't help make a hit has not met anything."
   - Then it writes up to three 15-30 minute jobs, each owning its areas.
   - The judge may reshape the milestones when what it sees shows a better path, so the plan stays alive, not locked.
   - A round that sees the same thing with nothing landed forces a change of approach, then asks the lead.
   - Rounds start on events (a land in the mission's areas, or its jobs all gone), at most one round per mission per
     10 minutes.
9. **Strong model for top line only.** The orchestrator and the design agent (Astra) set missions and purposes. Cheap
   models build (Haiku), judge (Haiku) and read research (MiniMax M3.1). No strong-model tokens go on manual reading
   or routine review.

The tools, in `~/AI/handoffs`:
- `mission.py` with `missions/<id>/`: intent, purpose, milestones, rounds;
- `look_pages.py`: real app screenshots at 1440 and 390 px, with console errors;
- `look_run.sh`: a run's status, its timing, and frames from its newest cut;
- `AREAS.yaml` and `areas.py`: map, branch areas, live collisions, conflicts by area;
- `make_brief.py --areas … --look … --queue`;
- `land.sh`;
- `autopilot.py`: land on exit, queue, signals, collisions;
- `outcome_check.sh`;
- `loop_stats.py`: the numbers below.

## Working examples we found (October 2026)

Each source was checked; second-hand figures are marked as such.

- **Anthropic, Claude Code team code review** ([claude.dev, 2026-10-15](https://claude.dev/blog/solving-code-review-at-anthropic/)).
  - Results: from June to September, merged PRs to Claude Code more than doubled, and the reverted share fell more
    than 40%.
  - Monorepo changes per day went from about 2,500 to more than 30,000.
  - What changed: review moved before the PR ("like spellcheck while you write"), with a 3-round cap and diff-only
    re-review.
  - Fix-forward is the norm, and "everything is reversible" (flags, reverts, staged releases).
  - *Not gate-free:* a PR still can't merge with an open bug or security finding. Low-risk changes need no human
    approval.
- **Cursor, scaling long-running autonomous coding** ([cursor.com, Jan 2026](https://cursor.com/blog/scaling-agents)).
  - Hundreds of concurrent agents wrote over a million lines on one project.
  - Flat self-coordination with locks failed, so they split roles: planners (recursive), workers that don't
    coordinate, and a judge at each cycle.
  - Prompts mattered more than the harness or models.
  - Periodic fresh starts fight drift.
- **Anthropic, building a C compiler with parallel Claudes** ([anthropic.com, Feb 2026](https://anthropic.com/engineering/building-c-compiler)).
  - 16 agents, no orchestrator. Each claimed a task with a lock file.
  - Frequent merge conflicts, which the agents resolved themselves.
  - GCC served as the trusted oracle: a runnable reference, not a test gate. (Figures from secondary coverage.)
- **pstack Orchestrate, by Lauren Tan (poteto), used at Cursor and from Grok Bot**
  ([cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack), playbook `orchestrate.md`;
  [Grok Bot launch](https://x.ai/news/introducing-grok-bot)).
  - Rules: "Completions are queue events, not interrupts." "The brief is the product." One writer per worktree.
  - A rolling window of workers, refilled as children finish ("blocking batches pay the slowest child").
  - Landing is continuous, never a terminal phase.
  - "Never reaches the human: … 'should I keep going'. When in doubt, act and log."
  - Its playbooks were used about 10,000 times in a week by Cursor's engineers (author's claim).
  - *Not gate-free:* every unit gets a verdict against the real artifact (live-ui-verified, …). Verification is scaled
    to the unit: a cheap command run by the worker itself, and a cross-model verifier only for high-blast-radius work.
- **Gas Town, by Steve Yegge** (secondary: [heise](https://www.heise.de/en/background/Full-Control-Gas-Town-Orchestrates-Ten-or-More-Coding-Agents-11178824.html), [cloudnativenow](https://cloudnativenow.com/features/gas-town-what-kubernetes-for-ai-coding-agents-actually-looks-like/)).
  20 to 30 parallel Claude Code workers, a dispatcher, watchdogs for stuck workers, and a bisecting merge queue so no
  worker pushes to main.
- **Research on ownership before writing.**
  - Claim Plane ([arXiv 2607.21909](https://arxiv.org/pdf/2607.21909)) declares change intents and admits only
    compatible ones before any write. Its evidence is a 6-pair feasibility check, so treat it as early.
  - Merge-conflict datasets ([arXiv 2604.03551](https://arxiv.org/pdf/2604.03551), [arXiv 2607.04697](https://arxiv.org/pdf/2607.04697)):
    about 28% of agent PRs conflict with their base; 84% of conflicts are in source files; conflict rate grows with
    churn.
- Our own research digest (a cheap model's read of about 60 sources; not every figure re-verified):
  `AGENT_LOOPS_2026-10/FINDINGS.md`. Its strongest point agrees with the examples above: **partition the write-set
  before dispatch.** If builders overlap in a round, the map is wrong.

### pstack against this method

poteto's Orchestrate playbook is the closest working example, and we take most of it:
- completions as queue events;
- the brief as the product;
- a rolling window of workers;
- continuous landing;
- one writer per worktree (our areas);
- never asking the human "should I keep going".

Its Autonomous run playbook is our mission loop in small: "State the exit condition as a checkable predicate", then
"each iteration makes the smallest change the evidence justifies… A plateau is not a stop".

Where it differs: every pstack unit gets a verdict against the real artifact before it lands. We moved that look
*after* the land (the judge and the outcome check) and fix forward. Its coordinator "never authors or edits code". Ours
doesn't either; the builders do.

### The design agent's plan (Astra, L2_loops)

It agreed on areas, landing without gates, and fixing forward. It added three things we took:
- progress is the next *observable mission result*, not merges;
- after landing, run the affected path on a small real input and inspect the frames and audio;
- blocking is an event that releases the builder's claim at once.

It also says to start with five builders (one per lead) and go to ten only when the work is disjoint. The area map is
what makes ten safe.

### Where we depart from every example

Every team above removed the *blocking gate at the end*, but kept a check the agent can run on the real thing:
- Anthropic: review before the PR, and an open security finding still blocks the merge.
- Cursor: a judge at each cycle.
- pstack: a per-unit verdict against the artifact.
- The C compiler: GCC as the oracle.

We go further: no suite and no review step at all. Our quality signal is the builder's own look at the real output plus
the outcome check after every land.

The risk is regressions landing on main. The bet is that fixing them forward, at our merge rate, costs less than gating
everything. If main breaks more often than we can fix it, that bet is wrong, and the first thing to add back is the
cheapest runnable check on the real artifact, not the suite.

## Results so far (updated by hand from `loop_stats.py`)

| Window | Merges | Per hour | Land conflicts | Area collisions | Stalls | Silent deaths | Cards moved (to done) |
|---|---|---|---|---|---|---|---|
| 20:00 to 23:40 (gated) | 6 | 1.6 | n/a | n/a | n/a | n/a | 63 (19) |
| 23:40 to 00:17 (no gate, loop v1) | 28 | 45 | 9 | 3 | 3 | 13* | 22 (6) |

\* Inflated: before 00:14, a builder whose work a lead had already landed was counted as a silent death.

Two notes:
- The first 37 minutes of no-gate landing drained a backlog of finished branches, so 45/h is a peak, not a rate.
- All 9 land conflicts were in shared hub files: `docs/PHASED_ENGINE.md`, `finish/levers.py`, `stages/real.py`,
  `comfy.py`, `edl.py`, `creative.py`, `index.html`.

The first collision scan, at 00:14, found three live collisions, all in the web UI: three UI builders in `app.js`,
the shell and the pages.

One broken main so far: a stray character in `edl.py` landed through a merge at 23:48 and was fixed forward at 23:51.

**Next measurements:** merges per hour after the backlog, conflicts per merge (target: zero between concurrent
builders), the time from collision to reshape, and whether main stays usable. That last one is checked by the outcome
check's 34 views on real projects.
