# Practices that held up over a long multi-agent build

One orchestrator (a strong model that only steers and reviews), cheap workers from two providers in git worktrees, a design partner model for UI and product design, and research workers for fact-finding. These practices came out of a single long night of building a production web app and its creative pipeline, with a real production run going on the same machine the whole time.

## 1. The real job comes first

- **Ask what a top professional would do, not just how to make the task faster.** For a creative production tool, the "producer" isn't the operations manager. They make a hit. Speed and cost matter because they buy more creative iterations. We rewrote our plan when the owner pointed this out: an efficiency track *and* an equal creative-impact track.
- **Make the ask deeper, not bigger.** Before planning, answer four questions:
  1. what would a top professional do that wasn't asked for;
  2. what's the rawest material to start from (the script, the GPU's own timeline log, the owner's picks), rather than summaries;
  3. which methods and tools they'd use;
  4. what, other than the agent or the owner, would show the result is right (logs, measurements, labelled side-by-sides).

  Then rewrite the ask.

## 2. Evidence before plans

- **Measure where the time goes before proposing fixes.** Our 3½-hour stage looked like "too many images". The image server's log showed the real waste: two large models swapped in and out for every image. A scheduling change fixes that with identical outputs.
- **Research workers oversell. The orchestrator checks fit.** Three parallel research reports came back with useful leads and confident but wrong recommendations: identity tools for an older model generation, engagement numbers without sources. Synthesise against what the system already has and what fits its models, and mark unverified numbers.
- **Trial tools narrowly with real questions.** A code-graph tool (Graphify) was tried on six real questions against grep. It won on "what is X / who calls X" and lost on broad searches, getting one wrong. Adopt it for what it's good at, require a grep confirmation, and rebuild it automatically after each merge.

## 3. Changing behaviour safely

- **New method versions are candidates.** A new version of the agents' instructions is listed and can be chosen on purpose, but is never the default for new runs until the owner promotes it after a labelled comparison. A worker spotted that "newest = default" would have silently switched production. It reported this under DECIDE instead of editing the tests, which is the behaviour we want.
- **Golden tests pin the default path.** When adding an optional mode, a test compares the default path's inputs and instructions against main's literal values. "Byte-identical" claims are compared, never asserted.
- **Every new creative feature is a hypothesis.** It gets its own switch, a labelled A/B against "off" on fixed benchmark scenes, and named failure modes shown beside the pictures:
  - sameness across episodes;
  - invention beyond the source material;
  - devices crowding every moment;
  - notes applied mechanically;
  - rules followed where the story says otherwise.

  A feature that doesn't beat "off" by the owner's eye is revised or retired.
- **Learned rules are guidance, not gates.** Preferences learned from the owner become rules with a scope, a strength (note / usually / always), a why, a source link, revisions and a use record. The agents must say which rules they followed or departed from. Nothing is learned silently.

## 4. Running many workers

- **At most 3 concurrent workers per provider, with load spread across providers.** A rate limit killed workers silently.
- **Switch model family after repeated quality misses.** Two rounds from one family missed subtle bugs. One round from the other family fixed all six listed defects, with one over-correction caught in review.
- **Pre-filled reports.** The brief script writes REPORT.json with every deliverable marked not_done, so workers fill in the shape instead of inventing one.
- **Workers commit each deliverable as it passes,** so an interruption loses little. A fresh worker continues from the previous one's committed and uncommitted state.
- **Separate port ranges** for workers' preview servers and the orchestrator's own checks. Workers left previews running on every worker port.
- **Never edit a steering script in place while a review is running.** bash reads scripts as it executes. Write a new file and `mv` it over the old one.

## 5. Review where the owner is

- **A review desk inside the app** (development mode only) for designs, HTML mocks, read-only branch previews and labelled tests. The owner comments and approves there; the orchestrator reads the comments before merging. No more "open this folder on the share".
- **The orchestrator verifies screens itself on real data.** Workers' screenshots have shown an error page, a made-up example instead of the real document, and a scratch copy that hid the real bug: every card said "just now", because seconds were multiplied by 1000.

## 6. The orchestrator's own mistakes go in the same log

The orchestrator hid a rebase conflict behind `tail`, dropped a brace while resolving a conflict, and raced merges against running reviews. They're logged as failures like any worker's, and each got a check or a rule.

## 7. Raising the ceiling: lessons from "Made by mechanical means"

Felix Rieseberg [built an art-directed interactive site in 48 hours](https://felixrieseberg.com/made-by-mechanical-means/) by directing a model, with a supervising thread and ~60 worker threads. What we're taking from it:

- **Start from first principles, then explore wide.** Ask what the product is fundamentally for, and who steers it and how. Then run several genuinely different directions in parallel with little guidance, pick one, and ask for variations of it. Polishing the first idea is how you get a "vanilla" result.
- **Every iteration is a page the owner can open on their phone.** Review shouldn't need a desk, a folder or a question to the orchestrator.
- **Taste feedback, not specs.** "Less excited", "warmer", "this one". The workers translate taste into changes and show the revision beside the original.
- **Quality from process, not code review.** Adversarial QA threads drive the real product in a headless browser round after round and write findings. A night of six "working" branches that were broken in the browser taught us this: the orchestrator should not be the one catching them.
- **Numbers to climb.** Give workers measurable targets (frame rate, seconds per image, pixel-identical output) and let them hill-climb. Models are very good at it.
- **Structure the code for parallel work.** One file per component means many threads can work at once. A 3,000-line front-end file was where most of our merge conflicts happened.
- **The supervisor remembers decisions.** Owner decisions are written to a register that every new brief carries (our standing orders), so nobody repeats themselves.
