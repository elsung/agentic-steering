# The Button Mash Method

VERSION 1.3.0 (2026-10-20), with the skill [skills/button-mash](skills/button-mash/SKILL.md). History: [CHANGELOG.md](CHANGELOG.md).

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
top of Felix Rieseberg's ambition tutorial. The model "optimizes for the literal request", and the literal request is
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
- **A judge proposed jobs on another lead's live run** ("unstick R004"). They were stopped after 42 s with nothing
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

**06:15: 193 merges (29 an hour), still no milestone met.** hitmaker-ui is on round 30; its rounds now agree on the
one next action at both screen sizes and are down to one contradiction on one page. Two more blind spots, found by
reading why previz-15 and script-to-hit had no judge round for 70 minutes:
5. **Unowned files block builders.** Five page folders (the project page among them) were in no area, so three UI
   builders in a row stopped with "outside my scope". Fix: every file the app serves now has an owner.
6. **A finished agent can still look alive.** A builder wrote its final reply at 05:15, but its `claude -p` process
   kept waiting on a background shell it had started. It held two areas for an hour, which starved previz-15's job and
   kept script-to-hit's judge from running. Fix: a builder whose reply is written has ended, whatever its pid says. A
   second bug showed up as soon as that was fixed: two queued jobs on the same area started in the same tick, because
   the held set wasn't updated after the first launch.

**07:00: the first milestone met.** previz-15's p0 (a run folder makes an ep01 cut and animatic of real takes, read
back by run id). Three independent judges had said "met" since 06:37, and the loop threw each one out. Judges write
an opened file as "path (how I looked)", and the evidence check tested the whole string as a path. Fix: the first
word is the path. A contact sheet of the 145 s cut showed real cast takes with captions from start to end.
7. **Holding a resource is not using it.** "Production first" paused seven mission scratch runs from 04:16 while a
   production run counted as live. By 06:59 the RTX was at 0 % with 122 production jobs queued. Fix: an RTX idle 10
   min releases the held runs for 30 min, and run-ops is told production isn't feeding the GPU.

8. **"Newest" is not "best".** script-to-hit's judge went from a 189 s cut with 183 s real (round 20) to a fresh run's
   2-of-24-shot cut (rounds 21-22), only because it was newer, and queued jobs to fix the fresh run. Fix: judge the
   best output toward the milestone, name it, and say if a newer one passed it.

9. **Scope blocks were the most common stop: 51 by 07:50.** Judges assigned areas by guessing from names, builders
   found the code elsewhere, and each one stopped "outside my scope" and waited for a person or a later round. Fix,
   two parts: (a) judges list the files a job edits, and the files' areas are added; (b) a builder that still blocks
   on scope is re-briefed once with the areas of the files it named, and queued. The queue still keeps two builders
   out of one area.

10. **Builders stop on decisions they already have defaults for.** The r23 builder wrote six decisions, each with a
    sound default (Rachel's sample as a draft, voices on the idle Spark), then stopped. Fix: the brief now says a
    decision with a default that can be undone is not a block: take it, mark it "draft, owner may swap", and keep
    going. The owner gets one decision line with the default already under way. The same hour the scope self-heal
    fired on its own (p-audience-input re-briefed with crew-cut added).

**08:05: two milestones met.** hitmaker-ui m1 (Home and project pages clean and usable at phone and desktop width,
one obvious next action) was met at round 42, 20 minutes after the scope self-heal and an hour after the goalpost
fix. Loop numbers: since 2026-10-18 23:40: 257 merges (30.5/h), 28 land conflicts, 0 did not start, 64 area collisions, 9 stalls, 20 silent deaths, 156 queue starts, 252 cards moved (65 to done).

11. **A rule in a prompt is a suggestion; a rule in the code is a rule.** The judges' constraints said "a fresh run
    it starts itself", and a mission builder started R008 inside the production project, beside the live R007. R007's
    shoot sat unqueued and the RTX was idle about an hour (h3:0). Fix: every agent job carries `H3_AGENT_JOB`, and the
    engine refuses to make, start, resume or pause a run in the production root for it, naming the way out (a
    scratch root). The constraint text changed too, but the refusal is what holds.

12. **A spin can hide in new words.** hitmaker-ui m2 hit "the test project shows no episode rows" in five rounds in a row. Each
    judge worded it anew (similarity 0.2 to 0.76), so the same-gap check never fired, and each round queued another
    patch job. Fix: every 5th unmet round on one milestone counts as a spin. The spin prompt shows the last five
    gaps side by side and asks for one job that first traces the root cause in the running system.

13. **Finished work that never lands is the quietest failure.** The check for "a land is already running" matched any
    process whose command line mentioned land.sh. A builder hanging after its reply has its brief on its command line,
    and the brief names land.sh and the builder's own worktree. Autopilot marked that head as handled and never came
    back to it. Fourteen finished builders sat unlanded, among them the ep01 voice work script-to-hit was waiting for.
    Fix: count only processes running land.sh, and recheck a skipped head. A scan of finished-but-unlanded branches
    found the 14.
14. **A deploy is part of a merge.** The dashboard kept serving old web code after a web merge until h3:0 restarted it
    (h3:0). land.sh now restarts it after any merge that touches the web code, and says so in the inbox.

15. **The model's own limits are an outage the loop must ride out.** From 10:56 to 12:37 every judge died on the
    Claude session limit within a minute. The loop relaunched each one 10 minutes later, about 30 wasted rounds, and
    builders started then died too. Fix: a judge that dies on a usage limit makes its mission wait 15 minutes, and
    the round isn't counted.
16. **Every wait needs the same "is it really alive?" rule.** land.sh waited on the newest row for a worktree, and
    that row was a 10-hour scratch runner, so four lands sat for 2 to 10 hours. Fix: land.sh waits only on a
    builder, and not past its written reply. The same bug had been fixed in autopilot three hours earlier. The rule
    lives in each script that waits, so each one has to get it.

**13:05: three milestones met** (previz-15 p0, hitmaker-ui m1 and m2). The 14 stranded branches are all handled:
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
    and the judges' GPU list. All of them now read `~/.config/h3/boxes_off.json` at every call, so the box's owner
    hands it back by editing one file, with no merge.
19. **Failover has to be rehearsed on a real pane.** Account failover (owner #394) keeps each lead's transcript and
    flags. Its first trial found that pointing `CLAUDE_CONFIG_DIR` at the default dir makes Claude Code start as a
    fresh install, and that a new account must trust each lead's folder once. Neither was in the docs.

20. **A retry must be keyed on the state it retries, not on its own output.** The conflict re-land was keyed on the
    inbox line it reacted to, and every re-land wrote a new line. Two watchers (autopilot and the watchdog) each
    re-landed, and by 13:55 there were 36 duplicate lands of three dead branches on the merge lock. Every real merge
    waited 12 to 22 minutes behind them. Fix: re-land once per branch head, and land.sh refuses a second copy for
    one worktree. Self-healing loops need idempotence keys, or the healer becomes the outage.

21. **"Blocked, the lead decides" is a silent wait unless the lead hears it.** hitmaker-ui blocked at 13:53 during the
    merge jam. The line went only to the inbox, and h3:4 never saw it, so the mission sat for 45 minutes. Fix: the
    block goes to the lead's pane with delivery checked, and a blocked mission whose own jobs land afterwards resumes
    itself. The block was the pipe, not the goal.

22. **Sequences need a hand-off, not a person.** A17's UI rounds sat idle after each landing (R1 13:45, R2 14:57)
    until h3:0 pushed. Fix: a chain file lists the rounds, and autopilot starts the next the moment the previous
    lands. With no brief written, it tells the lead where to write one, and starts the moment the file exists. The
    first version started a second R3 beside the one the lead had just launched, in another worktree. Rounds are now
    matched by name, and a hand-started one is followed, not doubled.

**16:15: four milestones met.** hitmaker-ui m3 (the Cut page shows the real cut with hit notes on the cut's own
seconds) was met at round 89. hitmaker-ui is 3 of 5, previz-15 is 1 of 5 (its judge split p1 into smaller steps), and
script-to-hit is 0 of 3: ep01 still lacks its spoken lines end to end. Loop numbers: since 2026-10-18 23:40: 450 merges (27.1/h), 309 land conflicts, 0 did not start, 67 area collisions, 12 stalls, 22 silent deaths, 301 queue starts, 405 cards moved (114 to done).

23. **Every pause needs an end that doesn't depend on someone remembering.** A manual hold on R010's visualise
    stage outlived the watcher meant to release it, and the run sat idle (h3:0). Fix: a hold carries an expiry
    (default 20 min), the runner releases expired holds and logs it, and the watchdog posts any hold over 10 min on a
    live run. The same goes for leases, locks and reservations: they all need a timeout plus an alarm.

**19:46: seven milestones met.** In the last three hours:
- hitmaker-ui m4 (one-tap steer) was met. hitmaker-ui is 4 of 5, now on m5 (premium).
- previz-15 p1a (boards) was met. previz-15 is 2 of 5.
- script-to-hit h1 (ep01 plays end to end, lines spoken, consistent faces) was met. That's its first milestone, after
  about 75 rounds; the last gaps were the voice routing and the S24 face check.

Loop numbers: since 2026-10-18 23:40: 515 merges (25.6/h), 310 land conflicts, 0 did not start, 67 area collisions, 12 stalls, 22 silent deaths, 342 queue starts, 446 cards moved (130 to done).

24. **Agents block on beliefs, so give them the checks, not just the rules.** previz-15's ep01-only run never
    started. Its builder waited for "owner OK for the paid read and World calls", which are Claude subscription calls,
    and for "the voice-research hold on two draft boxes", which wasn't active. Each rule was right; the builder's facts
    were wrong. Fix: every brief names the one command that checks each fact (what counts as paid, box_hold.sh
    status, the free-cards list), and h3:6 queued the run with the facts in its brief.

25. **A loose goal plus an autonomous loop will optimise the wrong thing in plain sight.** hitmaker-ui's last milestone
    said "looks premium and genre-aware". Over 15 rounds its judges and builders repainted the approved interface:
    rose background, italic serif title, heavy outlines. The owner called it terrible (owner #429). The loop did
    exactly what the words allowed. Fix: some areas are taste, not tasks. The look belongs to h3:0's reviewed UI
    rounds; mission jobs are marked no-visual, and the commit hook refuses stylesheets and fonts. Self-direction needs
    fenced areas where only a person decides.

26. **"Only a user can retry" is a stop the user never hears about.** The engine blocks a failed job's key until a
    user retries it. That's sensible for production, but nobody is told. R007 sat after a drain cancelled its jobs,
    and r97's one-hour test sat 25 min after one lookbook failure, with every card stale and the Spark idle. Fix: the
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
29. **Agents name a safe default and then stop anyway.** Rounds r126, r129 and r157 each wrote "Default: ...",
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

**Today's results (2026-10-20).**
- A replay of real run histories through the scheduler simulator: GPU idle time with runnable work fell from 2.9 h to
  0, and deadlocks fell to 0.
- The loop since 2026-10-18 23:40 (34.7 h): 835 merges (24 an hour), 320 land conflicts resolved, 87 area collisions,
  19 stalls, 22 silent deaths, 578 queue starts, and 813 cards moved (314 to done).
- The loop's own pass went from 11 min to under a minute. The fixes: timing every step, moving slow work off the pass,
  and reading git state from records instead of from slow disks.

**A watchdog outside every session (owner #368).**
- A system service checks a list of expectations every minute. Each is a when / expect-within / then action, and h3:0
  and the leads add lines there instead of writing waiter scripts.
- It also has built-in checks: empty design calls, silent builder exits, unresolved conflicts, quiet runs, and
  production-first holds.
- It writes every action to the inbox.
- It exists because the orchestrator went dormant twice in one night: a waiter script died silently, and a design call
  wrote 0 characters, and nobody noticed for 45 minutes.

**Next measurements:** merges per hour after the backlog, conflicts per merge (target: zero between concurrent
builders), the time from collision to reshape, and whether main stays usable. That last one is checked by the outcome
check's 34 views on real projects.
