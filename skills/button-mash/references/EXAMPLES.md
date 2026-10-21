# More worked examples (button-mash)

What happened, and what a good move looked like. The skill keeps the most instructive ones; these are the rest.

**The control loop took 11 minutes per pass, and work queued behind it.** No one had timed it. Good move: time the
loop's own steps, find the slow one (it was doing slow work inline and reading a busy disk), and move that work off the
loop. Then watch whether the fix held. The first fix didn't fully; the second did.

**The owner's "needs you" list held 36 items from earlier days, all already superseded.** The owner had to sort
through them to find the one live decision. Good move: whoever supersedes an item archives it at once, with a note on
what replaced it (it can be reopened), so the list stays true without a cleanup day.

**The same owner question was asked every round** (music for a show that has none on purpose). Good move: put the
owner's decision where the loop reads it every round, so the loop stops re-asking.

**Long research went to the expensive model by habit.** Good move: give reading and summarising to the cheapest
capable reader, with the output file named, and keep the expensive model for the decision the research feeds. When
the cheap reader failed on its provider's limit, fall back to another cheap model, not to the expensive one.

**Voice tests compared converted voices.** Good move: depth. A dubbing studio always lays out three things side by
side: the input performance, the target voice and the output. It listens for timing and emotion, not only timbre. A
test page laid out that way answers the owner's question in one listen.

**A test run claimed the shared card while the live production run waited.** Its builder had pointed it at that card
by hand, past the default that sends test work elsewhere. Good move: production goes first. Move or pause the test
run, then close the gap that let it through, so the next one is caught at once.

**Two measuring runs from one mission competed for one box.** Good move: one agent per task. The second reads the
first one's numbers instead of starting its own.

**A builder blocked because "the box is busy."** Busy is a queue, not a wall. Good move: submit to the shortest queue,
do the other work meanwhile, and collect the result.

**The watchdog called the live run stalled because nothing had been written for 15 minutes.** The run had
finished every stage; its status just hadn't been updated. Good move: before calling something stuck, ask
whether anything is still open. Quiet with work waiting is a stall. Quiet with nothing open is finished.

**After production finished, the watchdog brought back 28 held test runs at once, from experiments days old
whose builders were long gone.** Good move: bring back only what someone still owns and is working. The rest
stays put, and gets one line, not 28.

**Every routine restart onto new code posted a line to the owner's inbox: three lines every ten minutes.** Good
move: routine success goes to the log. The inbox is for what changes what someone does: a failure, a decision,
a milestone.

**A job failed four times with the same error, and each failure got a fresh automatic retry.** The error was in
the code the run was pinned to, and the fix was already in main. Good move: a failure that repeats its last reason
is the code or the input, not luck. Stop retrying, find where it is already fixed or fix it, then move the work
onto that.

**The fence hid the GPU from agents' CUDA, and a 3D preview still reached the card through its graphics driver.**
Good move: a fence protects a resource, not one door to it. When something gets through, close the path it used,
and check whether other paths lead to the same place.

**A self-heal relaunched a builder that had quit, into a worktree where its lead had already started another.** Two
builders then edited the same files. Good move: before an automatic restart, check whether someone already took
the work over.

**Idle processes read their whole history again every two seconds.** One had read nearly two terabytes since it
started, and together they slowed everything sharing the machine. Good move: measure what idle costs. Waste that
looks like work is still waste, and it taxes all the real work beside it.

**A cheap judge ran its own search across hundreds of folders on a slow disk to find the newest outputs.** Good move:
hand a cheap agent the answer it would otherwise search for. Put the facts it needs in its evidence, and say what
not to do and why.
