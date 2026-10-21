# Forward and clean: extreme motion without rot

*A digest written by a reading agent (2026-10-21). Quotes and figures are as it reported them, with their links; spot-check before citing a number.*

**The question.** How do we keep ~10 cheap agents building in parallel on one application — merging dozens of times an hour — while the codebase gets *cleaner* instead of sprawling into duplicate implementations, dead flags and parallel code paths?

**Our stance.** No blocking gates, no required suites, assessment by looking at the real output. Most of the literature below is gate-shaped, so the reconciliation is the main finding: **a gate that blocks a merge is better spent as a sensor the agent sees inside its own loop.** Feedback left, verdicts on a trend board, a person looking at the running thing.

---

## What the sources say

### Kent Beck, *Tidy First?* — https://newsletter.kentbeck.com/p/structure-and-behavior-prs

- **One change, one kind** — structural or behavioural, never both; the only rule that survives agent parallelism — and **timing is judgement**: tidy *first* when the payoff is immediate and known, *after* when you will return soon, *later* via a running list, *never* when behaviour is frozen. Tidy only what the next change needs.
- **Economics and the agent era:** tidying buys optionality — in the compounding game you invest in futures as much as in features — and the code must stay in a form the *tool* can modify. https://newsletter.kentbeck.com/p/earn-and-learn · https://newsletter.kentbeck.com/p/party-of-one-for-code-review

> "Constrain PRs to *only* contain one kind of change or the other. Never both."

### Martin Fowler, and Böckeler's agent-sensor work — https://martinfowler.com/bliki/OpportunisticRefactoring.html

- **Refactoring is ordinary work,** not a project phase: "getting the feature finished is not enough to be done". Refactor when you touch code. https://refactoring.com/
- **Quality is cheaper at fleet speed:** internal quality lowers the cost of future change and the payoff line arrives in weeks, not months. Cruft concentrates in hot areas, so hot areas get zero tolerance. https://martinfowler.com/bliki/DesignStaminaHypothesis.html · https://martinfowler.com/bliki/TechnicalDebt.html
- **Rule of three; no long forks.** Large changes stay reversible through an abstraction layer with a demolition date; flags die with their code. Merges are easy but *semantic* conflicts are not, so merge constantly. Agents copy and paste at the third repetition — nobody refactors without a nudge. https://martinfowler.com/bliki/BranchByAbstraction.html · https://martinfowler.com/bliki/SemanticConflict.html · https://martinfowler.com/articles/sensors-for-coding-agents.html

### Building Evolutionary Architectures (Ford, Parsons, Kua) — http://evolutionaryarchitecture.com/

- **A fitness function is an objective integrity assessment** of some characteristic — a measure, not a rule, and broad in mechanism: metrics, tests, monitors.
- **Graded and re-tuned:** functions are prioritised key / relevant / not relevant and reviewed periodically so each one's scale can move; a weekly success-rate report gauges "health, cadence".
- **Explicitly not a stick:** a chapter is titled "Fitness Functions as a Checklist, Not a Stick". Dependency drift is tracked to see "whether a potential issue is getting better or worse". https://martinfowler.com/articles/evo-arch-forward.html

### Felix Rieseberg — https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/

- **Ambition is altitude, depth and range, not speed.** "What do you want to happen next?" changes the workflow; the rawest available material is the starting point.
- **Never self-judge:** use an outside judge the agent can run right now, and add an adversarial crew member whose success is proving the code is bad.
- **A fleet of ~60 parallel threads on one shared folder:** modularity decided up front so threads do not collide, shared written memory instead of re-briefing, QA threads that drive the app. Small per-change regressions are invisible to reviewers, so thresholds must sit above the noise floor. https://felixrieseberg.com/made-by-mechanical-means/

> "I want a deeper version of this task, not a bigger one."

### How fast teams avoid rot

- **Ratchet, don't block:** the boundary checker freezes today's violations and rejects only *new* ones, so the list is a work queue that only shrinks. Ownership lives in the package definition; cycles are rejected. https://shopify.engineering/enforcing-modularity-rails-apps-packwerk
- **Large-scale change is sharded, tooled, reversible:** above a few hundred edits, learn the change-generation tools; each shard is independently testable and revertible; a check flags any *new* use of a symbol the change removed. Deprecations get a deadline and backsliding prevention, because "code is a liability, not an asset". https://abseil.io/resources/swe-book/html/ch22.html · https://abseil.io/resources/swe-book/html/ch15.html · https://abseil.io/resources/swe-book/html/ch20.html
- **Dead code is deleted by machine, at symbol level,** using static graphs plus runtime usage data, because static analysis alone misses dynamically referenced code; false positives are the worse failure. Rank hotspots by churn × complexity and judge by direction, not score: each gets fix-now / supervise / no-problem, and a suppressed one re-raises on sudden degradation. https://engineering.fb.com/2023/10/24/data-infrastructure/automating-dead-code-cleanup/ · https://codescene.com/blog/technical-debt-examples-prioritizing-tech-debt-in-react
- **Flags die on a schedule,** and agents are contained rather than trusted: disposable warm boxes, deterministic nodes mixed with agent loops, lint feedback run inside the agent's environment. https://linear.app/now/linear-agent-bug-fix · https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2 · https://vercel.com/blog/building-a-software-factory-for-ai-sdk

### AI-written codebases, 2024–2026

- **The failure is measured:** agents produce ~1.87× more semantic redundancy than humans, and reviewers respond *more* positively to agent pull requests. Duplicate chains climb to about half by the fifth turn — pass rate is blind to rot. https://arxiv.org/html/2601.21276
- **The cause is retrieval, not discipline, and the convention file is the map.** Showing an agent its own history barely helps; what helps is a map of what already exists, where it lives, what it is called. `AGENTS.md` is a standard read by most agent tools, layered per directory with the nearest file winning — each directory's owner maintains its file. Keep it concrete and small, and remember it is context, not enforcement; that is what hooks are for. https://agents.md/ · https://code.claude.com/docs/en/large-codebases
- **Parallelism has a price and rot accelerates:** replayed merges of real agent pull requests show a 19.8% conflict rate within one fleet, 41.7% across fleets, ~42% of them structural. By 2026 the moved-code share fell from 21% to under 4%. https://arxiv.org/pdf/2607.04697 · https://www.gitclear.com/write_only_mode_ai_research

---

## Ten practices for an agent fleet

Each: what an agent does, and the number that shows it working — a trend, never a merge blocker.

1. **One commit, one kind.** Split the agent's work into a behaviour commit and a structure commit. *Signal:* mixed-commit share.
2. **Tidy only what the next change needs.** One small structure-only commit per area; a list for the rest, no cleanup branch. *Signal:* median structure-commit size.
3. **Third copy consolidates.** Fold the third occurrence into the existing implementation; a detector prompts "look it up first" at two. *Signal:* duplicate-block rate.
4. **An architecture map per area.** Briefs name area, owner, seams and the implementations to extend, and link a generated map. *Signal:* share of features extending a module.
5. **One writer per hotspot file.** Routes, schemas and type definitions have one owner per cycle; others add via a new file. *Signal:* structural conflict rate.
6. **One expensive check per project.** Type check and full suite run once, on a lock; the result is reused. *Signal:* wait time per merge.
7. **Delete by moving, where the signals point.** Rank areas by churn × complexity and direction; a rotating slot moves dead code, flags and endpoints aside in the worst one. *Signal:* dead-entity count.
8. **Small landings, constant merging.** No rewrite; a migration goes through an abstraction layer with a demolition date. Land small and often; the suite catches semantic conflicts. *Signal:* biggest diff; oldest branch.
9. **Rot as a trend board.** Keep a history of every structural metric and plot it; thresholds may ratchet one notch with a reason. *Signal:* the board's slope.
10. **An outside judge.** Fresh-context reviewer, adversarial agent, or a real run — never self-assessment. *Signal:* defects caught by the judge.

---

## Testing the starting points against the sources

| Starting point | What the sources say | Sharpest caveat |
|---|---|---|
| Tidy the code you touch, in a separate small commit | Strongly supported: Beck's one-kind rule; Fowler's "leave it better than you found it" | Beck wants tidying *before* the change when the payoff is immediate, and agents need the explicit nudge — nobody refactors at the third repetition unprompted |
| Rule of three consolidates | Supported by Fowler | The evidence says *two* for agents: by the fifth turn half of task chains re-implement. Second = "go and look", third = consolidate |
| One builder slot in five for cleanup, ranked by real signals | Half supported: the ranking (churn × complexity, direction) is attested; no source sets a ratio | Closest precedent is the opposite shape — a three-week freeze to burn down a backlog. Better: a cleanup *queue* with a target, not a fixed tax |
| Architecture map per area, cited in briefs | Well supported: per-directory convention files with the nearest winning; a map beats a summary | Scope it per area and keep it short, or it becomes noise and gets ignored |
| Delete-by-moving on a cadence | Supported: machine detection at symbol level, behaviour-based flag detection, archiving as part of done | Delete only what a trusted detector says is dead, and clear existing violations before switching a new check on |
| Small landed refactors, never big rewrites | Supported, with one distinction | Never a big *rewrite*; a big *migration* is fine when sharded, tool-generated, individually revertible, with a demolition date |
| Rot signals tracked as a trend | Best supported: fitness functions as monitoring, the "checklist not a stick" warning, sensor histories read as slopes, hotspots judged by direction | Disagreement is scope only — what to enforce is the deterministic, low-false-positive class, which can run inside the agent's loop |
| Where the sources and our method disagree | The corpus consensus is a merge gate with human attention, which our method drops | Keep the deterministic checks as in-session sensors the agent must satisfy before reporting done; put judgement-heavy concerns on the trend board |
