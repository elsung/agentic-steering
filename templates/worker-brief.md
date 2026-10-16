# Worker brief (template)

The orchestrator fills this in and hands it to one fresh worker (small model, high effort).
One brief, one task, one worktree.

## Goal
<one sentence: what is true when this is done>

## Context packet (read only these)
- `<path>`: <why it matters, one line>
- `<path>`: <why it matters, one line>
Do not read the whole repository. If you need more, say which file and why in your report.

## Interfaces you must keep
- `<function / CLI / file format>`: <exact signature or shape>

## Acceptance tests
- [ ] `<test command>` passes (write the failing test first)
- [ ] the full suite passes: `<command>`
- [ ] <any output check: file exists, image size, no error lines in log>

## Rules
- Work in your own git worktree, never the live checkout.
- Do not delete files: move them to a `_trash/` folder.
- Stop and report if the same test fails twice after real attempts. Don't keep looping.
- Note every deviation from this brief, and why.

## Report (once)
Write the detail to `RESULT.md` in your worktree: what changed, test output, deviations, what was not tested.
Then send ONE short message: done or blocked, the branch name, the test count, and one line on anything the orchestrator must decide.
No follow-up "idle" summary.
