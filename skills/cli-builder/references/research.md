# CLI Design for AI Agents — Research Summary

**Date:** 2026-03-20
**Context:** Designing CLI tools for the agent platform to replace MCP servers. Researching optimal patterns for agent-callable CLIs.

---

## CLI vs MCP — Quantified

**Scalekit Benchmark** (25 runs, GitHub operations):
- CLI: 1,365–9,386 tokens/task, **100% success rate**
- MCP: 32,279–82,835 tokens/task, **72% success rate**
- MCP failure was TCP timeouts, but 10-30x token overhead is structural (schema bloat)
- Source: [scalekit.com/blog/mcp-vs-cli-use](https://www.scalekit.com/blog/mcp-vs-cli-use)

**Zechner Benchmark** (120 runs, debugging tasks):
- CLI: $0.39 avg cost
- MCP: $0.48 avg cost (29% more)
- Adding 800-token "skill doc" reduced tool calls by 1/3 and latency by 1/3
- Source: [mariozechner.at](https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/)

**Intune Case Study** (Reinhard):
- MCP: ~145,000 tokens for 50-device workflow
- CLI: ~4,150 tokens — **35x difference**
- Source: [jannikreinhard.com](https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/)

---

## Input Format: Flat Flags Beat Nested JSON

**Natural Language Tools Paper** (6,400 trials, 10 models, arxiv:2510.14453):
- JSON schema accuracy: **69.1%**
- Natural language/flat: **87.5%** (+18.4 pp)
- Open-weight models gained most: +26.1 pp
- Variance dropped 70% (more consistent)
- 31.4% fewer total tokens
- Mechanism: JSON forces simultaneous reasoning + format compliance, competing for capacity
- Source: [arxiv.org/abs/2510.14453](https://arxiv.org/abs/2510.14453)

**DeepJSONEval** (2,100 instances, 12 models, arxiv:2509.25922):
- Medium nesting (3-4 levels): reasonable accuracy
- Hard nesting (5-7 levels): **17-37% accuracy decline**
- Even best models (Claude Sonnet 4) only hit 57.9% strict accuracy on deepest nesting
- Source: [arxiv.org/html/2509.25922v1](https://arxiv.org/html/2509.25922v1)

**NESTful** (arxiv:2409.03797):
- Nested API call sequences substantially harder than flat for all models
- Source: [arxiv.org/html/2409.03797v3](https://arxiv.org/html/2409.03797v3)

**Implication:** `--customer 123 --item 456 --qty 2` beats `--json '{"CustomerRef":{"value":"123"}}'`

---

## Output Format: JSON Is Not Optimal

**Let Me Speak Freely?** (Tam et al., 2024, arXiv:2402.18442):
- JSON output reduced accuracy by **27.3 pp** on math tasks vs natural language
- Stricter constraints = greater degradation, consistently
- Source: [semanticscholar.org](https://www.semanticscholar.org/paper/7c394a8b4db70d7424abc300749fff0fe580bdae)

**ImprovingAgents Nested Format Benchmark** (GPT-5 Nano, Gemini 2.5 Flash, Llama 3.2):

| Format | Accuracy (GPT-5 Nano) | Tokens vs JSON |
|---|---|---|
| YAML | 62.1% | ~10% fewer |
| Markdown | 54.3% | 34-38% fewer |
| JSON | 50.3% | baseline |
| XML | 44.4% | ~80% more |

- Source: [improvingagents.com](https://www.improvingagents.com/blog/best-nested-data-format/)

**David Gilbertson TSV comparison:**
- JSON uses **2x tokens** and **4x generation time** vs TSV for tabular data
- Source: [medium.com](https://david-gilbertson.medium.com/llm-output-formats-why-json-costs-more-than-tsv-ebaf590bd541)

**TOON (Token-Optimized Object Notation)**:
- 40-60% fewer tokens than JSON for uniform tabular data
- 69% more accuracy per token spent
- Production case: 500-row table cost $1,940 (JSON) vs $760 (TOON) — 61% savings
- Source: [tensorlake.ai](https://www.tensorlake.ai/blog-posts/toon-vs-json)

**Anthropic's concise/detailed mode:**
- Detailed response: 206 tokens
- Concise response: 72 tokens — **3x reduction**
- Recommend `response_format` enum letting agent choose
- Source: [anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents)

---

## Tool Consolidation — Fewer Tools, Higher Success

**Berkeley Function Calling Leaderboard** (BFCL):
- Single-function calls: high accuracy across models
- Multi-step/parallel: "significantly underperform"
- Agents loop unproductively or demand already-provided credentials
- Source: [gorilla.cs.berkeley.edu](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html)

**Anthropic recommendation:**
- Replace `get_customer` + `list_invoices` + `list_notes` with single `get_customer_context`
- SWE-bench improvement came partly from tool consolidation
- Source: [anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents)

---

## Context Rot — Volume Degrades Performance

**Chroma Research** (18 models including Claude Opus 4, GPT-4.1, Gemini 2.5):
- 113K tokens context vs 300-token focused prompt: **30%+ accuracy drop**
- Effective capacity: 60-70% of advertised window
- Even single distractors reduce performance; effect amplifies
- Unused tool definitions are functionally distractors
- Content in the middle of long contexts is underweighted (lost-in-the-middle)
- Source: [research.trychroma.com/context-rot](https://research.trychroma.com/context-rot)

---

## Runtime Self-Documentation

**Google Workspace CLI pattern:**
- `gws schema <command>` returns machine-readable docs on demand
- Agent pays zero context cost for tools it doesn't query
- Source: [github.com/googleworkspace/cli](https://github.com/googleworkspace/cli)

**Anthropic Tool Search pattern:**
- Defer loading non-critical tools; agent pulls schema on demand
- 85% context reduction from on-demand loading
- Source: [anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## Design Principles (Evidence-Ranked)

### Strong Evidence
1. **Flat inputs over nested JSON** — 18.4 pp accuracy gain, 17-37% degradation from deep nesting
2. **Human-readable default output** — Markdown/tables use 34-38% fewer tokens with higher accuracy
3. **Consolidate operations** — multi-step chains have significantly higher error rates
4. **Minimize context footprint** — every unused token is a distractor
5. **Actionable error messages** — errors as tool results, not terminal states

### Moderate Evidence
6. **TOON/CSV for tabular data** — 40-60% fewer tokens (self-published benchmarks)
7. **Concise/detailed response modes** — 3x token reduction (Anthropic first-party)
8. **Runtime --help over pre-loaded docs** — 85% context reduction

### Directional
9. **No magic number for response size** — smaller/focused consistently beats large/comprehensive
10. **NDJSON vs JSON arrays** — no cognition difference, but NDJSON wins on streaming infra

---

## Application to Our CLI Design

For agent-callable CLIs (QuickBooks, Wex FSM, etc.):

**Input:** Flat flags by default, `--json` as escape hatch for complex creates
```
qbo invoices search --customer "Smith" --after 2026-01-01 --limit 10
# NOT: --json '{"CustomerRef":{"value":"123"},...}'
```

**Output:** Clean table/summary by default, `--json` or `--raw` for machine-readable
```
# Default output:
ID      Customer      Amount    Date        Status
1234    Smith LLC     $2,100    2026-03-15  Unpaid
1235    Smith LLC     $450      2026-03-01  Paid

# With --json:
{"Id":"1234","CustomerRef":{"value":"56"},...}
```

**Self-documentation:** `qbo invoices --help` returns usage, not pre-loaded into context

**Error messages:** "Customer 'Smithh' not found. Did you mean 'Smith LLC' (ID: 56)? Use `qbo customers search` to browse."

**Consolidation:** `qbo customer context 123` returns customer + recent invoices + balance in one call
