# Model Selection Reference

Current as of June 2026. Verify pricing at platform.claude.com/pricing.

## Available Models (Claude 4.x)

| Model | ID | Input/Output (per M tokens) | Best For |
|-------|----|---------------------------|----------|
| Opus 4.8 | claude-opus-4-8 | $5 / $25 | Frontier reasoning, architecture, code review |
| Opus 4.7 | claude-opus-4-7 | $5 / $25 | Default for agentic coding (xhigh effort default) |
| Sonnet 4.6 | claude-sonnet-4-6 | $3 / $15 | Balanced: code gen, analysis, tool use (high effort default) |
| Haiku 4.5 | claude-haiku-4-5-20251001 | $1 / $5 | Fast: classification, extraction, routing |

When building AI applications, default to the latest and most capable Claude models.

## Adaptive Thinking (Claude 4.x)

The 4.x line uses **adaptive thinking** — Claude decides when and how much to think based on the configured `effort` and the query. This replaces manual `budget_tokens` (deprecated on 4.6, returns 400 on 4.7+) and most "think step by step" scaffolding (no longer load-bearing on 4.x).

| Effort | When to use | Notes |
|---|---|---|
| `max` | Intelligence-demanding tasks | Risk of overthinking simple work |
| `xhigh` (4.7+) | Best default for most coding and agentic tasks | Opus 4.7 default |
| `high` | Minimum for intelligence-sensitive work | Sonnet 4.6 default |
| `medium` | Cost-sensitive workloads | |
| `low` | Latency-sensitive, scoped, non-intelligence-sensitive | Opus 4.7 strictly scopes to what's asked — won't go above and beyond |

## Selection Heuristics

| Task Type | Model | Why |
|-----------|-------|-----|
| Orchestrator agent | Opus 4.7+ or Sonnet 4.6 | Needs complex reasoning for delegation |
| Code generation | Sonnet 4.6 or Opus 4.7 | Sonnet for balance, Opus for hard cases |
| Code review | Opus 4.7+ | Catches subtle issues; ~11pp better bug-finding recall than prior generation |
| Data extraction | Haiku 4.5 | Fast, cheap, accurate for structured tasks |
| Classification / routing | Haiku 4.5 | Low latency for high-volume decisions |
| Tool-heavy workflows | Sonnet 4.6 | Reliable tool calling, good cost efficiency |
| Long-running tasks | Sonnet 4.6 default, Opus 4.7+ for critical paths | Cost control with quality where it matters |
| **Long-context retrieval (>200K)** | **Opus 4.6 or Sonnet 4.6** | Opus 4.7 has a documented retrieval regression at very long context (third-party MRCR benchmark); use prior gen for retrieval-heavy 1M-context workloads |

Default to Sonnet. Upgrade to Opus for tasks where reasoning quality directly impacts correctness. Downgrade to Haiku for high-volume, low-complexity subtasks.

## Multi-Model Strategy

Use different models for different stages:

```
Haiku (triage/classify) -> Sonnet (execute) -> Opus (review/validate)
```

Optimizes cost and latency while preserving quality where it matters.

## Model-Specific Prompting Notes

### Opus 4.7
- **More literal instruction following.** Doesn't silently generalize from one item to another. State scope explicitly when you want broad application.
- **Less tool use by default.** Raise effort to increase tool usage rather than rephrasing the prompt.
- **Fewer subagents by default.** Steer with explicit guidance ("Spawn multiple subagents in the same turn when fanning out").
- **More proactive progress updates.** Remove old "summarize progress every N tool calls" scaffolding — now redundant.
- **Persistent design aesthetic** for generated UI (warm cream / serif / terracotta). For different visuals, supply concrete alternative specs.

### Opus 4.6
- Does significantly more upfront exploration. Remove blanket "use this tool by default" instructions.
- Excessive subagent use can be reined in with explicit "Use subagents when tasks can run in parallel..." guidance.

### Sonnet 4.6
- Defaults to `high` effort. Sonnet 4.5 had no effort parameter; raising effort on 4.6 gives more reasoning headroom.

## In Claude Agent SDK

```typescript
// Agent-level model + effort override
agents: {
  "reviewer": {
    model: "opus",
    // effort is set at the top-level options or via the API call
  }
}
```

In skills, use the frontmatter field: `model: sonnet` (or `model: opus`/`model: haiku`).

## Cost Awareness

Multi-agent systems use around 15x more tokens than single agents. Three factors explain 95% of performance variance: token usage (80%), tool calls (15%), model choice (5%).

**Model selection matters least among these factors. Optimize token efficiency, prompt caching, and tool design first.**

## Self-host vs API

For workloads that fit a 70B-class open-weight model with good batching (vLLM continuous batching + prefix caching + FP8 quantization), self-hosting can cost ~$0.20-0.50 per million output tokens vs ~$10-25/M output on frontier APIs. Break-even is roughly $10K-$100K/month in API spend, depending on the operational tax (serving stack, KV memory tuning, batching tuning, model updates, GPU on-call). Below that, the API is the right answer.
