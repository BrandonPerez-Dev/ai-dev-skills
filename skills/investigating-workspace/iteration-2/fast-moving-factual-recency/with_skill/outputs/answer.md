---
Question:   What are the current Claude model IDs and which should be the default for a tool-calling agent?
Domain:     Technical
Strategy:   Official Anthropic platform docs (primary) → Anthropic SDK TypeScript/Python source on Context7 (ground truth) → choosing-a-model guidance page; blog posts and training-data recall explicitly excluded
Hypothesis: claude-3-5-sonnet-20241022 is stale; a claude-4 generation or newer is current; Sonnet-tier is likely the recommended default for tool-calling work
Done when:  Complete canonical model ID list verified from official docs + SDK source, tool-calling recommendation triangulated from 2+ independent official sources, versioning semantics clarified
---

## Answer

As of June 10, 2026, the current generally available Claude models are **Claude Fable 5** (`claude-fable-5`, launched June 9 2026), **Claude Opus 4.8** (`claude-opus-4-8`), **Claude Sonnet 4.6** (`claude-sonnet-4-6`), and **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`). For a tool-calling agent, Anthropic explicitly recommends starting with **`claude-sonnet-4-6`** — it is listed under "agentic tool use" in the model selection matrix and is the model used in official tool-calling SDK examples. Upgrade to `claude-opus-4-8` or `claude-fable-5` only if your agent requires complex multi-step reasoning or long-horizon autonomy that Sonnet cannot handle.

---

## Key Findings

1. **Claude Fable 5 launched June 9, 2026** — `claude-fable-5` is now Anthropic's most capable widely released model. It targets "the most demanding reasoning and long-horizon agentic work." Adaptive thinking is always on; extended thinking is not supported. Priced at $10 input / $50 output per MTok. [Confidence: high]
   - Refutation attempt: Checked whether Fable 5 has any tool-calling-specific limitations. Finding: no tool-calling restrictions documented, but it includes safety classifiers that can return `stop_reason: "refusal"` — a new integration concern not present in Opus/Sonnet models. This is a real cost and complexity tradeoff for tool-calling agents.

2. **Claude Sonnet 4.6 is Anthropic's explicit recommendation for agentic tool use** — The "Choosing a model" page lists its primary use cases as: "Code generation, data analysis, content creation, visual understanding, **agentic tool use**." The Python SDK `tools.md` and `helpers.md` examples use `claude-sonnet-4-5-20250929` and `claude-sonnet-4-20250514` for tool runner and MCP tool integration examples — the Sonnet tier has been the SDK team's tool-calling default across generations. [Confidence: high — triangulated from docs page + SDK source]

3. **The versioning scheme changed at generation 4.6** — Before 4.6, model IDs included a date (`claude-sonnet-4-5-20250929`). Starting with 4.6, the dateless format (`claude-sonnet-4-6`) is the canonical pinned snapshot, not an alias. Blog posts and tutorials that show `claude-3-5-sonnet-20241022` or `claude-3-opus-20240229` are referencing models from 2–3 generations ago. [Confidence: high — direct from model-ids-and-versions doc]

4. **`claude-sonnet-4-6` and `claude-opus-4-8` have dateless IDs that are pinned snapshots, not evergreen pointers** — A common misconception (noted explicitly in official docs) is that dateless IDs auto-update. They do not. Anthropic ships updates under new IDs. [Confidence: high]

5. **Haiku 4.5 is the right choice for sub-agent tasks, not top-level orchestration** — The docs explicitly slot Haiku for "sub-agent tasks" and "high-volume, straightforward tasks." For an agent that mostly calls tools and needs to reason about when and how to call them, Haiku is likely underpowered as the primary model.

---

## Model ID Reference (as of June 10, 2026)

### Currently active models

| Model name | Claude API ID | Context | Max output | Input / Output MTok |
|---|---|---|---|---|
| Claude Fable 5 | `claude-fable-5` | 1M | 128k | $10 / $50 |
| Claude Opus 4.8 | `claude-opus-4-8` | 1M | 128k | $5 / $25 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M | 64k | $3 / $15 |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | 200k | 64k | $1 / $5 |
| Claude Mythos 5 | `claude-mythos-5` | 1M | 128k | $10 / $50 (invite-only via Project Glasswing) |
| Claude Mythos Preview | `claude-mythos-preview` | — | — | invite-only |

All 4.6+ IDs are also valid on Bedrock (prefix `anthropic.`) and Vertex AI.

### Stale / legacy IDs seen in blog posts — DO NOT use as defaults

- `claude-3-5-sonnet-20241022` — Claude 3.5 generation, two major generations old
- `claude-3-opus-20240229` — Claude 3 generation, three generations old
- `claude-3-5-haiku-20241022` — Claude 3.5 generation, replaced by 4.x Haiku
- `claude-sonnet-4-5` / `claude-sonnet-4-5-20250929` — Previous Sonnet generation; still valid but superseded by 4.6
- `claude-opus-4-5`, `claude-opus-4-6`, `claude-opus-4-7` — Superseded by 4.8

The SDK `Model` type union (pulled from `anthropic-sdk-typescript` source as of this investigation) includes the full list of valid identifiers back to `claude-3-haiku-20240307` for backward compatibility. Valid does not mean recommended.

### SDK default in tool-calling examples

The official Anthropic Python SDK `tools.md` uses `claude-sonnet-4-5-20250929` and `claude-sonnet-4-20250514` for `tool_runner` and MCP integration examples. These are the previous-generation Sonnet models. The current equivalent is `claude-sonnet-4-6`.

---

## Tool-Calling Agent Decision Matrix

| Agent profile | Recommended model | Reasoning |
|---|---|---|
| Standard tool-calling agent (most cases) | `claude-sonnet-4-6` | Explicitly recommended for "agentic tool use" in Anthropic's model selection matrix; best speed/intelligence tradeoff at $3/$15 per MTok |
| Multi-step, long-horizon agentic coding | `claude-opus-4-8` | Docs slot it for "multi-hour autonomous coding agents, complex systems engineering"; supports `xhigh` effort for coding/agentic work |
| Highest capability, cost not a constraint | `claude-fable-5` | Most capable widely released model; be prepared to handle `stop_reason: "refusal"` and implement fallback logic |
| High-volume sub-agents, simple routing | `claude-haiku-4-5-20251001` | Fastest, cheapest; Anthropic explicitly slots it for "sub-agent tasks" |

---

## Contradictions & Surprises

- **The hypothesis was partially wrong.** The current state is not a `claude-3-7` variant — Anthropic skipped that numbering. The naming jumped from `claude-3.x` to `claude-4.x` and then introduced `claude-fable-5` / `claude-mythos-5` as a new naming scheme for the frontier tier. Blog posts showing `claude-3-7` may be speculative or from a naming scheme that was not adopted.

- **The TypeScript SDK `Model` type includes `claude-opus-4-8`, `claude-opus-4-7`, `claude-mythos-preview`, `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`** — pulled directly from source. The SDK does not yet include `claude-fable-5` or `claude-mythos-5` in the type union as of this investigation, likely because the SDK snapshot predates June 9. However, the `(string & {})` catch-all means these IDs will work in practice.

- **Fable 5 has a new failure mode for tool-calling agents**: `stop_reason: "refusal"`. Other Claude models do not return this. If you deploy `claude-fable-5` as your agent model, you need explicit fallback handling — a non-trivial integration change that Sonnet 4.6 does not require.

- **Dateless IDs are not aliases.** This contradicts a widespread assumption seen in tutorials. `claude-sonnet-4-6` will not change when Sonnet 4.7 ships; it stays pinned. New Anthropic releases ship under new IDs.

---

## Sources

- [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) — Anthropic official docs, verified June 10, 2026
- [Choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) — Anthropic official docs, verified June 10, 2026
- [Model IDs and versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions) — Anthropic official docs, verified June 10, 2026
- [Introducing Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) — Anthropic official docs, verified June 10, 2026
- `anthropics/anthropic-sdk-typescript` — `src/resources/messages/messages.ts` `Model` type union, via Context7, reflects pre-June-9 SDK state
- `anthropics/anthropic-sdk-python` — `tools.md` and `helpers.md` tool runner examples, via Context7

---

## Open Questions

- When will the TypeScript and Python SDKs add `claude-fable-5` and `claude-mythos-5` to the typed `Model` union? (Currently only reachable via the `(string & {})` escape hatch.)
- Does Fable 5's adaptive thinking (always on) meaningfully increase latency or cost for agents that make many short tool calls in a loop? The docs note it is "always on" with no way to disable it — worth benchmarking for high-frequency tool use patterns.
- Sonnet 4.6 is listed as supporting extended thinking — is this beneficial or a footgun for tool-calling agents where you want deterministic, fast tool dispatch? Docs recommend the `effort` parameter to tune this.

---

## Promote to context/

If this finding is being used in an Arboreus or agent-building context, the following should become architectural truth:

- **Default agent model:** `claude-sonnet-4-6` — Anthropic's explicit recommendation for agentic tool use; $3/$15 per MTok; 1M context; 64k output
- **Versioning rule:** IDs from the 4.6 generation onward (`claude-sonnet-4-6`, `claude-opus-4-8`, etc.) are pinned snapshots, not aliases. Hardcode the full ID; do not assume dateless = evergreen.
- **Fable 5 caveat:** If upgrading to `claude-fable-5`, implement `stop_reason: "refusal"` handling and optionally wire the `fallbacks` parameter. Fable 5 is not a drop-in replacement for Opus/Sonnet in tool-calling agents.
