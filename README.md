# Agentic steering: getting cheap agents to finish the job

A field guide to running many AI coding agents from one orchestrator: one capable model steers, many cheap workers execute, and mechanical checks (not the workers' own reports) decide whether the work is done. It started as a way to cut the token bill; it grew into a playbook for keeping cheap agents from skipping work, over-claiming, or failing silently.

**The setup:**
- One expensive model steers: priorities, briefs, review, merge.
- Many cheap workers execute.
- Tests and scripted checks decide whether the work is done; silence or a claim never does.

**The two halves of this repo:**
1. **Cost**: route every worker to a small model, scoped to one tmux session (this page).
2. **Steering**: what goes wrong when cheap workers build real features, and the briefs, report shape and review scripts that fix it ([STEERING.md](STEERING.md)).

Everything here was checked against the official docs, a source we could fetch, or our own logged runs. Anything we could not verify is marked as such.

## The situation we started from

We run about ten Claude Code sessions side by side in one tmux session.
- One window is the **orchestrator**: it plans, talks to the human, reviews and merges.
- The others are long-lived **workstream threads**: build, research, audio, tests and so on. Each spawns its own subagents.

Every one of them ran on the largest model, and so did every subagent. The bill was dominated by:
- **execution work** (edits, test runs, file reading) done on the most expensive model;
- **long contexts re-read on every turn** (cache reads);
- **notifications that woke the orchestrator.** Every finished subagent sent a report and then a near-identical "idle" summary, and each one cost an orchestrator turn.

## The rule we adopted

> **No worker or subagent in this tmux set runs on the large model. Workers run on the small model (Haiku 5.5, high effort) or on a cheaper third-party model through a separate CLI. The large model only steers, writes specs and reviews.**

The rule covers this tmux session only, not every Claude session on the machine. Scoping it took one gotcha to get right (see below).

## What the sources taught us (verified)

1. **Route by verifiability, not by difficulty.** If a cheaper model's output can be checked by a grep, a diff or a test, send the work down. Keep the expensive model for judgment calls, where a plausible but wrong answer spreads quietly. (Reddit comment, ref 1.)
2. **Haiku 5.5 has a 100k cliff.**
   - Under 100k tokens of context: input $0.10 per million, output $0.50 per million, cache reads $0.01 per million.
   - **Above 100k, every price is ×5.** Keep each worker's context small. (Ref 10.)
3. **Many cheap, checkable attempts beat one smart attempt.**
   - The large model alone: 3.5 minutes, $0.47.
   - The large model directing 10 Haiku workers: under a minute, $0.14. (Ref 10.)
4. **The trap.** "If Opus solves something in 100,000 tokens and Haiku burns a million before giving up, Haiku costs more." Small models also mishandle odd tool errors: one saved a rate-limit error page as data. Give workers precise specs and tests, not open-ended problems. (Ref 10.)
5. **Cache reads can be 30–50% of an agentic bill.** Long contexts that are re-read are the hidden cost. (Ref 10.)
6. **For no-reasoning categorisation, a dedicated small judge model can beat the small chat model.** Routing and labelling is a good job for a local judge. (Ref 10, ref 9 context.)
7. **From a practitioner's setup** (ref 1):
   - the advisor writes a spec, and workers build to it and note any deviation;
   - Haiku at **high** effort was the best balance;
   - a fresh worker started with about 72k fixed tokens until trimmed to about 6k;
   - checks are mechanical, and a reviewer from a *different model family* sees only load-bearing work;
   - timed wake-ups were about half of one setup's tokens.
8. **The counterpoint: watch how often the expensive model is called.** One tester ran five setups on the same real bug, 3 runs each, graded by hidden tests (ref 2):

   | Setup | Cost per fix | Time |
   |---|---|---|
   | Sonnet alone | $0.15 | ~1 min |
   | Haiku alone | $0.23 | ~6 min |
   | Opus + Haiku subagent | $0.23 | ~7 min |
   | Opus alone | $0.52 | ~2 min |
   | Haiku main + Opus advisor | $0.69 | ~7 min |

   - All five scored about the same.
   - In the advisor setup, the large model was about 90% of the bill.
   - On easy bugs the ranking flipped, and Haiku alone was cheapest.
   - The lesson: the saving comes from **how rarely the expensive model is woken**, not from the cheap model alone. It's one bug and a handful of runs, so treat it as a data point.

## The setup

### 1. Force the small model for every subagent, scoped to one tmux session

Both variables are documented in the official subagent docs.
```bash
tmux set-environment -t <session> CLAUDE_CODE_SUBAGENT_MODEL claude-haiku-5-5
tmux set-environment -t <session> CLAUDE_CODE_SUBAGENT_MODEL_FORCE 1      # overrides agent frontmatter
tmux set-environment -t <session> ANTHROPIC_MODEL claude-haiku-5-5       # new windows start on Haiku
tmux set-environment -t <session> CLAUDE_CODE_EFFORT_LEVEL high
```
New windows and panes in that session inherit these. The orchestrator window is started explicitly with the large model (`claude --model opus`). See `setup/scope-to-tmux.sh`.

### 2. Switch already-running windows in place

In each idle window:
```
/model claude-haiku-5-5
/effort high
```

**Gotcha 1: `/model` and `/effort` save a machine-wide default.** They write `model` and `effortLevel` into `~/.claude/settings.json`, which changes every future Claude session on the machine, not just this tmux set. If the rule should stay scoped, restore the settings file afterwards, as `setup/scope-to-tmux.sh` does, and rely on the tmux environment instead.

**Gotcha 2: older CLI builds resolve the alias `haiku` to the previous Haiku.** Use the full model ID. Check the model name in the status line after switching.

**Gotcha 3: a window holding more than 100k of context should be compacted (`/compact`) before switching.** Otherwise the small model starts above its price cliff.

Only switch windows that are idle at the prompt. A window showing a pending question belongs to the human.

### 3. How work flows

| Role | Model | Does |
|---|---|---|
| Orchestrator | large model | priorities, specs with acceptance tests, review, merge, talks to the human |
| Workers / subagents | Haiku 5.5, high effort | build to the spec, run the tests, report once |
| Readers / researchers | cheaper third-party model via its own CLI | fetch and summarise sources, verbatim quotes with citations |
| Judges | small local model | route, label and sort review queues. Diagnostics only, never a gate |
| Cross-family reviewer | a model from another lab | only load-bearing changes |

**Rules that make it work:**
- **Spec first.** The orchestrator writes: the files, the interfaces, the acceptance tests. The worker builds until the tests pass. If the same task fails twice, the orchestrator narrows the task instead of letting the worker loop. This avoids the "a million tokens before giving up" trap.
- **Stay under 100k per worker.**
  - one small, self-contained task per fresh worker;
  - a short context packet (paths and a few lines of summary) instead of "read everything";
  - git worktrees so workers never touch the live checkout.
- **One report per milestone.** The worker writes detail to a `RESULT.md` and sends one short message. The orchestrator answers duplicates in a line. This alone removed a large share of orchestrator turns.
- **The orchestrator rotates.** When its own context grows long, it writes a handoff and a fresh session takes over.
- **Mechanical checks over prose:**
  - the full test suite before every merge;
  - output checks for generated media;
  - citation checks on research (every claim quotes a fetched source; unfetched sources are marked).
- **Research gets verified.** Our first summary from a worker recommended mid-size workers and large-model threads, the opposite of the rule. It also cited a source it had never fetched. A second, cheap pass that fetched every source verbatim caught both. Treat worker research as a draft until it is checked against the sources.

See `templates/worker-brief.md` for the brief we hand every worker.

### 4. Steering: keep cheap workers from skipping work

Cheap workers on a real build stop halfway and call it done, claim tests pass when they don't, put worktrees in the wrong place, and sometimes make a check pass by weakening it. [STEERING.md](STEERING.md) has the failure log, the brief rules (goal and why first, checked facts, numbered deliverables), the fixed report shape, a table pairing each rule with what enforces it, and the ideas we took from [pstack](https://github.com/cursor/plugins/tree/main/pstack). The scripts in `tools/`: `wt_new.sh` (the orchestrator makes every worktree), `make_brief.py` (refuses a brief without goal, why, scope and verify; pastes the standing orders), `check_report.py` (the worker's REPORT.json and changed files against the brief), `review_branch.sh` (mechanical checks and the full suite, recorded in a ledger by commit) and `merge_verified.sh` (merges only a reviewed commit).

## Not verified / open

- The exact setting that caps auto-compact near 100k. The claim comes from a news recap; we have not found it in the docs.
- Whether a `PreToolUse` hook can see the resolved model of an Agent call, to block large-model subagents. Not documented, so we use the environment variables.
- Three of the ten sources were blocked by bot walls or paywalls and are not used for any claim.

## References

See [REFERENCES.md](REFERENCES.md).

## License

MIT
