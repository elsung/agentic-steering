# The Button Mash Method

VERSION 1.6.0 (2026-10-20), with the skill [skills/button-mash](skills/button-mash/SKILL.md). History: [CHANGELOG.md](CHANGELOG.md).

> **Hyper-aggressively push the motion and work of the agents forward; assessment loops, not evals or tests; no gates;
> iterate rapidly toward discovering and refining what we want.** (the owner's definition, #516)

Status: **live experiment, started 2026-10-18 23:40 PDT.** This page is kept up to date as evidence comes in, including
why if it fails. The rest of this repo describes the gated method that came before it, where tests and review scripts
decide when work is done. This page is what we switched to and why. (This page was first called METHOD_AGGRESSIVE.md;
the old name now points here.)

## How it steers: hard guidelines, strong steering, judgment (owner #521, #522)

The method is carried to every agent as a skill, [skills/button-mash](skills/button-mash/SKILL.md), read at every
start. It has three layers, and it deliberately avoids brittle mechanical rules:

1. **Hard guidelines** always hold, and each comes with its why so it can be applied in cases nobody foresaw:
   - never destroy the owner's work (move instead of delete);
   - never spend or publish without the owner's OK;
   - never stop someone's live work;
   - while working toward a goal, push hard and never leave a run stuck without saying why (idle capacity matters only when goal work waits for it);
   - pace deliberately when told, or for real limits: power and heat, cost, rate limits;
   - no gates;
   - nothing private in public material.
2. **Strong steering** gives direction:
   - push toward the goal behind the goal, with the ambition protocol (altitude, depth with the pros' real tools, range) and nouns turned into verbs;
   - act on the best default;
   - prefer reversible moves;
   - find the smallest move that unblocks progress;
   - fix causes and apply the fix to the live work at once;
   - assess the real output;
   - mash, but spend where it counts: burn tokens on the hard problem and the live blocker, and use the cheapest capable model, short briefs and one agent per task elsewhere;
   - keep the owner's view live (archive what your work supersedes, with a note on what replaced it);
   - report outcomes.
3. **Judgment** covers everything else. It is taught by worked examples from real stalls, with no numeric thresholds,
   timeouts or checklists. Rules written as thresholds kept breaking in the cases they didn't foresee. Judgment with a
   clear why bends to fit them.

The watchdog follows the same spirit. It reads signals (who owns a process, whether it's still making progress, and
whether capacity sits idle with work waiting). It acts when the answer is clear and flags when it isn't.

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

The tools, in the loop's tools directory:
- `mission.py` with `missions/<id>/`: intent, purpose, milestones, rounds;
- `look_pages.py`: real app screenshots at 1440 and 390 px, with console errors;
- `look_run.sh`: a run's status, its timing, and frames from its newest cut;
- `AREAS.yaml` and `areas.py`: map, branch areas, live collisions, conflicts by area;
- `make_brief.py --areas … --look … --queue`;
- `land.sh`;
- `autopilot.py`: land on exit, queue, signals, collisions;
- `outcome_check.sh`;
- `loop_stats.py`: the numbers below.

## Staying smart through a very long run (owner, 2026-10-21)

The owner's observation, after two days of continuous work across many context compactions with no hand-off
documents: what keeps the models smart and focused is not memory but **living sources of truth that stay current**.

- **Close-eye management with watchers:** the status board and the review desk are watched continuously, so a stale
  card or an item with nothing to look at is caught within minutes, not discovered by the owner.
- **The research docs and the pipeline spec are the sources of truth.** An agent arriving fresh, or one whose context
  was just summarised, reads them and knows what is true now. The spec is regenerated whenever the settings it
  describes change, so its version always matches what runs.
- **Regular checking keeps them clean, current and improving,** so they give a clear picture of what we are doing.
- **Old documents are archived, never left to rot and never deleted:** moved aside, listed in an archive index
  (where each went, why, and how to fetch it back), so a stale page never misleads and nothing is lost.

**How we apply it:** a regression watch runs on every heartbeat (every 15 minutes). It fixes what is safe (a pipeline
spec out of date is rewritten; a card still open after its branch merged is closed; a duplicate queued job is moved
aside) and flags the rest (cards untouched for hours, review items with nothing to look at, a mission still working on
a closed run, a status file that stopped updating). It keeps the archive index current and says only what is new.

**Why it works:** compaction keeps a summary of the conversation, but the work's real state lives in files. When those
files are current, a summary is enough; when they rot, no summary can save the run. Freshness of the sources, not
the length of the context, is what lets a long run stay coherent.

## Forward and clean: fast motion without code rot (owner, 2026-10-21)

> "how do we be super ambitious and press forward and iterate towards our goal but doing smartly with architecture in
> mind ... so we dont end up with spaghetti code and code rot and massive compounding tech debt? ... extreme forward
> motion and fervor for constant quality improvements ... while still be able to have cleaner and cleaner and better
> and better code and construction as we iterate aggressively."

The research digest is in research/FORWARD_AND_CLEAN.md (Beck, Fowler, evolutionary architecture, Rieseberg, the
large-codebase practices of fast teams, and 2024-2026 studies of agent-written code). Its main finding fits this
method: **a check that would block a merge is worth more as a sensor the builder sees inside its own loop**, with the
judgement-heavy measures on a trend board. Agents' failure mode is measured and specific: they re-implement what
already exists, because they can't see it, not because they're careless. So the cure is mostly a map plus a nudge,
not discipline.

**The practices (each with the trend that shows it working; never a gate):**

1. **One commit, one kind.** A behaviour change and a structure change (rename, move, extract) go in separate
   commits. *Trend:* share of mixed commits.
2. **Tidy what the next change needs, in its own small commit, first or right after.** The rest goes on a list,
   never a cleanup branch. *Trend:* size of structure commits.
3. **Second copy: look it up. Third copy: consolidate.** Agents reach a re-implementation by the second time, so the
   brief says "before you add a player, modal, poller or endpoint, find the existing one and extend it". *Trend:*
   how many places define each pattern (rot signals: players, modals, toasts, pollers).
4. **An architecture map per area, cited in every brief.** Short: what each part owns, its seams, and where each kind
   of new thing belongs. A map stops reinvention where history alone does not. *Trend:* features that extend an
   existing module vs add a parallel one.
5. **One writer per hotspot.** A hub file (the big route file, the big page script) has one builder at a time
   (the area queue already does this); others add a new file the hub includes. *Trend:* land conflicts per merge.
6. **A cleanup queue with a target, fed by real signals.** Rank areas by churn x size x fix commits and by
   direction (getting worse or better), not by a score. While any hot area is getting worse, at least one builder
   slot in five takes the top item of the queue; as the trends improve, the slice shrinks. *Trend:* the slope of the
   worst area's signals.
7. **Delete by moving, only what the evidence says is dead.** Dead code, flags and endpoints go to a retired folder
   when nothing references them (search proves it; for endpoints, the request log too). False positives are the
   worse failure. *Trend:* count of dead items found vs moved.
8. **Small landings; migrations, never rewrites.** A big change goes in shards behind a seam (strangler fig, branch
   by abstraction), each shard landed and undoable, and the temporary seam has a removal date. *Trend:* the biggest
   landed diff; the oldest open branch.
9. **Rot as a trend on the board.** The rot signals are measured hourly from main and kept as history; the board
   shows the slope. A threshold may ratchet one notch with a reason; it never blocks. *Trend:* the board's slope.
10. **Outside eyes on the real output.** A fresh-context look at the running page, render or run, and a red-team
    crew member whose job is to show the change is wrong; never the builder grading itself. *Trend:* faults the
    outside look catches before the owner does.

**Where we differ from the sources.** Nearly every team studied blocks merges on deterministic checks and runs full
suites. We don't (owner #321, #572): the deterministic checks (dependency direction, duplicate blocks, dead symbols)
run as sensors inside the builder's loop and travel with its report; semantic conflicts are caught by looking at
the real output after a merge and fixing forward. The owner proposed a fixed one-in-five cleanup slot; no source
sets a ratio, so we run it as a floor while the trends are worsening, not as a permanent tax.

**Applied first (2026-10-21):** rot signals measured hourly (worst: the route file, 8052 lines and 207 routes, and the
main page script, 5973 lines, each changed ~190 times and fixed ~17 times in a week); three cleanup builders on the
web layer (the area map and dead-code inventory, one shared poller, the first route group out of the route file).
Before/after numbers go here when they land.

**First results (00:32 -> 01:39, about an hour, with feature work landing on top):** four cleanup builders, all landed
with behaviour unchanged by their own before/after probes. The main page script went from 5973 to 5413 lines (its
Dev desk block moved to its own file); the route file from 8052 to 7868 lines and from 207 to 194 routes (the
house-rules group moved to its own module); polling loops from 10 to 8 behind one hidden-tab-aware poller; six toast
copies became one helper (12 of 12 before/after screenshots identical). The whole web layer still grew by 143 lines
that hour, from feature work. That is the point of tracking slope: cleanup has to outpace growth in the hot files,
and one hour showed it can. One lesson about the signals themselves: a name-pattern count (toast definitions) read 5
both before and after, because each page kept a small named lane on the shared helper. Count implementations, not
names.

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

### What the research says about intent judges (and what we changed)

A second digest (MiniMax M3.1 over about 30 sources, October 2026; figures as reported, not all re-checked) found
one structural rule above all: **the judge must open the real artifact, not read the transcript.**
- "Across 54 cycles a frontier agent claimed improvement every time, yet 56 percent had a measured delta of zero or
  below". The in-band judge "accepted cycles of which 44 percent were real-world regressions"
  ([arXiv 2607.25152](https://arxiv.org/abs/2607.25152)).
- Where intent *is* checkable from the artifact, that error fell to zero.
- 75.5% of failing runs claimed done.
- Committed agent loops in public repos almost never have stop conditions, budgets or verifiers
  (217 of 36,645 repos had loops; none had those, [arXiv 2608.21884](https://arxiv.org/abs/2608.21884)).
- For video, humans agree only 66.9% on pairwise preference ([arXiv 2605.03475](https://arxiv.org/abs/2605.03475)),
  so a judge's taste call on one clip is weak evidence. Numbers (duration, frames, a face match, the words spoken) are
  strong evidence.

What we built from it, the same hour:
1. **Default-fail evidence.** A judge's "met" counts only if it lists the real outputs it opened, and they exist.
2. **A fresh second judge confirms every "met"**, told to try to show it isn't. One lucky pass never ends a milestone.
3. **Anti-spin as a counter, not a judgment.** Three rounds with nothing new landed puts the mission in `blocked` for
   its lead (Devin: stop when "a round fixes nothing new").
4. **A non-progress exit and an attempt floor.** A plateau is not a stop; the judge must change approach (pstack).

### Ambition as a protocol (owner #338)

After 90 minutes the loop merged fast, but missions hadn't moved, and it was clear why. Builders did the literal
ticket ("silence a 404") and stopped at the edge of their scope. Judges proposed polish while the purpose was far off.

Ken Huang's "Your agent isn't lazy, it has no protocol" names this
([substack](https://kenhuangus.substack.com/p/your-agent-isnt-lazy-it-has-no-protocol); most of it is paywalled), on
top of [Felix Rieseberg's "How to be more ambitious: a tutorial for humans with models"](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/), which names four kinds of ambition (speed, altitude, depth, range) and credits Tom Kelley's nouns-into-verbs. The skill carries all four, plus his four-question depth check, beliefs checked against raw data, an outside check on the real output, durable workflows, and a crew of specialists with a red team. The model "optimizes for the literal request", and the literal request is
"your best guess, not your goal". The fix is ambition as rules the agent runs every time: "named rungs, forced
statements before acting, a defined judge." It has three moves:
- **altitude:** the goal beyond the goal;
- **depth:** what the field's best expert would do;
- **range:** a method from another field.

What we built from it:
- every brief makes the builder write ALTITUDE, DEPTH and RANGE before code, then deliver the ambitious version;
- if the right fix is outside its scope, the builder names it with a default instead of shrinking the job;
- every judge round starts with the single biggest step toward the purpose;
- judges see which GPUs are free, because run-bound missions had been waiting on one busy box while two others sat
  idle.

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
| 23:40 to 01:36 (areas, missions, restart-proof) | 54 | 28 | 9 | 7 | 3 | 17* | 73 (15) |

\* Inflated: before 00:14, a builder whose work a lead had already landed was counted as a silent death.

Two notes:
- The first 37 minutes of no-gate landing drained a backlog of finished branches, so 45/h is a peak, not a rate.
- All 9 land conflicts were in shared hub files: `docs/PHASED_ENGINE.md`, `finish/levers.py`, `stages/real.py`,
  `comfy.py`, `edl.py`, `creative.py`, `index.html`.

The first collision scan, at 00:14, found three live collisions, all in the web UI: three UI builders in `app.js`,
the shell and the pages.

One broken main so far: a stray character in `edl.py` landed through a merge at 23:48 and was fixed forward at 23:51.

**Incidents in the first hour of missions (and the fix):**
- **Queued jobs started 2-3 times.** The launcher ran `cd dir && nohup agent &`, which backgrounds a subshell. That
  subshell held the caller's output pipe open for the agent's whole life, so the queue's launch timed out before it
  could claim the job. Fix: claim the job before launching, and launch with `cd dir || exit; nohup agent &`, which
  returns in milliseconds.
- **A judge proposed jobs on another lead's live run** ("unstick a run"). They were stopped after 42 s with nothing
  committed. Fix: every judge prompt now carries standing constraints: never touch a running run; use a scratch copy.
- **A judge read an expected 404** (the app probing a dev-only endpoint) as a defect. The builder it sent found this in
  minutes and said so. Cost: one small job. Fixing forward absorbed the judge's mistake.
- **The loop worked end to end within the hour.** The UI judge looked at real screenshots, a builder fixed the phone
  form and tabs in a couple of minutes, and it landed on exit. The pre-viz builder found its fix needed a file outside
  its area and posted `blocked` with a default, as designed.

**The 01:10 crash (owner #334-337).** The desktop session ended. The user's service manager stopped, taking down
the terminal multiplexer and every agent, builder and design call started under it, plus the loop's own supervisor.
The loop was dead for 5 minutes, and tokens and time were lost. What we changed:
- Every agent and long job now runs in its own session (`setsid`), so the session that started it can die without
  taking it along.
- Every brief is saved to disk at launch. Two builders couldn't be resumed because their briefs lived only in `/tmp`.
- `resume_workers` runs when the terminal sessions are restored. It relaunches each killed builder once from its
  brief, told to continue from its commits. A builder that finished but never landed is landed instead. A lost design
  call is relaunched. The signal for "killed, not finished": the agent's log is empty, because `claude -p` writes its
  reply only at the end.
- A keeper restarts the supervisor within 30 s, with or without the service manager.
- Messages to leads are delivery-checked: the sender waits for an empty input box, confirms the message was taken,
  and retries.
- Run stages have time budgets. Over budget, or no progress row for 15 minutes, raises a stall to the run's lead at
  once (one run had sat 62 minutes in one stage with nobody acting).
- "Gate met = go": leads act on a met condition without waiting for the orchestrator.

**The first full reshape (01:28 to 01:55).**
- 01:28: two builders collided in the 3,272-line crew file.
- A split job was queued. Its first builder turned the file into an 8-module package behind a facade that keeps every
  name.
- Its land conflicted with main, because others kept changing the old file. A fresh builder merged main, re-applied
  main's newer changes inside the new modules, and landed it 26 minutes after the collision.
- The area map was then split along the modules (read, world, direct, cut; only the shared helpers stay a hub). Builders
  on different crew stages no longer touch the same files.

Two more pieces landed in the same window:
- **Self-healing conflicts.** A conflicted branch gets one fresh resolver that merges main keeping both sides' intent.
  The first one landed in 3 minutes.
- **A scope hook per worktree.** It refuses commits outside the builder's areas, which closed the "builder wandered
  into another area" collisions.

**After 5 hours (05:10): 175 merges (32 an hour), 197 cards moved (49 to done), and still no mission milestone met.**
What we learned about why, in order:
1. **Missions wait on GPUs.** Run-bound jobs blocked behind a production run. Fix: judges see which machines are free.
   "Production first" pauses mission scratch runs on the RTX while a production run is live, and resumes them after.
2. **The loop's own blind spots looked like spinning.** The judge's look only read the newest live run, so it couldn't
   see scratch work. A long-running scratch runner counted as a busy builder. A progress counter ignored jobs that
   landed outside the mission's areas. Each fix took minutes once the bug was named.
3. **Two copies of one decision.** The UI showed two different "next actions" because two files computed one. Jobs
   fixed one side each round. Fix: one job owning both files, one shared function.
4. **Judges move the goalposts.** Milestone 1 ("one clear next action") silently grew to include milestone 2 ("the
   season as pictures"), so it could never be met in 24 rounds. Fix: judge only the current milestone's own words, and
   keep later gaps for later milestones.

**06:15: 193 merges (29 an hour), still no milestone met.** The UI mission is on round 30; its rounds now agree on the
one next action at both screen sizes and are down to one contradiction on one page. Two more blind spots, found by
reading why the pre-viz mission and the episode mission had no judge round for 70 minutes:
5. **Unowned files block builders.** Five page folders (the project page among them) were in no area, so three UI
   builders in a row stopped with "outside my scope". Fix: every file the app serves now has an owner.
6. **A finished agent can still look alive.** A builder wrote its final reply at 05:15, but its `claude -p` process
   kept waiting on a background shell it had started. It held two areas for an hour, which starved the pre-viz mission's job and
   kept the episode mission's judge from running. Fix: a builder whose reply is written has ended, whatever its pid says. A
   second bug showed up as soon as that was fixed: two queued jobs on the same area started in the same tick, because
   the held set wasn't updated after the first launch.

**07:00: the first milestone met.** The pre-viz mission's p0 (a run folder makes an ep01 cut and animatic of real takes, read
back by run id). Three independent judges had said "met" since 06:37, and the loop threw each one out. Judges write
an opened file as "path (how I looked)", and the evidence check tested the whole string as a path. Fix: the first
word is the path. A contact sheet of the 145 s cut showed real cast takes with captions from start to end.
7. **Holding a resource is not using it.** "Production first" paused seven mission scratch runs from 04:16 while a
   production run counted as live. By 06:59 the RTX was at 0 % with 122 production jobs queued. Fix: an RTX idle 10
   min releases the held runs for 30 min, and run-ops is told production isn't feeding the GPU.

8. **"Newest" is not "best".** The episode mission's judge went from a 189 s cut with 183 s real (round 20) to a fresh run's
   2-of-24-shot cut (rounds 21-22), only because it was newer, and queued jobs to fix the fresh run. Fix: judge the
   best output toward the milestone, name it, and say if a newer one passed it.

9. **Scope blocks were the most common stop: 51 by 07:50.** Judges assigned areas by guessing from names, builders
   found the code elsewhere, and each one stopped "outside my scope" and waited for a person or a later round. Fix,
   two parts: (a) judges list the files a job edits, and the files' areas are added; (b) a builder that still blocks
   on scope is re-briefed once with the areas of the files it named, and queued. The queue still keeps two builders
   out of one area.

10. **Builders stop on decisions they already have defaults for.** One builder wrote six decisions, each with a
    sound default (a character's sample as a draft, voices on the idle Spark), then stopped. Fix: the brief now says a
    decision with a default that can be undone is not a block: take it, mark it "draft, owner may swap", and keep
    going. The owner gets one decision line with the default already under way. The same hour the scope self-heal
    fired on its own (p-audience-input re-briefed with crew-cut added).

**08:05: two milestones met.** The UI mission m1 (Home and project pages clean and usable at phone and desktop width,
one obvious next action) was met at round 42, 20 minutes after the scope self-heal and an hour after the goalpost
fix. Loop numbers: since 2026-10-18 23:40: 257 merges (30.5/h), 28 land conflicts, 0 did not start, 64 area collisions, 9 stalls, 20 silent deaths, 156 queue starts, 252 cards moved (65 to done).

11. **A rule in a prompt is a suggestion; a rule in the code is a rule.** The judges' constraints said "a fresh run
    it starts itself", and a mission builder started a run inside the production project, beside the live production run. That run's
    shoot sat unqueued and the RTX was idle about an hour (the orchestrator). Fix: every agent job carries `H3_AGENT_JOB`, and the
    engine refuses to make, start, resume or pause a run in the production root for it, naming the way out (a
    scratch root). The constraint text changed too, but the refusal is what holds.

12. **A spin can hide in new words.** The UI mission m2 hit "the test project shows no episode rows" in five rounds in a row. Each
    judge worded it anew (similarity 0.2 to 0.76), so the same-gap check never fired, and each round queued another
    patch job. Fix: every 5th unmet round on one milestone counts as a spin. The spin prompt shows the last five
    gaps side by side and asks for one job that first traces the root cause in the running system.

13. **Finished work that never lands is the quietest failure.** The check for "a land is already running" matched any
    process whose command line mentioned land.sh. A builder hanging after its reply has its brief on its command line,
    and the brief names land.sh and the builder's own worktree. Autopilot marked that head as handled and never came
    back to it. Fourteen finished builders sat unlanded, among them the ep01 voice work the episode mission was waiting for.
    Fix: count only processes running land.sh, and recheck a skipped head. A scan of finished-but-unlanded branches
    found the 14.
14. **A deploy is part of a merge.** The dashboard kept serving old web code after a web merge until the orchestrator restarted it
    (the orchestrator). land.sh now restarts it after any merge that touches the web code, and says so in the inbox.

15. **The model's own limits are an outage the loop must ride out.** From 10:56 to 12:37 every judge died on the
    Claude session limit within a minute. The loop relaunched each one 10 minutes later, about 30 wasted rounds, and
    builders started then died too. Fix: a judge that dies on a usage limit makes its mission wait 15 minutes, and
    the round isn't counted.
16. **Every wait needs the same "is it really alive?" rule.** land.sh waited on the newest row for a worktree, and
    that row was a 10-hour scratch runner, so four lands sat for 2 to 10 hours. Fix: land.sh waits only on a
    builder, and not past its written reply. The same bug had been fixed in autopilot three hours earlier. The rule
    lives in each script that waits, so each one has to get it.

**13:05: three milestones met** (the pre-viz mission p0, the UI mission m1 and m2). The 14 stranded branches are all handled:
4 merged, 6 already in main, 3 conflicts sent to the resolver, plus the voice work.

17. **Throwaway copies are a resource leak a fast loop turns into an outage.** At about 30 merges an hour, every job
    made a worktree, often a scratch run (~10 GB), and a land copy. `/` hit 0 bytes: 485 GB of scratch, 221 GB of
    worktrees, 152 GB of failed land copies (owner #405/406). Fix:
    - everything agents make lives on the 24 TB data disk: worktrees symlinked, scratch, TMPDIR, pytest temp, land copies;
    - the engine refuses agent scratch and runs anywhere else;
    - an hourly job moves merged worktrees and old scratch to an archive, never deleting;
    - the watchdog alerts below 200 GB free.
    A self-healing loop needs garbage collection as much as it needs retries.
18. **Resource rules belong in one runtime file every router reads.** "Route nothing to two named GPU boxes" (owner #392)
    touched the engine's render targets, fallback cards, draft boxes and voice workers, plus autopilot's GPU watch
    and the judges' GPU list. All of them now read one shared "boxes off" file at every call, so the box's owner
    hands it back by editing one file, with no merge.
19. **Failover has to be rehearsed on a real pane.** Account failover (owner #394) keeps each lead's transcript and
    flags. Its first trial found that pointing `CLAUDE_CONFIG_DIR` at the default dir makes Claude Code start as a
    fresh install, and that a new account must trust each lead's folder once. Neither was in the docs.

20. **A retry must be keyed on the state it retries, not on its own output.** The conflict re-land was keyed on the
    inbox line it reacted to, and every re-land wrote a new line. Two watchers (autopilot and the watchdog) each
    re-landed, and by 13:55 there were 36 duplicate lands of three dead branches on the merge lock. Every real merge
    waited 12 to 22 minutes behind them. Fix: re-land once per branch head, and land.sh refuses a second copy for
    one worktree. Self-healing loops need idempotence keys, or the healer becomes the outage.

21. **"Blocked, the lead decides" is a silent wait unless the lead hears it.** The UI mission blocked at 13:53 during the
    merge jam. The line went only to the inbox, and a lead never saw it, so the mission sat for 45 minutes. Fix: the
    block goes to the lead's pane with delivery checked, and a blocked mission whose own jobs land afterwards resumes
    itself. The block was the pipe, not the goal.

22. **Sequences need a hand-off, not a person.** A17's UI rounds sat idle after each landing (R1 13:45, R2 14:57)
    until the orchestrator pushed. Fix: a chain file lists the rounds, and autopilot starts the next the moment the previous
    lands. With no brief written, it tells the lead where to write one, and starts the moment the file exists. The
    first version started a second R3 beside the one the lead had just launched, in another worktree. Rounds are now
    matched by name, and a hand-started one is followed, not doubled.

**16:15: four milestones met.** The UI mission m3 (the Cut page shows the real cut with hit notes on the cut's own
seconds) was met at round 89. The UI mission is 3 of 5, the pre-viz mission is 1 of 5 (its judge split p1 into smaller steps), and
the episode mission is 0 of 3: ep01 still lacks its spoken lines end to end. Loop numbers: since 2026-10-18 23:40: 450 merges (27.1/h), 309 land conflicts, 0 did not start, 67 area collisions, 12 stalls, 22 silent deaths, 301 queue starts, 405 cards moved (114 to done).

23. **Every pause needs an end that doesn't depend on someone remembering.** A manual hold on a run's visualise
    stage outlived the watcher meant to release it, and the run sat idle (the orchestrator). Fix: a hold carries an expiry
    (default 20 min), the runner releases expired holds and logs it, and the watchdog posts any hold over 10 min on a
    live run. The same goes for leases, locks and reservations: they all need a timeout plus an alarm.

**19:46: seven milestones met.** In the last three hours:
- The UI mission m4 (one-tap steer) was met. The UI mission is 4 of 5, now on m5 (premium).
- The pre-viz mission p1a (boards) was met. The pre-viz mission is 2 of 5.
- The episode mission h1 (ep01 plays end to end, lines spoken, consistent faces) was met. That's its first milestone, after
  about 75 rounds; the last gaps were the voice routing and the S24 face check.

Loop numbers: since 2026-10-18 23:40: 515 merges (25.6/h), 310 land conflicts, 0 did not start, 67 area collisions, 12 stalls, 22 silent deaths, 342 queue starts, 446 cards moved (130 to done).

24. **Agents block on beliefs, so give them the checks, not just the rules.** The pre-viz mission's ep01-only run never
    started. Its builder waited for "owner OK for the paid read and World calls", which are Claude subscription calls,
    and for "the voice-research hold on two draft boxes", which wasn't active. Each rule was right; the builder's facts
    were wrong. Fix: every brief names the one command that checks each fact (what counts as paid, box_hold.sh
    status, the free-cards list), and the loops lead queued the run with the facts in its brief.

25. **A loose goal plus an autonomous loop will optimise the wrong thing in plain sight.** The UI mission's last milestone
    said "looks premium and genre-aware". Over 15 rounds its judges and builders repainted the approved interface:
    rose background, italic serif title, heavy outlines. The owner called it terrible (owner #429). The loop did
    exactly what the words allowed. Fix: some areas are taste, not tasks. The look belongs to the orchestrator's reviewed UI
    rounds; mission jobs are marked no-visual, and the commit hook refuses stylesheets and fonts. Self-direction needs
    fenced areas where only a person decides.

26. **"Only a user can retry" is a stop the user never hears about.** The engine blocks a failed job's key until a
    user retries it. That's sensible for production, but nobody is told. A run sat after a drain cancelled its jobs,
    and another run's one-hour test sat 25 min after one lookbook failure, with every card stale and the Spark idle. Fix: the
    watchdog catches a run that stopped on a failed or cancelled job. A mission scratch run is retried once per
    failed job; a production run goes to its lead with the exact retry command.

27. **Failover state lives where the work started, not where the process runs now.** After the switch to account b,
    every resumed lead kept writing its transcript under account a's folder. A map that looked only in the pane's
    current folder found nothing, and the next switch would have skipped six leads. The first switch also showed the
    other trap: `/exit` can raise a dialog (feedback, "stop background tasks"). Fix: look in both folders. Never type
    into a pane with background shells or child jobs. Dismiss the feedback prompt; cancel any other dialog and skip
    the pane with the reason. A switch must leave every pane either moved or untouched, never half-exited.

28. **A slow step in the loop holds every job behind it, so time each step.** One autopilot pass took 11 minutes, and
    a UI round sat queued behind areas whose round had already merged. Timing each step showed the cause:
    `drive_missions` took 253 s because starting a judge round ran the mission's look command (up to 10 min) inside
    the pass. Fix: round starts run on their own, with the mission's own lock, and any step over 60 s is logged. The
    same check found two autopilot loops running at once (keeper plus service); a lock file now allows one.
29. **Agents name a safe default and then stop anyway.** Three rounds each wrote "Default: ...",
    undoable and scratch-only, and posted it as a block. A rule in the brief was not enough. Fix: the block command
    itself (event.sh) turns any block that names a default into `[decided]` and tells the builder to take it and go
    on. Two more versions of the same stop got rules in the brief: a busy box is a queue, not a block, and an
    hours-long run is started detached and read by the next round, not fitted inside the builder's timebox.
30. **An owner decision has to reach the judge, or the loop re-asks it every round.** The owner emptied the starter
    music on purpose. The judge issued "starter music" jobs twice, and both blocked on the missing tracks. Fix: the
    decision went into the mission's constraints (no music; sound carries the beats until tracks exist), which the
    judge reads every round.

31. **Order rules written as waits deadlock; write them as priorities.** "B waits for A" stops B forever when A cannot
    start. Write it as "A goes first when it can run; otherwise B runs". A queued shoot that could not start once held every image job behind
    it, though there was nothing for them to wait for.
32. **Never hold one resource while waiting for another.** A first draft was classed as GPU work for the whole job,
    so it held the GPU window through its CPU steps, and the work behind it waited. Fix: one owner per GPU, a queue per card,
    and leases with heartbeats, so a holder that stops renewing loses the card.
33. **Leave memory to its owner.** Estimating free VRAM from outside the image server
    is a guess, and the scheduler acted on the guess. The image server manages its own resident models; let it, and read
    only what it reports.
34. **An idle resource with runnable work is a bug.** That calls for a watcher that corrects it, not a gate. When a card
    sits idle while jobs are queued, the loop says why, and something corrective runs: it frees a stale hold, reroutes,
    or restarts a stuck service.
35. **No gates (#481, #507, #514).** Replace every gate with flow and notes. A check that stops work becomes a note that
    travels with the work, and the next round reads it. We audited the briefs, launchers, landing script, scheduler and
    standing orders and removed every gate. Where a gate is found later, it is removed, not tuned.
36. **Every patch adds a part, and pairs of parts interact.** Scheduler fixes piled up: each was right alone, and two
    of them together deadlocked. Before changing the scheduler, replay real run histories in a simulator and look at
    idle time and deadlocks across the whole history, not at the one case the patch was for.
37. **A merged fix for the live run goes into the live run at once, and services restart onto new code.** The rule is
    two minutes from merge to the live run. Long-running supervisors load their code once, and one kept enforcing a
    lock rule that main had already changed, blocking the live run. Fix: the watchdog restarts any supervisor whose
    loaded revision is behind main, and stops a leftover old one. A run left "running" for days beside the live run
    is posted for retirement after 24 hours, and its queue never goes ahead of the live run's.
38. **An account switch must cover background services, not only sessions.** Switching the interactive sessions to a
    second account left the schedulers and watchers on the first, still spending its limit. The switch now rewrites
    one environment file that every service reads and restarts the services.
39. **A default that limits is a visible per-run setting, never a silent rule (#512).** "One machine per roll" was a
    hidden default, and it looked like a slow pipeline. Now each run lists its machines at start, and a run without
    the setting says so.
40. **Inherit, don't invent.** When each prompt layer writes its own camera and lighting words, the layers drift
    apart. Every layer now derives from one source per scene and shot: one camera spec and one lighting
    sentence, copied down, not rewritten.

41. **Tell stale from important by owner and progress, never by location alone.** A cleanup stopped dozens of
    "orphaned" scratch runners by path. At least one belonged to a builder that was still working. Ask what the thing
    is, who owns it and whether they are still here, and whether it is moving. Stop it only when it clearly belongs to
    no one's live work, and say what you stopped. When unsure, flag it. The root fix: scratch runners end with the
    builder that started them.

42. **Measure before fixing again.** A speed milestone stayed unmet for ten rounds while fixes merged, because none of
    them was measured end to end. The judge now asks for one timed run before any further fix.
43. **A goal the loop can't satisfy has to be restated.** "Watched by ear" read as "a person must watch", so no round
    could meet it. Restate it in checkable terms as a default, and keep the owner's review after the fact, not as a
    gate.
44. **A fence an agent can override needs a watcher.** A builder pointed its test run at the production card by hand.
    The watchdog's production-first check missed it because the runner had no machine flag, so the gap was closed.
45. **When you change a signal, move its readers with it.** Blocks that named a default began posting as decisions,
    which was right, but the self-heal that re-briefs out-of-area stops only read blocks. For an afternoon, 25 such
    stops parked instead of healing.
46. **Quiet with nothing open is finished.** A watcher that keys on silence alone flags finished work as stuck, and
    one that resumes everything it held revives ownerless experiments. Ask what is open and who still owns it.
47. **The owner's inbox is for what changes what someone does.** Routine success (a restart onto new code) belongs in
    the log; three routine lines every ten minutes buries the one that matters.
48. **Reproduce on the real thing, as it really runs.** Two profiles of an idle process on a trimmed copy found nothing;
    the full copy with the real pinned code showed 16 s of work per 2 s tick. The trim removed the cost.
49. **The same failure twice is the code, not luck.** A retry that hits the same reason gets no further; find the fix
    (often already merged) and move the work onto it.
50. **A fence guards a resource, not one door to it.** Hiding the GPU from one API left another path open.
51. **Self-heal checks for a live sibling.** Restarting quit work without asking who already took it over doubles it.
52. **Idle has a cost; measure it.** Processes re-reading their history every tick taxed every real job on the machine.
53. **Give cheap agents the facts they would otherwise go and search for**, and say what not to do and why.
54. **Count only what someone is waiting on.** An idle-GPU alert counted every queued job on disk and labelled it
    owner work; the 243 jobs were two research copies nobody had served for two days. A signal that counts the
    unowned trains everyone to ignore it.
55. **Two tools on one thing share one lock.** A cleanup that told git to forget missing worktrees ran while a mover
    had one worktree in flight, and it lost its git record (re-attached; no edits lost). Movers and pruners now take
    the same lock.
56. **A superseded run competes with its replacement.** An old timed run, its builder gone, held a render card for
    an hour without progress while the current timed run waited hours for that card. Stopping the old one is the
    fastest speed-up available; check owner and progress first, then stop it and say so.
57. **A delete is the owner's: gather it, size it, remind them.** Old merged worktrees go into one folder on the same
    disk (an instant move), with an index, one copy-paste delete command, and a weekly reminder. The system frees
    the decision; the owner frees the disk.
58. **Report the number that didn't move.** Moving active worktrees off the busy disk took it from 95.5 % to 93 %
    busy: renders were the load. Saying so points the next fix at the real cost.
59. **A pointer in the environment travels to everything spawned under it.** Agents were pointed at a lab box so
    their checks stayed off the main card; every run and runner they started inherited the pointer, so real work kept
    landing on the slow boxes. Fix by construction: the place that starts run work decides the machine, drops the
    inherited pointer, and says so; the lab boxes stay for tests.
60. **Guard the write, not the door.** A UI check reached the live data through a path nobody fenced. The guard
    belongs where every path meets (the queue write), keyed on who is asking, and it answers with the right place to
    go instead.
61. **A cleanup check must recognise every shape of the thing.** Runners started through a second launch form were
    invisible to the orphan check and respawned for seven hours. When something survives a cleanup, look at how it
    was started.
62. **Goals evolve; keep the path versioned.** The owner's intent sharpens as work lands. Judges read the owner's
    newest words each round and may add, split, reword, replace or call a milestone good enough for now, with the why
    and its source kept beside the old list, so the path can move without losing how it got there.
63. **What a process starts, it stops.** Test helpers left encoders and job runners alive after the builder ended,
    and load reached 72. Give children a process group and a timeout at the source, and a sweep for leftovers.
64. **A rank means something only inside the queue that made it.** A timed run was kept off the card because an
    admission cap compared its job ranks with another project's, which were numbered in another catalog. Give every
    cross-boundary comparison a shared first key (the run's class), or it orders by accident.
65. **Mark at the moment it becomes true, not once at start.** A timed runner marked its runs when it started; the run
    it served began a minute later and was never marked. A state that can arrive later is checked each tick.
66. **A delivery check that reads the screen must know how the screen shortens things.** A long message shows as a
    collapsed placeholder, so a check for its words failed every time and the message was resent every minute for half
    an hour. Check the effect (the input box emptied) rather than the echo.
67. **A hang looks like silence on every meter at once.** A video loader deadlocked with the card idle and the lock
    held for 20 min, and nothing flagged it. The watch is the conjunction: one call for 10 min, card idle, lock held;
    then escalate in steps (interrupt, restart, retry the job) and say each one.
68. **Count implementations, not names.** A cleanup folded six toast copies into one helper and the name count read
    the same before and after. Measure the thing the cleanup removes.
69. **A rule enforced by the asker's own code fails while older code is running.** A card window held new takers
    back, but a runner started on older code never checked it and took the card in turns. Enforce at a point every
    version passes (the start of the thing, a shared lock) and keep an outside sweep that acts whatever code is running.
70. **A sweep reacts; a guard at the door prevents.** A once-a-minute pause let a runner that started and claimed inside
    that minute take the card first. Refuse at start, and keep the sweep as the backstop.
71. **Your own automation must respect the owner's live work.** A routine "restart onto new code" restarted the
    owner's live roll; nobody had told it about the rule "never restart the roll". Every self-healing action asks the
    same stale-vs-important question a person would.
72. **A service that starts work in the background and returns can kill that work on exit.** A timer-started board
    pass died at birth every hour for four hours, because the service manager cleaned up the unit's processes when its
    start command returned. A job that must outlive its starter says so in how it is run.
73. **A declared output must be read where the worker writes it.** Two reports written to a path relative to the
    worker's folder were read as absolute, called missing, and their readers rerun. Resolve paths the way the worker
    would.
74. **A new rule meets the old ones.** "Agent run work goes to the main card" and "only the owner's roll on the main
    card while it runs" were each right; together they moved a lab run onto the card mid-roll, because the first ran
    after the second had cleared it. When you add a rule, find the rules it overlaps and decide which wins, in code.
75. **A hold must not wait on what it holds.** A hold "until the episode's cut" blocked the items the cut needed, so
    the cut could never come. Before a hold, ask what its release depends on.
76. **A waiting job must not hold capacity.** Every render slot was taken by jobs that were themselves waiting for the
    card, so the work the card needed could not be claimed. Count waiting and working separately.
77. **One state, one owner.** Two watchers both paused and resumed the same runs; one resumed what the other still
    needed held. Hand state over explicitly instead of letting two loops act on it.
78. **Check before spending, not after.** Renders whose inputs had changed ran four minutes each and only then failed
    their freshness check. A cheap check belongs at claim time, before the expensive work.
79. **A real need without a door goes around the fence.** A builder that had to time something on the main card had
    no sanctioned way in, so it posted straight to the renderer in a loop while the guard stopped each attempt. Give
    the need a door (a wrapper that takes the lock), then the fence holds.
80. **Stopping a worker must take back what it sent.** A stopped job's request kept rendering on the card outside every
    lock. A worker withdraws its own queued and running requests on the way out, and a sweep catches the ones whose
    worker is already gone.
81. **The writer and the reader of a contract must agree on its shape.** A guard looked for a JSON window file; the
    orchestrator wrote YAML under another name, and the guard would have refused the very job the window was for. Read
    the file the other side actually writes, in every format it uses.
82. **Reverse a wrong rule cleanly.** "Run work goes to the main card" moved lab work onto it; the owner's rule was the
    opposite. Turn the rule around in code and in the briefs at once, and say plainly that it replaces the old one.
83. **A checklist is not a ladder.** A readiness list judged one item at a time sat on item one for seven rounds while
    others' work had already met half of it. When milestones are independent, check them all each round and work only
    on the open ones.
84. **A long-lived process runs the code it loaded.** The loop that applied judges' verdicts had loaded its rules nine
    hours earlier, so new rules reached the judges' prompts but never the code that acted on their answers. A
    long-lived worker reloads its rules when they change, or is restarted with them.
85. **"List what is left" erases what is done.** Judges told to send back only the unfinished items dropped each one
    they met, and a checklist of eight showed five with nothing done. Keep finished items in the record; send changes,
    not the remainder.
86. **A citation must be about the claim.** A judge marked one item met citing a real owner message about another. A
    check that the source exists is not a check that it says what is claimed; quote the source beside the claim.
87. **A copy inherits its source's state; decide what it keeps.** Scratch copies carried their source's holds (they sat
    queued forever), its closed status and its code pin. When you copy work, say which state comes along.
88. **A per-worker file must not live in a shared place.** Every branch edited one report file at the repository's
    root, and almost every merge conflicted on it. Per-worker records live per worker, or merge with a fixed rule.
89. **The rules you give the agents bind you too.** The orchestrator searched the busy disk it had told every agent
    never to search. Run your own commands past your own standing orders.
90. **A hold is checked at every door, not only the new one.** A box held for an install was skipped by the router
    that spreads work, but a run pinned to that box by name went straight there and failed. A rule about where work
    may run is checked where every job is claimed, for every way of naming the place.
91. **A failure must show its cause, not its last words.** Failed jobs still showed their last progress line ("waiting
    for the card"), so a person read a content check's failure as a wait that had failed. When work fails, its status
    line becomes the reason.
92. **A default that undoes a person's choice must say who undid it.** A 20-minute default expiry released a person's
    hold, and later work ran that the hold was there to stop; nobody could tell what had cleared it. Size defaults to
    how people use them, and log every change to shared state with who or what made it.
93. **A sensor that skips what it cannot measure is blind there.** The watch for readers that die without their report
    only looked at jobs that named an output file; one that named none died on a rate limit and nobody noticed for
    half an hour. When a sensor can't check a case, it still watches for the failures it can see.
94. **Back off on the same tool; switch tools only out loud.** A rate-limited reader is tried again on the same model
    every few minutes, with one line saying so; moving it to another model is a visible decision, never a silent
    fallback.
95. **Idle is a state to act on.** The main card kept tens of GB of models loaded with both queues empty. A watcher
    frees resources after a quiet stretch with nothing holding them; the next job loads what it needs.
96. **Check the reported cause before building its fix.** The orchestrator asked three times that "waits never fail";
    the failed jobs' reason field said a content check failed, and the same two items failed after every requeue.
    Read the record first; the same item failing the same way after each retry is not a wait.
97. **A fixed-size list drops the urgent item.** The board covered a fixed list of ten missions, and the one blocking
    the main goal was not on it. Build the list from the priority source, urgent first, and never cap away the urgent.
98. **Ending a state clears its fields.** Two missions ran for hours with pause fields still set, so every reader
    called them paused. The step that leaves a state moves its fields to history, in the same write.
99. **Hand cleanup that repeats becomes the system's.** A lead moved paused scratch folders off the full disk by hand,
    leaving a pointer and a log row each. The same rule, keep list included, now runs every hour.
100. **Edit a hand-written file as text.** Re-serialising a status file to reorder it would have restyled every row
    the leads wrote. Move blocks as they are; generate only what is new, and check it still parses before writing.
101. **A choice made once goes stale while the work waits.** Work was sent to a machine when it was claimed and then
    waited there for hours while a faster one sat idle. Where work waits is decided again while it waits.
102. **A count from one partition misreads a shared resource.** Each workspace counted only its own jobs at a shared
    card, so a card with ninety waiters from elsewhere looked as free as an idle one. Measure the shared thing at the
    shared place.
103. **Two names for one thing split a queue.** One machine had two names; jobs queued under one were never claimed
    by the worker that answered to the other, and nothing said why. Normalise names where work enters.
104. **Every fence must honour the deliberate opening.** The orchestrator opened a window to use an idle machine; one
    rule honoured it, another older rule moved the work away anyway. When you open an exception, find every rule that
    guards the same door.
105. **An exception must survive the hand-off.** A worker restarted itself on older pinned code, which ran the old
    rule again and undid the exception. Carry the decision with the work, and close it when its reason ends.
106. **A service outlives the worker that started it.** A builder's dev server ran day-old code for a day after the
    builder ended, and a roll was about to rely on it. Give such services an owner, and restart them when their code
    changes.
107. **Fixed in the file is not fixed in the process.** A watchdog loaded its code once and ran it for ten hours; six
    checks added in that time never ran, though each was reported done. A long-running loop reloads itself when its
    code changes, and "done" means the running process has the change.
108. **Watch a new sensor fire once.** A check meant to stop workers when a window closed matched a word their command
    line never contained, so it was silent, and silence looked like nothing to do. Make it act once on a real case
    before calling it live.
109. **Ask what the work targets, not what the text mentions.** A watch flagged two missions every round for working
    on a closed run, because an old task name in a list that only grows mentioned it. Read the targets of the live
    work; text that only accumulates will match forever.
110. **A stack of patches means the fix is below the cause.** One night's placement rule grew four parts: decided
    once at start, an exception passed through a restart, a carried flag, and a sweeper that stopped workers when the
    exception ended. Each fixed the one before. The decision belonged at the moment work is claimed, read fresh each
    time; there it is one rule, and the other three go away. (Owner: every fix to the core cause, said in the note.)
111. **Alive is not acting.** A queue's head was alive and beating, so every liveness check passed, yet it never
    took its turn: it ran older code that did not see itself as head. Judge a turn by whether it is taken, and let the
    shared record end a turn that is not.
112. **One job, one process.** A job was set back to queued while its process still ran, so a second process ran it
    too; both wrote one file and the first read the other's half. Tie the job to its process at the place it runs, so a
    twin waits instead of starting.
113. **One name, one meaning in a scope.** An imported function and a local list shared a name in one function, so
    every run that reached the call failed. Name each thing once where it is used.
114. **Read the record under the name the code uses.** A lock file named after one numbering was read as another box,
    and the diagnosis went to the wrong machine. Resolve names through the code's own mapping before reading.
115. **Coming back by itself is a list you can check.** A restore map that read the wrong folder, a boot unit left
    off, and flags copied in three places would each have kept the crew down after a reboot. One launch script for
    the flags, the map regenerated with what comes back, and a dry run that prints every command.
116. **A rule only acts where its code runs.** A queue rule landed in new code, but every process on one card ran
    older code, so nothing applied it and the card stalled three more times. Put the rule in the data every version
    already reads, and give it one caller on current code.
117. **A message through a dead messenger never arrives.** Cancels reached a job only through the runner that
    started it; a job whose runner died waited for five hours with its row cancelled. Let each process read its own
    record where it already looks, instead of trusting a relay.
118. **Decide what a thing is by its own claim, not by where it stands.** A check counted any agent in a folder as a
    builder and blocked a status refresh because a lead worked there. Use the claim the thing makes itself (a lock it
    holds), and leave shared places out.
119. **Fix the class, not the instance you were shown.** A first fix let waits requeue; two more stale reasons still
    failed the next hour. A stale result means the world moved: every kind is a redo, and only the same reason
    repeating is a loop.
120. **Idle is a live fact, not a declared state.** Cleanup waited for runs to be marked paused, so idle roots whose
    runs still said running filled the disk. Read the facts that show use (processes, briefs, queued jobs, newest
    file) and act on those.
121. **What serves the work must match how the work is placed.** Jobs were spread across three boxes, but each worker
    served one box label and only one worker per project was allowed, so two free boxes sat idle beside queued work.
    Let one server take everything its work lists, and count limits per box.
122. **Read a measure the way the hardware means it.** On shared-memory machines the card's own free figure left out
    memory the system could reclaim, so every large step waited with most of the memory free. Ask the machine what it
    is (its own name), not a size that happens to match another kind.
123. **A copy should not inherit a decision about the original.** Copies of a paused run were born paused and did
    nothing. A copy exists to be run: reset what was a choice about its source, and say so in the copy's record.
124. **Share instead of duplicating, and prove the original untouched.** Copies duplicated read-only media, about a
    gigabyte each, many times an hour. Link what is never rewritten, make writers replace a file instead of writing
    through it, then hash the original before and after a real run.
125. **An idle loop is a hidden fan.** Dozens of idle workers re-read unchanged files every two seconds and kept the
    machine loud. Re-read only what changed, sleep longer while nothing changes, wake on a change, and exit when there
    is nothing left to do.
126. **A safety proof covers only the writers it ran.** Copies shared the original's files through links, proven safe
    by hashing the original around a real run of the engine. A builder's own shell command then wrote through a link
    and broke three of the original's pictures. Prove sharing against every writer that can touch the copy, or do not
    share what anyone can write.
127. **Two forms of one fact never compare equal.** A record wrote a full hash and the check compared it with a
    shortened one, so every item that held one looped as "changed". When two places record the same fact, make them
    one function or compare them in one form.
128. **A step must not record its own product as its input.** A stage recorded a derived file as an input, then
    rewrote that file from its own output, so it always looked stale and re-ran. Record what a derived file is built
    from, never the file itself.
129. **Measure where the bytes go before naming the culprit.** The obvious suspect (agent transcripts and caches) came
    to under one gigabyte an hour; the code checkouts made per pin were seventeen. Per-source numbers first, then the
    fix where most of them are.
130. **A failure nobody retries is a stale page.** A judge that hit its limit left the status page stale for over an
    hour, because only the next hourly run would try again. A failed step says so and tries again soon, not at the
    next scheduled slot.
131. **A breaker must not lean on what the stall breaks.** A rule that moved a stuck queue head needed the lock to be
    free and the same head for thirty seconds; the stalls held the lock and flipped the head, so it never fired, three
    times. Key a breaker on how stuck looks from outside: the card free, work waiting, nothing taken.
132. **Check the premise in the data before you build.** A board was said to hold the card through its CPU steps; its
    holds were in fact all render time, and the idle GPU was model loading inside the renderer. The fix that was ready
    would have gained nothing, so it was not landed.
133. **A request in prose is invisible to the machine.** A builder wrote "do not land this yet" in its notes and was
    landed within the hour. Give the one field the lander reads, and tell every brief about it.
134. **Put priority on the work, not on the queue.** Test jobs ran at the production roll's CPU priority and twenty two
    of them slowed it; running every test job a step lower lets the operating system serve production first, with
    nothing new to run.
135. **A rule tuned for heavy work can starve light work.** A grace that keeps a card on its loaded model, to save
    minutes of reloading, kept it on a light voice model whose short calls kept renewing it while heavy jobs waited. Say
    which work a rule is for.
136. **Judge "made" by the result, not by the job.** A switch that turns a run's redos into review notes counted any
    item whose job had run as made. Items whose outputs grew after they ran (new looks named later) were noted
    instead of made, and the roll drew no boards for an hour. A first make is never a redo, whoever ran before.
137. **What you stop remaking, everything after it must accept.** The same switch kept a stale upstream step as it was,
    but every later step still waited for a current one, so nothing downstream could ever start. When you stop a
    redo, change the readiness rule in the same change: a made item counts as done for what follows.
138. **Dry-run the exact code that will run.** A two-part fix was applied to a live run with one part left out. A
    read-only planner pass of that exact commit on the live state showed six items still skipped, minutes before the
    run went idle on them. Prove the commit that is pinned, on the state that is live.
139. **A test copy at new code is a different run.** A copy pinned to the newest code restaled its whole world and
    started redoing it, and marking the stopped work "failed" made the planner retry it. Copy at the source's own pin
    plus your commits, and stop work as cancelled, the state the planner leaves alone.
140. **A check must not carry what it hides.** A public repository's leak check held the private words it refused, in
    plain text. Keep the list outside the repository, and fail closed when it is missing.
141. **A code repository holds code: megabytes, not gigabytes.** Agents saved their evidence (boards, strips, clips,
    logs) beside their notes and committed it. Nothing refused it, so a repository of 12-30 MB of source grew to 1.7 GB
    of tracked media and a 1.5 GB history. Every one of hundreds of worktrees, every land copy and every release
    checkout carried it, so each new worktree wrote 150 MB or more to the SSD, every repack rewrote the history, and
    clones slowed to minutes. The fix pattern has three parts. Ignore media at setup, with an allow-list for the few
    assets the code serves. Move evidence to a data drive automatically when work lands, and leave a link at the same
    path so notes still open. Add a size and tracked-media check to the doctor. Then rewrite the history once, with a
    mirror kept as an object alternate so every old commit still resolves.
142. **A history rewrite moves more than branches.** The rewrite also moved the detached HEAD of every release checkout
    to its new commit, so a release folder named for its old commit read as foreign and was set aside and checked out
    again. Before a rewrite, list everything that names a commit (releases, pins, worktrees); after it, check each one
    still matches.
143. **Idle means done, not quiet.** A prune treated a worktree with no live process as idle; one held a finished
    builder's branch that had not landed yet. Its registration was moved, and its land failed. Judge idle by the work's
    state (landed or not), not by whether a process is running.
144. **A move across disks is a copy.** Moving a folder to another disk copies it first, and a cleaner running at the
    same moment removed the half-made copy. Copy, check the copy, and only then set the source aside.
145. **Every run ends with a retrospective, and the next run starts from it.** Fixes made during a run were scattered
    across chat and notes, so the next run met the same causes again. Write the retrospective in the repository the next
    run's prep reads. It covers:
    - the result against its targets, and where the time went;
    - what went right, and what went wrong with each cause and its fix at that cause;
    - a pre-flight checklist for the next run, and a regression table it must match or beat.

    Link it to the one before, and keep a rolling index with each run's date and headline numbers. Update it while the
    fixes land. Before the next run starts, tick its checklist and check its regression table. The file is the source of
    truth; any shared doc is only a view.

**Today's results (2026-10-20).**
- A replay of real run histories through the scheduler simulator: GPU idle time with runnable work fell from 2.9 h to
  0, and deadlocks fell to 0.
- The loop since 2026-10-18 23:40 (34.7 h): 835 merges (24 an hour), 320 land conflicts resolved, 87 area collisions,
  19 stalls, 22 silent deaths, 578 queue starts, and 813 cards moved (314 to done).
- The loop's own pass went from 11 min to under a minute. The fixes: timing every step, moving slow work off the pass,
  and reading git state from records instead of from slow disks.

**A watchdog outside every session (owner #368).**
- A system service checks a list of expectations every minute. Each is a when / expect-within / then action, and the orchestrator
  and the leads add lines there instead of writing waiter scripts.
- It also has built-in checks: empty design calls, silent builder exits, unresolved conflicts, quiet runs, and
  production-first holds.
- It writes every action to the inbox.
- It exists because the orchestrator went dormant twice in one night: a waiter script died silently, and a design call
  wrote 0 characters, and nobody noticed for 45 minutes.

**Next measurements:** merges per hour after the backlog, conflicts per merge (target: zero between concurrent
builders), the time from collision to reshape, and whether main stays usable. That last one is checked by the outcome
check's 34 views on real projects.
