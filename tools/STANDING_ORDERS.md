# Standing orders (pasted verbatim into every worker brief by make_brief.py)

One constraint per line, each with its reason. Edit these for your project. When you catch yourself restating an
instruction to a worker, append the line here before you act. Reasons matter: a worker that knows why makes better calls.

1. Work only in the worktree path you were given. Never create worktrees; never edit the live checkout. (Relative paths landed worktrees inside the live repo.)
2. Never delete files; move them to `_trash/`. (Owner's rule.)
3. Kill only processes you started, by PID. Never `pkill -f` or `killall`. (Other work shares the machine.)
4. Never change or remove an existing API field, file format or function signature; only add. (Other screens depend on them.)
5. Never delete or weaken a test or a check, and never split strings to get past one. If a check is wrong, say so under DECIDE.
6. Write only inside the SCOPE paths in your brief; anything else goes under DECIDE. (check_report.py fails files outside scope.)
7. Run the full suite yourself before reporting and paste its summary line. "Running" is not a result.
8. Any screen you change: load it in a headless browser on real data, zero page and console errors, screenshots you have looked at under `_shots/`.
9. Never invent a file path or data layout; read the code that writes the data and test on real data, read-only.
10. If you run short on room, commit each finished deliverable and continue; never end with parts "deferred". The same failure twice after real attempts: stop and report BLOCKED with what you tried.
11. Write REPORT.json before replying. Silence or a prose-only reply counts as not done.
