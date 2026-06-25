# Technical Research Strategy

For questions about code, APIs, libraries, architecture, debugging, and system design.

## Where the Signal Lives

| Source | Signal Quality | Use For |
|--------|---------------|---------|
| **Source code** (the actual codebase) | Highest — ground truth | How things actually work, not how docs say they work |
| **Tests** | High — executable documentation | Expected behavior, edge cases, contracts |
| **Official docs** (library/framework) | High but can lag behind code | API surface, intended usage patterns |
| **Type definitions / interfaces** | High — compiler-enforced contracts | Understanding data shapes and API contracts |
| **Git history** | High — reveals intent and evolution | Why decisions were made, when things changed |
| **Stack Overflow** (accepted + high-vote answers) | Medium — verify against current docs | Common problems and solutions, but answers age poorly |
| **GitHub Issues / Discussions** | Medium-high — real-world edge cases | Known bugs, workarounds, maintainer opinions |
| **Blog posts / tutorials** | Low-medium — varies wildly | Conceptual understanding, but verify code against current API |

## Search Strategy

### Match the question to the right approach:

- "What does this code do?" → codebase-focused, edge-first exploration
- "What's the best approach for X?" → web-focused, multiple perspectives, comparison
- "Why was this built this way?" → git history, commit messages, docs, ADRs
- "Is this pattern correct?" → web search for best practices + codebase comparison

### Codebase exploration (edge-first):

- Start from system boundaries: entry points, API routes, exports, event handlers
- Trace inward: follow imports, function calls, data flow
- Cycle between bottom-up (known APIs → callstacks → abstractions) and top-down (data structures → ownership → relationships)
- Read types and interfaces before implementations
- Read tests — they document expected behavior and edge cases

### Search strategy (multi-layer):

1. **Broad keyword search** — Glob for file patterns, Grep for terms across the codebase
2. **Structural refinement** — narrow using regex patterns, directory scoping
3. **Targeted reading** — deep-read files identified in steps 1-2, with `file:line` precision

### Documentation:

- Project docs: `README.md`, `ARCHITECTURE.md`, `docs/`, `.context/`
- Inline: JSDoc, comments on key interfaces and non-obvious logic
- Git history: recent commits on relevant files reveal intent and evolution

### Web research:

**Use SearXNG (`mcp__searxng__searxng_web_search`) as your primary search tool.** It aggregates 70+ engines (Google, Brave, DuckDuckGo, Reddit, etc.), returns more results than WebSearch, and catches GitHub issues, Reddit dev discussions, and community solutions that single-engine search misses. Runs locally with no rate limits.

**When to use which search tool:**
- **SearXNG** — primary for all web research. Better coverage across engines, surfaces Reddit dev threads and GitHub discussions that WebSearch misses.
- **WebSearch** — fallback if SearXNG is unavailable.
- **Context7** — for library documentation when available (more structured than search).
- **Playwright** — when you need to read full page content that WebFetch can't parse.

**Search tips:**
- Search for reference implementations, known issues, migration guides
- Look for multiple perspectives — not just the first Stack Overflow answer
- When initial results are too theoretical, follow up with implementation-specific searches

## Source Credibility (Technical)

Weight sources in this order:

1. **Source code and tests** — ground truth, always wins
2. **Official documentation** — authoritative but can be outdated
3. **GitHub issues from maintainers** — insider knowledge
4. **Stack Overflow (high-vote, recent)** — community-verified
5. **Blog posts** — useful for concepts, verify all code snippets
6. **AI-generated content / SEO articles** — lowest trust, cross-reference everything

**Key rule:** Code that runs > documentation that claims. If docs and code disagree, the code is right.

## Technical-Specific Guidelines

- **Start broad, narrow fast.** Glob first, then targeted reads.
- **Don't read everything.** Entry points, types, and tests first. Implementation details when needed.
- **Use Context7** for library docs instead of guessing at APIs.
- **Check version compatibility.** Solutions from 2 years ago may not work with current versions.
