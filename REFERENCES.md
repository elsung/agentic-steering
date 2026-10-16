# References

Status: **used** means the source was fetched and every claim we took from it is quoted from the fetched text. **Blocked** means we could not fetch it, so no claim in this repo relies on it.

| # | Source | Status | What we took from it |
|---|---|---|---|
| 1 | [Haiku 5.5 is 40x cheaper than Opus 5.5. Your Explore subagent is probably still running on Opus](https://www.reddit.com/r/ClaudeCode/comments/1x0kzbh/haiku_55_is_40x_cheaper_than_opus_55_your_explore/) (r/ClaudeCode) | used | Subagents silently inherit the large model. "Route by verifiability, not difficulty." Advisor spec, Haiku at high effort, trimming fresh-session tokens, mechanical checks, cross-family review, cost of timed wake-ups. |
| 2 | [I tested the "Haiku codes, Opus advises" setup… It was the most expensive of 5 setups](https://www.reddit.com/r/ClaudeCode/comments/1x5167d/i_tested_the_haiku_codes_opus_advises_setup/) (r/ClaudeCode) | used | Five-setup cost comparison on one real bug. The advisor's call rate dominates the bill. |
| 3 | [Haiku as main, Opus for subagents?](https://www.reddit.com/r/ClaudeCode/comments/1x11wj6/haiku_as_main_opus_for_subagents/) (r/ClaudeCode) | used | Discussion of the inverted layout. We chose the opposite: the large model steers, the small model executes. |
| 4 | [What Is Claude Code's Advisor Strategy? How to Use Opus as an Adviser With Sonnet or Haiku](https://www.mindstudio.ai/blog/claude-code-advisor-strategy-opus-sonnet-haiku) (MindStudio) | used | Background on the advisor pattern. |
| 5 | [Sonnet-main, Opus-advisor, Haiku-subagents](https://medium.com/@dan.avila7/sonnet-main-opus-advisor-haiku-subagents-splits-your-claude-code-session-across-three-models-1e9e96a47f26) (Medium) | blocked (403) | none |
| 6 | [Opus Plans, Haiku Executes: The Agent Cost Stack](https://dev.to/max_quimby/opus-plans-haiku-executes-the-agent-cost-stack-13h0) (dev.to) | used | Plan/execute split as a cost stack. |
| 7 | [Claude Code Advisor: Run Sonnet 5.5, Let Opus 5.5 Advise](https://www.vibecodingacademy.ai/blog/claude-code-advisor) (Vibe Coding Academy) | used | Background on the `--advisor` flag. |
| 8 | [How to Build a Coding Agent That Costs 80% Less](https://x.com/cyrilXBT/article/2108693524900110515) (X) | blocked (bot wall) | none |
| 9 | [Haiku 5.5 vs Jev: is Anthropic's Jev-killer about to make decision models obsolete?](https://medium.com/@itaispector1/haiku-5-5-vs-jev-is-anthropics-jev-killer-about-to-make-decision-models-obsolete-e25520bbe9f8) (Medium) | blocked (403) | none |
| 10 | [Anthropic's Haiku 5.5: Theo Browne Says It's Finally a Small Model Worth Using](https://finance.biggo.com/news/f6f440d7b101f382) (BigGo, recap of a Theo Browne video) | used | Pricing and the 100k cliff. Opus solo vs Opus + 10 Haiku. The "burns a million tokens" trap. Tool-error failure. Cache reads at 30–50% of the bill. A dedicated judge model for no-reasoning categorisation. |

## Official documentation

- [Subagents](https://code.claude.com/docs/en/sub-agents): `CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, and the per-agent `model` field.
- [Model configuration](https://code.claude.com/docs/en/model-config): model aliases and effort levels.
- [Environment variables](https://code.claude.com/docs/en/env-vars): `ANTHROPIC_MODEL`, `CLAUDE_CODE_EFFORT_LEVEL`, and the `CLAUDE_CODE_DISABLE_*` context trims.
