# Changelog: the Button Mash Method and skill

One entry per revision. Semantic versions:
- **patch**: wording;
- **minor**: a new guideline or worked example;
- **major**: a change of approach.

Each entry names the real incident or owner note that taught it.

## 1.2.0 (2026-10-20)

**Minor: a new steering line and a worked example (owner notes #530-#531).**

- **Keep the owner's view live.** When work supersedes something waiting on the owner (a review item, a card, a
  decision), archive it at once, with one line on what replaced it. When a newer write-up replaces an older one, mark
  the older one as superseded.
- **Taught by:** 36 items from earlier days sat in the owner's "needs you" list, all already superseded, and had to be
  cleared by hand.

## 1.1.0 (2026-10-20)

**Minor: a new steering line and two worked examples (owner note #525).**

- **Mash, but spend where it counts.** Burn tokens where they move the goal: the hard problem, the live blocker, the
  decision that unlocks others. Elsewhere use the cheapest capable model, short briefs with context and one agent per
  task. No duplicate work, no re-deriving what's known, no re-running long reports, and stop loops that make no
  progress.
- **Taught by:**
  - a judge that re-issued work on one stale shot for six rounds, while builders spent half an hour each finding
    nothing new;
  - long research handed to the expensive model by habit instead of the cheap reader.
- **Links** to the existing cost guidance in STEERING.md and PRACTICES.md instead of repeating it.

## 1.0.0 (2026-10-20)

The first versioned release of the method (BUTTON_MASH_METHOD.md) and the skill (skills/button-mash/SKILL.md).

**What the method is:** keep many agents moving hyper-aggressively toward the goal behind the ask, with assessment
loops (look at the real output against the intent), not evals, tests or gates, and iterate fast toward discovering and
refining what we want.

**The hard guidelines, each with its why in the skill:**
- never destroy the owner's work (move instead of delete);
- never spend or publish without the owner's OK;
- never stop someone's live work;
- while working toward a goal, push hard and never leave a run stuck without saying why;
- pace deliberately for power and heat, cost and rate limits;
- no gates;
- nothing private in public material.

**What changed on the way to 1.0.0:**
- **The method page was renamed** from METHOD_AGGRESSIVE.md, which now points to it, and it opens with the owner's
  definition.
- **Lessons 31-41 were added:**
  - order rules as priorities, not waits;
  - one owner per resource, and never hold one resource while waiting for another;
  - leave memory to its owner;
  - an idle resource with waiting goal work is a bug for a watcher to correct;
  - no gates;
  - replay real histories before changing the scheduler;
  - root fixes reach the live run at once, and services restart onto new code;
  - account switches cover background services;
  - limiting defaults are visible settings;
  - inherit, don't invent;
  - tell stale from important by owner and progress.
- **The skill was first written as rules, then reshaped** (owner notes #521-#522) into hard guidelines with their why,
  strong steering, and judgment taught by worked examples. The incidents behind the examples:
  - a builder that named a safe default and stopped anyway;
  - a take waiting for a draft that was never coming;
  - a merged fix that the pinned live run wasn't running;
  - an 11-minute control-loop pass;
  - a cleanup that went by path alone and stopped a live builder's runner;
  - an owner decision that was re-asked every round;
  - a "busy box" block.
- **"Never leave the GPU idle" became "push hard while working toward a goal"** (owner note #523). Idle capacity
  matters only when goal work waits for it; with no goal, idle is fine.
- **Today's measured results:**
  - a replay of real run histories took GPU idle time with runnable work from 2.9 h to 0, and deadlocks to 0;
  - the control loop's pass went from 11 min to under a minute.
