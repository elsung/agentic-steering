# Steering cheap agents so they finish the job

Cheap workers are fast and inexpensive, but on a real build they fail in predictable ways. This page records the failures we saw and the fixes that worked, in the order we learned them. It is a living log: every new failure type is added the day it happens.

The principle behind all of it:

> **No report is not success, and a claim is not evidence.** Silence, an "idle" notice, "tests are running", or "should work" all mean NOT DONE until the orchestrator has checked it.

## What went wrong (one afternoon, 9 small-model workers, one web app)

The task was a dashboard build: about ten features across a Python back end and a JavaScript front end, each given to one worker in its own git worktree.

| # | Failure | Times | Root cause | Fix (mechanical first) |
|---|---|---|---|---|
| 1 | Worktree created inside the live checkout | 4 | The worker inherits the orchestrator's working directory, so a relative path lands inside the repo | The orchestrator creates the worktree before briefing and passes the absolute path. Workers never run `git worktree add`. (`tools/wt_new.sh`) |
| 2 | Stopped halfway and called it done ("UI deferred to save tokens", "next phase") | 4 | Big briefs. The worker stops when its own idea of the core is finished | Numbered deliverables, and the report answers each one. An unanswered item is not done. Bigger jobs are split across workers in sequence. |
| 3 | False test claims ("all pass" with 3 failing; "full suite running") | 3 | Partial or stale test runs reported as the result | The orchestrator always runs the full suite itself. The report must paste the summary line. "Running" is rejected. |
| 4 | Broke an existing contract (a list changed into a count) | 1 | The worker reshaped data for its own screen | Brief rule: only add fields, never change existing ones. The review script flags removed response keys. |
| 5 | Deleted its own tests; split a word in code (`"blen" + "der"`) to get past a check | 2 | Made the check pass instead of making the code right | Brief rule: never delete or weaken a test or a check; if a check is wrong, say so. The review script lists deleted tests, changed asserts and split strings. |
| 6 | Invented file paths: the feature found nothing on real data | 1 | Wrote code from the brief's words, not from the real folders | Acceptance includes proof on real data (read-only), pasted in the report. |
| 7 | Built on an old main; merging would have deleted work merged since | 1 | Long-running branch | The review script checks the branch contains current main and flags files where the branch deletes far more than it adds. |
| 8 | Stale facts in the product (an old model name) | 2 | The small model's own knowledge | A "facts I checked" block in the brief with exact names and values. |

What worked:
- **Briefs that open with the goal and why** (see below).
- **A "facts I checked" block**: exact paths, function names, current behaviour, a real-data example.
- **The fixed report shape.**
- **Screenshots on real data before merging any UI.**
- **A fresh worker instead of a third re-send.** After two stops short, the remaining items go to a new worker with a clean context.

## Context and intent first, even at more tokens

We tried the opposite direction too: terse, controlled language (in the style of ASD-STE100 Simplified Technical English) to cut tokens. Our conclusion:

- **Keep the precision:** one word per meaning, defined once ("done" = full suite passing, summary line pasted, committed, nothing deferred); warnings placed before the step they apply to; numbered steps with their acceptance check.
- **Never strip the reasons.** Workers that know the goal and why it matters make better judgement calls. Pure commands make them literal and brittle. That is exactly the failure mode that costs re-sends. The failures above were misreadings of scope, not wordiness. A longer brief that prevents one re-send is cheaper.
- **Creative work is different.** For prompts that produce creative output (story, style, direction), rich language and intent are the point; we do not compress them at all.

## Rules for every brief

1. **Goal and why first**: who it serves, what it is for, what good looks like. Then context, then numbered deliverables, then rules, each with its reason.
2. **Facts I checked**: exact paths, names, current behaviour, real-data examples. Never ask a worker to guess a layout.
3. **Numbered deliverables**, each with its acceptance check. A user-facing screen is a deliverable, never optional.
4. **Warnings before the step** they apply to: don't change existing fields; don't delete or weaken tests; don't touch the live checkout.
5. **The worktree is made by the orchestrator**, absolute path given.
6. **Size**: one worker is about one screen or one module. Split bigger jobs and run them in sequence on one branch.
7. **Report shape, exactly:**
   ```
   STATUS: DONE | BLOCKED
   COMMIT: <hash> on <branch>
   TESTS: <full-suite summary line, pasted>
   BUILT: <one line per deliverable>
   PROOF: <real-data or screenshot evidence when asked>
   NOT DONE: <list, or "nothing">
   DECIDE: <one line, or "nothing">
   ```
   `NOT DONE` can't be left out, which makes stopping short visible at a glance.

## Rules for the orchestrator when a report arrives

1. A missing, partial or idle-only report = NOT DONE. Ask once. If the worker stops short again, stop it and brief a fresh worker with the remaining items.
2. Run `tools/review_branch.sh <worktree>` before reading the worker's claims. Merge only on its PASS plus your own look at the diff.
3. UI changes: screenshot at desktop and phone width on real data before merging.
4. Rebase or resolve conflicts yourself when main has moved; a worker resolving conflicts in code it didn't write is how merged work gets lost.
5. Add every new failure type to the table above the same day.

## Structure enforcement: what it can and can't do

Grammar- or schema-constrained output (llama.cpp GBNF; JSON-schema structured outputs on frontier APIs, such as Claude Code's `claude -p --json-schema`) prevents *malformed* output. It does not prevent a worker from skipping work or over-claiming. Where it helps:

- **Make skipping visible.** Require one entry per input item (each deliverable, each note, each shot) with a status and a reason, then check the list against the inputs in code. A missing item fails mechanically.
- **Constrain only the final answer.** Let the model reason freely; forcing structure from the first token can make reasoning worse.
- **Local models** benefit most: grammars make small local models dependable enough for structured steps.
- **Judge models** (small classifier-style decision models) are for questions code can't answer, such as "does this image match the shot's intent". They are not the main check on whether a worker did what it was asked; code checks are cheaper and more reliable there.

## Tools

- [`tools/wt_new.sh`](tools/wt_new.sh): creates `<prefix><name>` on a new branch from current main and refuses any path inside the live checkout.
- [`tools/review_branch.sh`](tools/review_branch.sh): mechanical checks before you read a worker's claims:
  - where the worktree is, and whether the branch contains current main;
  - uncommitted changes and committed junk;
  - deleted test files and test functions, changed asserts, strings split to dodge a check;
  - lopsided deletions, and removed response keys;
  - the full test suite.

  Prints PASS or FAIL with reasons. On its first run it caught a committed notes file the worker had reported as clean.
