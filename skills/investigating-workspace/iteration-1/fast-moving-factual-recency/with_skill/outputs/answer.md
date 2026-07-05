# Claude Model IDs — Current as of June 9–10, 2026

## Answer

For a tool-calling agent, **`claude-sonnet-4-6`** is the recommended default. Anthropic's own model selection matrix calls it out specifically for "agentic tool use" and it hits the sweet spot of speed + intelligence at $3/$15 per MTok. If your agent runs complex, long-horizon tasks where accuracy matters more than cost, use **`claude-opus-4-8`** instead. The brand-new **`claude-fable-5`** (launched June 9, 2026) is the most capable model available but costs 3x more than Sonnet and is best saved for the most demanding reasoning/agentic workloads.

---

## Key Findings

1. **The model family is now "Claude 4.x" generation — not "3.5" or "3.7"** — those blog posts are outdated. The 3.x generation was fully superseded. `claude-3-5-sonnet` and `claude-3-7-sonnet` are old names. [Confidence: high]
   - Refutation attempt: searched for regressions/issues in claude-sonnet-4-6 for tool calling — zero results, no known issues.

2. **A new top tier was released on June 9, 2026: Claude Fable 5 (`claude-fable-5`) and Claude Mythos 5 (`claude-mythos-5`)**. These are not "Claude 4" models — they're a new naming scheme ("Fable 5"). `claude-mythos-5` is invitation-only (Project Glasswing). [Confidence: high — sourced from official launch docs dated June 9, 2026]

3. **Starting with Claude Opus 4.7, model IDs dropped date suffixes for current releases**. `claude-sonnet-4-6` is a pinned snapshot (not an evergreen alias). Older models like `claude-sonnet-4-5-20250929` still use date suffixes. [Confidence: high — from official versioning note on models/overview page]

4. **`claude-sonnet-4-20250514` and `claude-opus-4-20250514` are deprecated and retire June 15, 2026** — if you're on either of these, migrate now. [Confidence: high — from deprecation warning on official docs]

5. **Anthropic explicitly lists Sonnet 4.6 for "agentic tool use"** in the model selection matrix alongside Opus 4.8 for "agentic coding". The distinction: Sonnet for general agent+tool pipelines; Opus for multi-hour autonomous or high-autonomy work. [Confidence: high — from "choosing-a-model" page]

---

## Current Model IDs (Complete List)

### Generally Recommended / Latest Generation

| Model Name | API Model ID | Tier | Best For | Price (input/output MTok) |
|---|---|---|---|---|
| Claude Fable 5 | `claude-fable-5` | Frontier (new) | Most demanding reasoning + long-horizon agents | $10 / $50 |
| Claude Mythos 5 | `claude-mythos-5` | Frontier (invite-only) | Same as Fable 5, no safety classifiers | $10 / $50 |
| Claude Opus 4.8 | `claude-opus-4-8` | Opus | Complex reasoning, agentic coding, high-autonomy | $5 / $25 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Sonnet | **Agentic tool use, code gen, data analysis** | $3 / $15 |
| Claude Haiku 4.5 | `claude-haiku-4-5` (alias) / `claude-haiku-4-5-20251001` (pinned) | Haiku | Real-time, high-volume, sub-agent tasks, cost-sensitive | $1 / $5 |

### Legacy (Still Available, Migrate Soon)

| Model Name | API Model ID |
|---|---|
| Claude Opus 4.7 | `claude-opus-4-7` |
| Claude Opus 4.6 | `claude-opus-4-6` |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` (alias) / `claude-sonnet-4-5-20250929` (pinned) |
| Claude Opus 4.5 | `claude-opus-4-5` (alias) / `claude-opus-4-5-20251101` (pinned) |

### Deprecated (Retire June 15, 2026)

- `claude-sonnet-4-20250514` (alias: `claude-sonnet-4-0`)
- `claude-opus-4-20250514` (alias: `claude-opus-4-0`)

### Also Deprecated (Retire August 5, 2026)

- `claude-opus-4-1-20250805` (alias: `claude-opus-4-1`)

### AWS Bedrock IDs (for the three main current models)

| Model | Bedrock ID |
|---|---|
| Claude Opus 4.8 | `anthropic.claude-opus-4-8` |
| Claude Sonnet 4.6 | `anthropic.claude-sonnet-4-6` |
| Claude Haiku 4.5 | `anthropic.claude-haiku-4-5-20251001-v1:0` |

---

## Tool Calling Recommendation Decision Tree

```
Is your agent long-horizon / multi-hour / high-autonomy?
  YES → claude-opus-4-8 (effort: xhigh recommended)
  NO  → Is it high-volume / latency-sensitive / cost-sensitive?
          YES → claude-haiku-4-5
          NO  → claude-sonnet-4-6  ← DEFAULT
```

Anthropic's own docs call out Sonnet 4.6 specifically for "agentic tool use" in the model selection matrix. Haiku 4.5 is explicitly recommended for "sub-agent tasks" in multi-agent pipelines, making it a strong choice for leaf nodes in an orchestration tree.

For Claude Fable 5: it supports the memory tool and tool result clearing (context editing beta), so tool calling works, but it has safety classifiers that return `stop_reason: "refusal"` — you'll need to handle that in your agent loop. It's also 3x Sonnet's cost.

---

## Contradictions and Surprises

- **Naming scheme break**: Claude 4.x used "Opus/Sonnet/Haiku" naming. The new generation dropped that entirely — "Claude Fable 5" and "Claude Mythos 5" are new names with no tier mapping. This will cause confusion if you're following old blog posts.
- **"claude-sonnet-4-6" is a pinned snapshot, not an alias**: Starting with the 4.6 generation, dateless IDs are snapshots too. This is a change from earlier behavior where dateless IDs (like `claude-sonnet-4-0`) were aliases pointing to a dated version.
- **Haiku 4.5 is the only current model with a date in its primary ID** (`claude-haiku-4-5-20251001`), while also having a dateless alias (`claude-haiku-4-5`). Both are pinned to the same snapshot.
- **Claude 3.x generation**: Completely absent from the current model list except `claude-3-haiku-20240307`, which is deprecated (EOL April 20, 2026). If you're still using any `claude-3-*` IDs, you're already past or near end-of-life.

---

## Sources

- [Models overview — platform.claude.com](https://platform.claude.com/docs/en/docs/about-claude/models/overview) — verified June 10, 2026
- [Choosing the right model — platform.claude.com](https://platform.claude.com/docs/en/docs/about-claude/models/choosing-a-model) — verified June 10, 2026
- [Introducing Claude Fable 5 and Claude Mythos 5 — platform.claude.com](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) — dated June 9, 2026
- Context7 Claude API docs (`/llmstxt/platform_claude_llms_txt`) — indexed from `platform.claude.com`, verified June 10, 2026

---

## Open Questions

- No publicly documented benchmark comparisons between Sonnet 4.6 and Fable 5 specifically on tool-calling accuracy (function selection correctness, argument generation) — worth checking the Anthropic model card or evals page if that matters for your use case.
- `claude-fable-5` has a new tokenizer (introduced with Opus 4.7) that produces ~30% more tokens for the same text compared to pre-4.7 models. If you're migrating a prompt-heavy agentic system from Sonnet 4.5 or earlier to Fable 5, expect higher token counts.
