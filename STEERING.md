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
| 9 | Reported DONE with the full suite passing, but the screens were broken in a browser (a script error, a 500 on real data, content invisible, off-theme colours) | 1 | Tests covered the API, not the page; the worker never opened the page | For any screen, the worker must load it in a headless browser against real data, report zero page and console errors, and attach screenshots it has looked at. The orchestrator opens them too. |
| 10 | The reply said "DONE, NOT DONE: nothing" while the same worker's REPORT.json marked two items not_done | 1 | The prose summary is written for the reader; the structured file was filled item by item | Read the checked REPORT.json, not the reply. `check_report.py` caught it on its first real use. |
| 11 | Invented its own REPORT.json shape (so every item read as missing); silently dropped one brief item; used `rmtree`; called a main-thread-only function from a background thread against the docstring; worked off a stale main | 1 | A free-form report; long brief items read selectively; tests with a fake context hid the threading bug | `make_brief.py` writes a pre-filled REPORT.json (every item not_done) for the worker to fill in, not invent. Two new standing orders: honour docstring contracts; code never deletes. Reading the diff against each brief item stays the orchestrator's job. |

| 12 | A "real-data proof" test that ended in `assert True`; a test named for a feature that never exercised it; a positional constructor call that put a value in the wrong field, so the feature never worked while its test passed | 1 | Tests written to pass, named for the brief item rather than checking it | `review_branch.sh` fails hollow asserts. The orchestrator reads each new test against the brief item it claims. Real-data proof goes in REPORT.json evidence, not in the suite. |
| 13 | Claimed "default behaviour byte-identical" while the default path gained a second copy of every input; a cache that ignored its own key; failed sub-agents skipped silently; a model setting written to config that the code never reads (the cheap model would have run on the expensive one) | 1 | Tests checked the new mode only; "identical" was asserted, not compared; config added without tracing where it is read | A golden test of the default path against main's literal behaviour; a test per new config key that sets it and checks the effect; sub-agent failures change the output visibly. After two quality misses on one model family, the next round went to the other family and came back largely right (one over-correction, fixed in review). |
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

## A report the checker can read: BRIEF.json and REPORT.json

Prose reports let a worker leave things out without saying so. So the deliverables and the report are also data:

1. Before briefing, the orchestrator writes the numbered deliverables into the worktree with `tools/make_brief.py <worktree> --goal ... --why ... --scope src/x/,tests/ --verify "cmd" "D1|test|..." "D2|screenshot|..."` (proof is test, screenshot, real-data or none) and pastes the printed list into the brief.
2. `make_brief.py` also writes a pre-filled `REPORT.json` (one entry per deliverable, all not_done). Before replying, the worker fills it in: status, commit, the pasted test summary line, and one entry per deliverable (`done` or `not_done`, evidence, evidence files).
3. `tools/review_branch.sh` runs `tools/check_report.py`, which fails when:
   - a deliverable has no entry;
   - a `done` has no evidence, or names a file that doesn't exist;
   - a screenshot deliverable has no image;
   - the commit isn't HEAD;
   - the claimed test count differs from the orchestrator's own run;
   - the status is `done` while an item is `not_done`.

   A missing REPORT.json is a FAIL: silence is not success.

Both files stay untracked (add them to `.gitignore`). This is the cheap version of schema-constrained output for tools that can't enforce a schema on a subagent's reply: the structure is checked after the fact, in code.

## What we took from pstack

[pstack](https://github.com/cursor/plugins/tree/main/pstack) (Cursor's engineering plugin, MIT) arrives at many of the same rules from the other side: one strong engineer running fleets of agents. Four of its ideas filled real gaps here.

1. **Standing orders, pasted verbatim into every brief.** Directives decay across re-briefs and resumes, and each dropped one costs a human turn. `tools/STANDING_ORDERS.md` holds numbered constraints, each with its reason; `make_brief.py` pastes it into every brief. When you catch yourself restating an instruction, add the line before you act.
2. **A brief with an empty field is a unit you haven't scoped.** `make_brief.py` refuses to write a brief without a goal, a why, a SCOPE (paths the worker may write) and a VERIFY command, and it adds a timebox. `check_report.py` fails any file changed outside SCOPE. On its first run against a past branch it flagged three files outside the brief's folder.
3. **A verification ledger keyed by commit.** `review_branch.sh` appends one row per verdict (time, branch, commit, PASS/FAIL, level). `merge_verified.sh` merges only a commit with a full-suite PASS; a commit made after review voids it. "Was this verified?" is answered by the ledger, not by memory or a transcript.
4. **Each rule paired with what enforces it** (pstack's `/correct`): eliminate the mistake by structure first, then a check, then a test, and write docs only for judgment calls, because nothing fails when an agent skips a doc. When the same correction comes twice and the rule lives only in docs, move it up a level in the same change.

| Rule | Enforced by | Level |
|---|---|---|
| Worktree outside the live checkout | `wt_new.sh` creates it; `review_branch.sh` fails otherwise | structure |
| Brief has goal, why, scope, verify | `make_brief.py` refuses otherwise | structure |
| Standing orders reach every worker | `make_brief.py` pastes them | structure |
| Only reviewed commits merge | ledger + `merge_verified.sh` | structure |
| Every deliverable answered with evidence | BRIEF.json + `check_report.py` | check |
| Write only inside SCOPE | `check_report.py` | check |
| Full suite passes; claimed count matches | `review_branch.sh` + `check_report.py` | check |
| No deleted tests, split strings, removed keys | `review_branch.sh` | check |
| Screens work on real data | screenshot proof in BRIEF.json; the orchestrator opens them | check + eye |
| Context and intent in briefs | `--why` required; the rest is judgment | docs |

Also from pstack, now in our orchestrator rules:

- **Never resume an agent to check on it**; a resume restarts it. Probe read-only (its branch, its REPORT.json, its process). A transcript's modification time is not liveness.
- **A silent death is a failure with a cause.** Write down the unit, the last evidence and what's left, then brief a fresh worker with consolidated scope: the original brief, every later directive, the prior report and branch. Never trust a resumed agent's "done".
- **Switch model family after repeated quality misses.** In our case two rounds from one family missed subtle bugs; one round from the other family fixed all six listed defects.
- **Retry by failure mode.** Out of room: split the scope. Tool or model error: a different model. Unknown: once. Two retries, then replan around it.
- **Verify on a different model family** from the worker for high-blast-radius units (UI, data formats, schedulers). Agreement across families is high signal.

What we did not take: pstack's terse-prose rules for creative work. For prompts that produce story, style or direction, rich language and intent stay (see "Context and intent first").

## Rules for the orchestrator when a report arrives

1. A missing, partial or idle-only report = NOT DONE. Ask once. If the worker stops short again, stop it and brief a fresh worker with the remaining items.
2. Run `tools/review_branch.sh <worktree>` before reading the worker's claims. Merge with `tools/merge_verified.sh` only on its PASS plus your own look at the diff.
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
- [`tools/make_brief.py`](tools/make_brief.py) and [`tools/check_report.py`](tools/check_report.py): the deliverables as BRIEF.json, and the check of the worker's REPORT.json against them (see above).
- [`tools/STANDING_ORDERS.md`](tools/STANDING_ORDERS.md): numbered constraints with reasons, pasted into every brief.
- [`tools/merge_verified.sh`](tools/merge_verified.sh): merges only a commit with a full-suite PASS in the ledger.
- [`tools/review_branch.sh`](tools/review_branch.sh): mechanical checks before you read a worker's claims:
  - where the worktree is, and whether the branch contains current main;
  - uncommitted changes and committed junk;
  - deleted test files and test functions, changed asserts, strings split to dodge a check;
  - lopsided deletions, and removed response keys;
  - the full test suite.

  Prints PASS or FAIL with reasons. On its first run it caught a committed notes file the worker had reported as clean.
