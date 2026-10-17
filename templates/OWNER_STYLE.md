# Writing to the owner: the house style

Sources: communication patterns from high-velocity teams and distributed leadership. This page is the short version every agent uses. It governs how we *say* things, never how much we check.

## The rules
- **Line one is the answer.** The status, the result or the ask. Someone who reads only line one has it.
- **Least that fully answers, then stop.** No preamble, no narration of effort, no closing summary.
- **One point per line.** Bold the lead-in so the bold alone carries the message.
- **Numbers over adjectives.** "26/30 pass, 4 fail on one missing file", not "mostly passing".
- **Status words are exact.** Built ≠ tested ≠ merged ≠ live. Cause confirmed ≠ suspected.
- **Plain words.** Translate a tool or term the first time, in five words or fewer. No tool names in the UI.
- **Never drop a risk or a blocker to be short.** It gets its own line.
- **One labelled ask, last.** Say what happens if the owner doesn't answer (full auto never waits).
- **Depth on request.** "Walk me through it" switches brevity off for that reply.
- **Never invent status.** Unknown is written as unknown, with what would settle it.

## Shapes
**Status recap (orchestrator, status command):** the brief format.
```
TL;DR: <one line: what changed, any blocker>
✅ <done>   🟡 <in progress>   ⬜ <not started>   🔴 <blocker or risk>
Your move: 1. <pick>  2. <pick>   (or: nothing needed)
```
**Board card (work tracking):** title at most 70 characters, next step at most 110 (the tool enforces limits). Detail goes in the linked file.
**Dev desk review:** ask (one line) · why (2–4 bullets) · options with one recommended · if you don't answer · then details.
**Lead → orchestrator (inbox):** `<time> · <thread> · <one-line headline>`, then at most 4 bullets. A long investigation goes in a file and gets linked.
