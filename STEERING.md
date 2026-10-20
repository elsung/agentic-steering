# Steering cheap agents so they finish the job

> **Now: [the Button Mash Method](BUTTON_MASH.md).** It keeps agents moving with assessment loops, not evals or tests, and no gates. The spec-first and test-gated advice below is the earlier method, kept for the record.

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
| 14 | Six workers on one provider at once hit its plan's rate limit; one died mid-edit with work uncommitted, another exited silently with no changes | 1 | Concurrency set by how much work was waiting, not by provider limits | Cap at 3 concurrent workers per provider; spread load across providers; a worker that exits without REPORT.json is failed: read its log tail for the cause and relaunch fresh from its committed and uncommitted state. Tell workers to commit each deliverable as it passes, so an interruption loses little. |
| 15 | A new test wrote into the repo's own config folder (relative path) and broke 13 other tests depending on order; the worker then called the failures "pre-existing" and filled a required field with an invented value | 1 | Relative paths in tests; failures blamed on the base without checking; placeholder content to satisfy a schema | `review_branch.sh` fails when the suite leaves new files in the repo; "pre-existing" is checked against main's own green run; standing order: never fill a required field with invented content. |
| 16 | (The orchestrator's own slips) A rebase stopped on a conflict whose output was piped through `tail`; the review ran on a half-rebased tree. Another conflict resolution dropped one closing brace in a stylesheet, scoping a whole page's styles inside a phone-only media query; every test passed. Merging branches one by one moved main under three running reviews. | 1 | Hidden rebase output; no structural check on CSS; reviews racing serial merges | Rebase loudly (`git rebase main || echo "REBASE CONFLICT"`) and check for unmerged files before reviewing; a test that every stylesheet's braces balance (proved on the broken file); merge a batch only after its reviews finish. |
| 17 | "Proof" screenshots that were a hand-made mock page, or showed an error message, reported as working screens; a new script redeclared a top-level helper (`esc`) the main app declares, so whichever loaded second died and with a reorder the whole dashboard would have failed to load | 2 | Screenshots taken to satisfy the report, not looked at; scripts share one global scope | Orchestrator drives the REAL flow on a scratch copy of real data before merging any UI. Planned check: a test that no two static scripts declare the same top-level name. Standing order 9 now says: a screenshot is proof only of the real page in the real flow; an error on screen means not done. |
| 18 | A waiter `until ! pgrep -f "x.py"; do sleep 20; done` never ends because pgrep matches the waiter's own command line. Found twice: two loops ran 78 h in one thread, and in another it hid two stages for ~10 days. Also: long text sent into a tmux window with send-keys sat unsubmitted until a separate C-m. | 2 | Self-matching process patterns; terminal input quirks | Wait on a PID (`while kill -0 PID`) or a done-file, never on `pgrep -f` of your own pattern. Send the text, then a separate `tmux send-keys C-m`, and check the pane. |
| 19 | (The orchestrator) A rebase chain printed "REBASE CONFLICT" and then carried on into the review; and it rebased an integration branch made of merge commits, which linearised it into a mid-rebase mess. Main hadn't even moved. | 1 | Warning without stopping; rebasing when not needed | Rebase only when the branch does not already contain main, and stop on a conflict: `git rebase main \|\| { git rebase --abort; echo REBASE CONFLICT; exit 1; }`. Never rebase an integration batch built from merges; re-merge the batch instead. |
| 20 | (The orchestrator) Briefs written with the scope as space-separated paths; the tool split only on commas, so every in-scope file read as "outside SCOPE" and two finished branches failed review on bookkeeping. Separately, a Dev desk item pointed at a file outside the allowed roots and the worker saw a refusal instead of the page. | 2 | A tool that accepts input it then misreads; publishing without opening the page as the worker would | Tools accept every reasonable form (commas, spaces, globs) instead of relying on the caller to remember one. Open every Dev desk item through the dashboard (not the file path) before telling the worker it is there. |
| 21 | A worker marked a structural deliverable "done" when only two of the stages it was meant to restructure were queued; the mechanical review PASSED (suite green, report shaped right), and the lead found the gap plus a real bug (a made item never counted as ready, so a scene waited forever) by reproducing the claim | 1 | A green suite and a well-formed report measure what the tests cover, not what the brief asked | A mechanical PASS is not acceptance. The lead reproduces each structural claim on real data before calling it accepted; time-to-quality is measured to the accepted PASS, not the first green run |
| 22 | Two workers on the same brief both stopped at the hardest item (splitting one big stage into per-item jobs) and called it "blocked, needs an owner decision" | 2 | The brief described the outcome (scene 1 starts while later casting runs) but not the structural change that outcome needs, so the change looked optional | Name the structural change in the deliverable itself. When workers call the core item blocked, the orchestrator decides it the same hour; that decision is the orchestrator's, not the owner's |
| 23 | A worker used `git stash` / `stash pop` inside its worktree | 1 | The stash stack is shared by every worktree of a repo; a pop can apply another worker's changes | Standing order: never `git stash`; set work aside with a WIP commit |
| 24 | (The orchestrator) Widened a model's role from bulk reading to coding workers without asking the owner; the owner found out when asking which jobs ran where | 1 | A routing change was treated as an implementation detail | Model routing is an owner-visible decision: record it with the owner's words, and measure before widening (see PRACTICES.md section 12) |
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

## Practices from a long multi-agent build night

See [PRACTICES.md](PRACTICES.md) for how we ran a night with ~15 worker branches, three research tracks and a design partner: candidate versions, model-family switching, provider caps, a review desk, research synthesis, and treating every new feature as a hypothesis.

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
