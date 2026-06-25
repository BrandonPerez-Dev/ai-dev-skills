---
name: readme
description: >-
  Write open-source README files for developer tools and projects. Use when
  creating a new README, rewriting an existing one, or adding documentation for
  a release. Covers CLI tools, Docker images, MCP servers, libraries, web apps,
  and multi-mode projects. Applies cognitive funneling, mode-specific patterns,
  and community-validated structure. Also triggers on: "write a readme",
  "document this project", "add a README", "open-source this".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# README

Show what the tool does before asking anyone to install it. Structure for the reader who hasn't decided yet.

<HARD-GATE>
Do NOT write a single line of the README until you have read the project. At minimum: the package manifest (Cargo.toml, package.json, pyproject.toml, go.mod), the entry point(s), any existing README or docs, and the project's spec/design docs if they exist. A README written from assumptions instead of project state is worse than no README — it teaches the wrong mental model.
</HARD-GATE>

## Mode Detection

READMEs for different project types follow fundamentally different patterns. Detect which mode(s) apply, then load the corresponding reference file(s).

| Signal | Mode | Reference |
|--------|------|-----------|
| Binary crate, `bin/`, CLI entry point, argument parser (clap, cobra, argparse, commander) | **CLI Tool** | [cli-mode.md](references/cli-mode.md) |
| Dockerfile, docker-compose.yml, container image published to registry | **Docker Image** | [references/docker-mode.md](references/docker-mode.md) |
| MCP server implementation, tools/list endpoint, stdio/SSE/streamable-http transport | **MCP Server** | [references/mcp-mode.md](references/mcp-mode.md) |
| `lib.rs`, `src/lib/`, npm package with exports, PyPI package | **Library / SDK** | [references/library-mode.md](references/library-mode.md) |
| HTTP server, frontend app, SaaS, web API | **Web App / API** | [references/webapp-mode.md](references/webapp-mode.md) |
| GitHub Action, Terraform module, Helm chart, plugin | **Infrastructure / Extension** | [references/infra-mode.md](references/infra-mode.md) |

Projects often span multiple modes (e.g., CLI + Docker + MCP). When multiple modes apply:
- **Read all relevant reference files** before drafting
- **Merge patterns** — don't repeat sections, integrate them (e.g., one Installation section with subsections per distribution method)
- **Lead with the primary mode** — the mode most users will encounter first

If no mode is obvious, ask the user.

## Process

### Phase 1: Understand the Project

Read the project to extract:

1. **What it does** — one sentence, concrete, naming the category and what it replaces/improves
2. **Who it's for** — the primary user persona
3. **How it's distributed** — which modes apply (CLI binary, Docker image, npm package, etc.)
4. **Key capabilities** — the 3-5 things it actually does, not aspirational features
5. **Configuration surface** — env vars, config files, flags, profiles
6. **Security considerations** — does it touch the network, filesystem, credentials, sandboxed processes?
7. **Current state** — is there an existing README to improve? Existing docs to link to?

Sources to check (in order):
- Package manifest (Cargo.toml, package.json, pyproject.toml, go.mod)
- Existing README, CONTRIBUTING, CHANGELOG
- `docs/`, `specs/`, design documents
- Entry points (main.rs, index.ts, __main__.py)
- Dockerfile, docker-compose.yml
- CI config (.github/workflows/)
- Test files (reveal real usage patterns and edge cases)

### Phase 2: Load Mode References

Read the reference file(s) for every detected mode. These contain the mode-specific section patterns, structural conventions, and examples. Do not draft without reading them.

### Phase 3: Draft

Apply the section order below, adapting to the detected mode(s). Every section is evaluated — include it if it adds value, skip it if it doesn't apply.

**CHECKPOINT: After the first draft, present it to the user for review.** READMEs are high-visibility artifacts — the user should validate tone, emphasis, and what's included before polishing.

### Phase 4: Polish

After user feedback:
- Verify all code examples actually work (or are consistent with the codebase)
- Verify all links resolve
- Check that the README survives `cat README.md` in a terminal (no critical info in images only)
- Ensure badges reference real CI jobs / real package versions
- Remove any empty or placeholder sections

## Section Order

Derived from cognitive funneling: broadest/most-filtering information first, implementation detail last. Not every section applies to every project — skip sections that don't add value.

```
1.  Logo + Badges
2.  Title + One-Sentence Pitch
3.  Visual Demo (screenshot, GIF, terminal recording)
4.  Quick Start (30-second path to "it works")
5.  What Is This? / Background
6.  What This Is NOT (disambiguation)
7.  Features / Why Use This?
8.  Installation (by platform/method)
9.  Usage (real examples with expected output)
10. Configuration (minimum viable config, link to full reference)
11. Mode-Specific Sections (Tools list, Docker params, API reference — see mode refs)
12. Use Cases (concrete named scenarios)
13. Architecture / How It Works (brief, for contributors)
14. Integration with Other Tools
15. Security
16. Contributing
17. License
```

### Section Guidelines

**1. Logo + Badges**
- Dark/light logo via `<picture>` with `prefers-color-scheme` media queries if available
- 2-4 badges max: CI status, license, version/downloads. Badges on one line.
- No ASCII art logos. No "made with love" badges. No social media follow badges.

**2. Title + One-Sentence Pitch**
- The pitch names the category AND what it replaces or improves: "X is a Y that does Z"
- If there's a predecessor, name it: "a faster alternative to grep", "a cat clone with syntax highlighting"
- Keep under 120 characters

**3. Visual Demo**
- CLI tools: terminal recording (asciinema) or screenshot showing real output
- Web apps: screenshot of the primary interface
- Libraries/MCP servers: may skip if the value is in the API, not the UI
- Must show current state — stale visuals are worse than none

**4. Quick Start**
- The single fastest path to a working state. One code block. Copy-pasteable.
- Hierarchy of speed: `docker run` / `npx` (30s) > `brew install` (60s) > `curl | sh` (90s) > `cargo install` (3-5min)
- Fastest path first. No prose before the code block — at most a one-line setup instruction.

**5. What Is This? / Background**
- Only needed when the name and pitch aren't self-explanatory
- 2-3 paragraphs max covering: what problem it solves, what approach it takes, key design decisions
- Skip for projects where the title + pitch + demo already communicate this

**6. What This Is NOT**
- For projects in ambiguous categories where users will arrive with wrong mental models
- Name specific things people might confuse it with and explain the difference
- High-trust signal — shows the maintainer knows the tool's boundaries (ripgrep pattern)
- Skip for projects where the category is obvious

**7. Features / Why Use This?**
- Bullet list of concrete capabilities, not marketing adjectives
- Each feature should be verifiable: "supports X" not "blazingly fast"
- Benchmark table with real numbers if performance is a selling point (specify hardware, corpus, conditions)
- Feature comparison matrix vs. alternatives if the tool has direct competitors

**8. Installation**
- By platform, most popular distribution method first
- Use `<details>` blocks for per-platform depth to keep the section scannable
- For tools requiring post-install configuration (shell integration, config file creation), use numbered steps
- Always include the "from source" path last

**9. Usage**
- Real examples with expected output, not just flag documentation
- Start with the most common use case, not the most basic
- Show input AND output — the reader should know what to expect
- For CLIs: show 2-3 common invocations, then link to `--help` or man page for full reference

**10. Configuration**
- Show the minimum viable configuration inline (5-15 lines)
- Annotate every non-obvious field
- Link to full configuration reference if it exists elsewhere
- Never dump the entire config schema in the README

**11. Mode-Specific Sections**
- See the relevant mode reference file(s) for what goes here
- This is where Tools lists (MCP), Docker parameter tables, API references (libraries), etc. live

**12. Use Cases**
- Concrete named scenarios: "CTF challenge hosting", "CI credential injection", "local dev sandboxing"
- Each use case in 2-3 sentences: what the scenario is, how this tool helps, link to example if available
- Skip if the tool has only one obvious use case

**13. Architecture / How It Works**
- Brief (under 200 words) — this is for contributors, not users
- Link to ARCHITECTURE.md or design docs for depth
- Useful for tools with non-obvious internal structure (sandboxing, plugin systems, etc.)

**14. Integration with Other Tools**
- Table or list showing how it composes with ecosystem tools
- Skip if the tool is standalone with no integration surface

**15. Security**
- Mandatory for anything network-facing, credential-handling, or running untrusted code
- What the security model is, what it protects against, what it doesn't
- Link to SECURITY.md for vulnerability reporting

**16. Contributing**
- Short: how to report bugs, whether PRs are welcome, link to CONTRIBUTING.md
- If no CONTRIBUTING.md exists, include setup instructions for development

**17. License**
- SPDX identifier. One line. Last section.

## Anti-Patterns

| Anti-Pattern | What Happens | Prevention |
|--------------|-------------|------------|
| **Marketing-first** | Testimonials, contributor bubbles, tracking pixels before explaining what it does | Pitch in section 2, nothing promotional before it |
| **Badge wall** | 8+ badges signaling nothing useful | Max 4: CI, license, version, one domain-specific |
| **Config dump** | 200 lines of YAML with no annotation | Minimum viable config (5-15 lines), annotated, link to full reference |
| **Wall of text before demo** | Reader leaves before understanding the tool | Visual demo and quick start in sections 3-4, above the fold |
| **Empty sections** | "TODO", "Coming soon", placeholder text | Omit the section entirely — an empty section signals abandonment |
| **Stale visuals** | GIF showing UI from 6 months ago | Use text-based demos (asciinema) when possible; date screenshots |
| **Docs-site delegation without a docs site** | "See our docs at [404]" | README is the docs until the external site is mature and maintained |
| **README as API reference** | Entire API surface documented inline | API reference belongs in generated docs; README shows the 3 most common calls |
| **One install path** | Only `cargo install` when Docker/brew exist | List every distribution method, fastest first |
| **Assumed context** | Jargon or acronyms without introduction | Define terms on first use; link to background for domain concepts |

## Bias Guards

| Trap | Reality | Do Instead |
|------|---------|------------|
| **Feature completionism** | Listing every feature drowns the signal | Pick the 3-5 that matter most to the primary user persona |
| **Author's curse of knowledge** | You know the tool; the reader doesn't | Write for someone who landed from a search result, not a collaborator |
| **Optimism bias** | Describing what the tool will do, not what it does now | Document current state only — aspirational features go in a roadmap, not the README |
| **Template cargo cult** | Copying a template's sections without evaluating each one | Every section must justify its presence for THIS project |
| **Verbosity as thoroughness** | More words = better documentation | Shorter is better if nothing is lost. Cut ruthlessly after the first draft |

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Cognitive funneling is the organizing principle.** Every section answers a more specific question than the one before it. The reader who isn't interested filters out early; the reader who is interested goes deeper. This ordering is not arbitrary — it's the structure that minimizes wasted reading time.
- **The 30-second test is real.** If someone can't understand what the tool does and get it running within the first scroll, the README has failed its primary job. Quick Start is section 4, not section 8.
- **Show, don't tell.** A terminal recording of the tool in action communicates more than 500 words of description. A working code example beats a feature list. Expected output alongside the command beats "try it and see."
- **Self-contained until you earn link-out.** Don't delegate to a docs site that doesn't exist or isn't maintained. README is the docs until proven otherwise. The threshold: the external site has been live, indexed, and maintained for 3+ months.
- **Omit rather than placeholder.** A section that says "Coming soon" or "TODO" signals abandonment. If a section isn't ready, leave it out entirely. You can add it later.
- **The README must survive `cat`.** Critical information should not be locked in images. Every screenshot or GIF should have equivalent text nearby — a code block, a description, or a link to the text version.
- **Write for the search-result arrival.** The reader didn't start at your landing page. They found this repo from a Google result, a link in a Slack channel, or a dependency tree. They have zero context. The first 3 sections must stand alone.
