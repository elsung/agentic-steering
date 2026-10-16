# Worker brief (template)

The orchestrator fills this in and hands it to one fresh worker (small model, high effort).
One brief, one job of about one screen or one module, one worktree. See [STEERING.md](../STEERING.md) for why each part is here.

## Goal and why it matters
<Who this serves, what it is for, and what good looks like, in a few sentences. Include why it matters now.
A worker that knows the purpose makes better calls than one that only has steps.>

## Facts I checked
- Worktree: `<absolute path>` on branch `<name>` (already created; work only there; never create worktrees; never edit the live checkout).
- `<path or function>`: <what it does today, one line>
- `<real data example>`: <what it looks like>
Read these first. If you need more, read the code that writes the data; never guess a path or layout.

## Deliverables
1. <deliverable>. Acceptance: <test or check that proves it>.
2. <deliverable, including any screen the user will see>. Acceptance: <screenshot on real data, or a test>.
3. ...

## Rules (each with its reason)
- WARNING: do not change existing API fields or file formats; add new ones. (Other screens depend on them.)
- WARNING: do not delete or weaken a test or a check. If a check is wrong, say so under DECIDE.
- Full suite before reporting: `<test command>`. Paste its summary line; "still running" is not a result.
- Do not delete files; move them to `_trash/`. (Owner's rule.)
- If you run low on room, commit each finished deliverable and continue. Do not end with parts deferred.
- If the same test fails twice after real attempts, stop and report BLOCKED with what you tried.

## Report (exactly this shape, one message)
```
STATUS: DONE | BLOCKED
COMMIT: <hash> on <branch>
TESTS: <full-suite summary line, pasted>
BUILT: <one line per deliverable>
PROOF: <real-data output or screenshot paths, when asked>
NOT DONE: <list, or "nothing">
DECIDE: <one line, or "nothing">
```
No follow-up "idle" summary.
