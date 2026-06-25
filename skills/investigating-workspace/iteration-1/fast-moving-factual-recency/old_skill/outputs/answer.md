## Answer

As of June 9, 2026, the current Claude model IDs are in three active tiers (Opus, Sonnet, Haiku) plus a brand-new top-tier family (Fable/Mythos) that launched today. For an agent that mostly does tool calling, **`claude-sonnet-4-6`** is the official recommended default — described by Anthropic as "frontier intelligence at scale, built for coding, agents, and enterprise workflows" with "agentic tool use" listed explicitly as a primary example. Opus 4.8 is the step up if you need maximum reasoning capability at higher cost.

---

## Key Findings

1. **Blog posts are almost certainly outdated.** The naming scheme changed significantly with the 4.6 generation (June 2025+). Before that, IDs had dates baked in (`claude-sonnet-4-5-20250929`). From 4.6 onward, IDs are dateless (`claude-sonnet-4-6`). Anything citing `claude-3-7-sonnet`, `claude-3-5-sonnet`, or `opus-4-20250514` is from the old scheme. [Confidence: high, from official versioning docs]

2. **`claude-fable-5` launched today (June 9, 2026).** This is now Anthropic's most capable widely released model. It uses a new naming scheme entirely (not Opus/Sonnet/Haiku). If blog posts mention it and predate this date, they were referencing a preview. It's genuinely brand new. [Confidence: high]

3. **Dateless IDs are pinned snapshots, not evergreen pointers.** A critical misconception: `claude-sonnet-4-6` is NOT an alias that updates to the next sonnet. It is a fixed snapshot. This changed from the old behavior where `claude-sonnet-4-5` WAS an alias pointing to the latest dated snapshot. Starting with 4.6, dateless = pinned. [Confidence: high, from official model-ids-and-versions page]

4. **`claude-opus-4-20250514` is deprecated.** The original Claude Opus 4 and Sonnet 4 (both dated May 2025) have been announced for deprecation and retirement. Do not use these. [Confidence: high, from API release notes]

---

## Current Model IDs (Claude API)

| Model | Claude API ID | Best for | Pricing (input/output per MTok) |
|---|---|---|---|
| **Claude Fable 5** | `claude-fable-5` | Most demanding reasoning, long-horizon agents | $10 / $50 |
| **Claude Mythos 5** | `claude-mythos-5` | Same as Fable 5 but no safety classifiers; invite-only via Project Glasswing | $10 / $50 |
| **Claude Opus 4.8** | `claude-opus-4-8` | Complex reasoning, high-autonomy agentic coding, computer use | $5 / $25 |
| **Claude Sonnet 4.6** | `claude-sonnet-4-6` | **Best default for tool-calling agents** — speed + intelligence balance | $3 / $15 |
| **Claude Haiku 4.5** | `claude-haiku-4-5-20251001` (or alias `claude-haiku-4-5`) | Fast, cheap, sub-agent tasks, high-volume | $1 / $5 |

**Bedrock IDs:** prefix `anthropic.` (e.g., `anthropic.claude-sonnet-4-6`). Haiku still has `-v1:0` suffix on Bedrock.
**Vertex AI IDs:** same as Claude API for 4.6+. Haiku uses `@` date notation: `claude-haiku-4-5@20251001`.

---

## For Tool-Calling Agents Specifically

The official "choosing a model" matrix lists Sonnet 4.6 explicitly for "agentic tool use." The specific guidance:

- **Default recommendation: `claude-sonnet-4-6`** — explicitly listed for code generation, data analysis, content creation, and agentic tool use. Best cost/performance balance.
- **Step up to `claude-opus-4-8`** if you need multi-hour autonomous coding agents, large-scale refactoring, or complex systems engineering. Default effort level is `high`; use `xhigh` for the most demanding agentic work.
- **Step up to `claude-fable-5`** for the most demanding long-horizon agentic tasks (launched today; $10/$50 — 3x Sonnet cost).
- **Step down to `claude-haiku-4-5`** for sub-agent tasks, high-volume tool dispatch, or cost-sensitive work where near-frontier intelligence is enough.

A useful lever before switching models: the **`effort` parameter** on Opus 4.8 and Sonnet 4.6 lets you trade intelligence for latency/cost within a single model. Tuning effort is often a better lever than jumping to a different model tier.

---

## Why Blog Posts Are Confusing

Three overlapping things create the noise:

1. **Two generations of naming schemes.** Pre-4.6 models have dates in the ID; 4.6+ do not. Blog posts mixing both look inconsistent but are technically correct for their era.
2. **Aliases that used to be evergreen.** `claude-sonnet-4-5` once pointed to "latest sonnet 4.5 snapshot" — some blogs relied on this behavior. That pointer concept is gone for 4.6+ models; the ID IS the snapshot.
3. **Claude Fable 5 is a brand-new naming family.** The Opus/Sonnet/Haiku family name scheme was the norm for Claude 1–4. "Fable" and "Mythos" are a new class above them. Any blog post that doesn't mention Fable is from before today (June 9, 2026).

---

## Sources

- [Models overview — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/overview) — primary source for all current model IDs and pricing
- [Choosing a model — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) — official selection matrix and agent recommendations
- [Model IDs and versioning — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions) — dateless ID behavior, pinned vs alias explanation
- [Introducing Claude Fable 5 and Claude Mythos 5 — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) — launch details, API changes, availability
- Anthropic SDK TypeScript CHANGELOG (via Context7) — confirmed `claude-opus-4-8` as of SDK 0.100.0 (May 28, 2026)

---

## Contradictions & Surprises

- **Haiku 4.5 still uses a dated ID** (`claude-haiku-4-5-20251001`) while Sonnet 4.6 and Opus 4.8 are dateless. This is not an inconsistency — Haiku 4.5 shipped before the 4.6 generation cutoff, so it got the old format. There is no Haiku 4.6 yet.
- **Claude Fable 5 does NOT support extended thinking**, unlike Sonnet 4.6 and Haiku 4.5. Instead it uses "adaptive thinking" which is always on. This matters if you're currently using extended thinking — it requires a small migration.
- **Fable 5 has a refusal mechanism** that returns `stop_reason: "refusal"` as a 200 (not an error). If you switch from Opus 4.8 to Fable 5 for agents, you need to handle this new stop reason.
- **Opus 4.8 defaults to `effort: high`** everywhere including the Messages API, not just Claude Code. Set it explicitly if you want a different level.

---

## Open Questions

- No Haiku 4.6 exists yet — it's unclear when Anthropic will update the Haiku tier to the dateless format.
- Claude Fable 5 is brand new (today); real-world tool-calling benchmarks and community feedback on agent quality vs. Opus 4.8 don't exist yet.
- Fable 5 has a 30-day data retention requirement and is not available under zero data retention — relevant if you're in a compliance-sensitive deployment.
