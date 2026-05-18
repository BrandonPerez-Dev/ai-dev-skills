/**
 * The skill graph definition — macro categories, sub-skills, and edges.
 * Embeddings are added by build-graph.ts.
 */

import type { SkillGraph } from "./graph.js";

export const SKILL_GRAPH_DEFINITION: Omit<SkillGraph, "version" | "model"> = {
  nodes: {
    // ── Macro Categories ──────────────────────────────────────────────
    "software-design": {
      id: "software-design",
      type: "macro",
      description:
        "Feature development, system design, architecture, implementation, and delivery. Use when building new features, designing systems, refactoring, or shipping code.",
      invoke: "design",
      keywords: ["build", "feature", "implement", "architect", "refactor", "create", "add", "develop"],
    },
    "quality": {
      id: "quality",
      type: "macro",
      description:
        "Debugging, code review, testing, and verification. Use when something is broken, needs review, or needs to be validated.",
      invoke: null,
      keywords: ["bug", "error", "broken", "fail", "review", "test", "verify", "wrong", "crash", "500"],
    },
    "product": {
      id: "product",
      type: "macro",
      description:
        "Product management — product definition, backlog management, and naming. Use when defining what to build or managing product scope.",
      invoke: "product-definition",
      keywords: ["product", "user story", "scope", "MVP", "backlog", "persona"],
    },
    "business": {
      id: "business",
      type: "macro",
      description:
        "Business strategy — opportunity evaluation, market analysis, customer research, financial modeling, and experiments. Use when evaluating ideas, sizing markets, or building business cases.",
      invoke: "opportunity-research",
      keywords: ["opportunity", "market", "TAM", "revenue", "business case", "customer", "experiment"],
    },
    "ai-engineering": {
      id: "ai-engineering",
      type: "macro",
      description:
        "AI agent development — building agents, prompt engineering, eval-driven testing, tool discovery, and MCP servers. Use when building AI systems, writing prompts, or creating agent tooling.",
      invoke: null,
      keywords: ["agent", "prompt", "eval", "MCP", "tool", "LLM", "AI", "Claude", "SDK"],
    },
    "infrastructure": {
      id: "infrastructure",
      type: "macro",
      description:
        "Infrastructure and DevOps — project scaffolding, CI/CD, cloud architecture, and workspace management. Use when setting up projects, deploying, or managing environments.",
      invoke: null,
      keywords: ["deploy", "CI", "CD", "scaffold", "infra", "cloud", "AWS", "Docker", "pipeline"],
    },
    "security": {
      id: "security",
      type: "macro",
      description:
        "Security auditing — application security (OWASP, SAST, dependency scanning, agent/MCP attack surfaces) and infrastructure security (host hardening, network assessment, firewall auditing, CIS benchmarks). Use when auditing code for vulnerabilities, hardening systems, or assessing security posture.",
      invoke: null,
      keywords: ["security", "audit", "vulnerability", "OWASP", "hardening", "pentest", "CVE", "scan"],
    },
    "meta": {
      id: "meta",
      type: "macro",
      description:
        "Claude Code workflow management — skill creation, maintenance, evaluation, orchestration, and research. Use when improving Claude Code itself, creating skills, or investigating how things work.",
      invoke: null,
      keywords: ["skill", "workflow", "Claude Code", "improve", "meta", "how does"],
    },
    "delivery": {
      id: "delivery",
      type: "macro",
      description:
        "Shipping and task management — commits, PRs, kanban boards, parallel execution, and workspace isolation. Use when ready to commit, create PRs, manage tasks, or parallelize work.",
      invoke: null,
      keywords: ["commit", "PR", "push", "merge", "kanban", "task", "board", "parallel"],
    },

    // ── Sub-Skills ────────────────────────────────────────────────────

    // Shared across multiple macros
    "research": {
      id: "research",
      type: "skill",
      description:
        "Answer questions about how code works, explore unfamiliar codebases, and compare approaches before making decisions. Use when asking 'how does this work', 'what does this do', 'what are my options', or 'I need to understand this before changing it'.",
      invoke: "research",
      keywords: ["how does", "what is", "explain", "understand", "explore", "unfamiliar", "compare", "options", "look into", "figure out"],
    },
    "prompt-engineering": {
      id: "prompt-engineering",
      type: "skill",
      description:
        "Craft effective instructions, tool descriptions, and structured context for AI models. Use when writing system prompts, skill descriptions, or optimizing prompts.",
      invoke: "prompt-engineering",
      keywords: ["prompt", "system prompt", "instructions", "context", "description"],
    },

    // Software Design sub-skills
    "design": {
      id: "design",
      type: "skill",
      description:
        "Plan and design a new feature, capability, or system before writing code. Use when someone says 'let's build', 'I want to add', 'create a new', or 'implement' something that doesn't exist yet. Produces an approved plan before coding starts.",
      invoke: "design",
      keywords: ["build a feature", "add new", "create new", "implement", "let's build", "I want to add", "new capability", "develop"],
    },
    "architecture": {
      id: "architecture",
      type: "skill",
      description:
        "Define how a system is structured — components, data flow, API contracts, and integration points. Use when deciding 'how should this be organized', 'what talks to what', or 'what's the right pattern for this'.",
      invoke: "architecture",
      keywords: ["system structure", "how should this be organized", "API contract", "data flow", "components", "pattern", "integration"],
    },
    "tdd": {
      id: "tdd",
      type: "skill",
      description:
        "Write code using test-driven development — the red-green-refactor cycle. " +
        "Use when someone says 'use TDD', 'write tests first then implement', " +
        "'red green refactor', 'test-driven', or 'build this with TDD'. " +
        "Writes a failing test, implements just enough to pass, then refactors. One vertical at a time.",
      invoke: "tdd",
      keywords: [
        "use TDD",
        "test-driven development",
        "write tests first",
        "red green refactor",
        "build with TDD",
        "test-first approach",
        "failing test then implement",
        "TDD cycle",
      ],
    },
    "test-planning": {
      id: "test-planning",
      type: "skill",
      description:
        "Plan what to test and how — vertical slices, integration test contracts, mock boundaries.",
      invoke: "test-planning",
      keywords: ["test plan", "test strategy", "what to test", "mock"],
    },
    "plan": {
      id: "plan",
      type: "skill",
      description:
        "Plan a feature before building it — write constraints, define vertical slices with done criteria and test contracts. " +
        "Use when someone says 'plan this feature', 'write a plan', 'break this into verticals', " +
        "'what are the constraints', 'write a spec', 'define the approach', or 'plan before coding'. " +
        "Produces a lightweight plan document, not a full design doc.",
      invoke: "plan",
      keywords: [
        "plan this feature",
        "write a plan",
        "break into verticals",
        "define constraints before coding",
        "write a spec",
        "what's the approach",
        "plan before building",
        "how should we build this",
        "define the work",
        "feature planning",
      ],
    },
    "build": {
      id: "build",
      type: "skill",
      description:
        "Execute a plan by writing code one vertical at a time. Use after plan produces ready verticals. Accepts complete plans, partial plans, or single verticals.",
      invoke: "build",
      keywords: ["execute plan", "start coding", "write the code", "implement", "build it"],
    },
    "ship": {
      id: "ship",
      type: "skill",
      description:
        "Finalize completed work for delivery — review what was built, run final checks, then decide to merge, create a PR, or keep iterating. Use when coding is done and you're ready to wrap up.",
      invoke: "ship",
      keywords: ["ship it", "we're done", "ready to merge", "finalize", "wrap up"],
    },
    "ui-ux-design": {
      id: "ui-ux-design",
      type: "skill",
      description:
        "Modern UI/UX design principles. Visual design decisions, interaction patterns, agentic UX.",
      invoke: "ui-ux-design",
      keywords: ["UI", "UX", "design", "visual", "interaction", "layout", "responsive"],
    },
    "frontend-build": {
      id: "frontend-build",
      type: "skill",
      description:
        "Implement UI designs with visual verification using browser MCP servers for screenshot-based iteration.",
      invoke: "frontend-build",
      keywords: ["frontend", "component", "React", "CSS", "HTML", "UI implementation"],
    },
    "frontend-design": {
      id: "frontend-design",
      type: "skill",
      description:
        "Create distinctive, production-grade frontend interfaces with high design quality.",
      invoke: "frontend-design",
      keywords: ["frontend", "interface", "web app", "page", "component"],
    },

    // Test pipeline sub-skills
    "test-writer": {
      id: "test-writer",
      type: "skill",
      description:
        "Write test code from approved test-planning contracts — integration tests first, one vertical at a time. " +
        "Use after test-planning produces contracts and before build begins. " +
        "Translates contracts into executable AAA-structured tests, confirms red, and commits as locked artifacts.",
      invoke: "test-writer",
      keywords: [
        "write the tests",
        "create test files",
        "implement test contracts",
        "write integration tests",
        "test code from plan",
        "red tests first",
        "locked test artifacts",
      ],
    },

    // Quality sub-skills
    "systematic-debugging": {
      id: "systematic-debugging",
      type: "skill",
      description:
        "Find and fix bugs by investigating the root cause first. Use when something is broken, returning errors, crashing, failing tests, throwing exceptions, or behaving unexpectedly. Never guess at fixes — investigate first.",
      invoke: "systematic-debugging",
      keywords: ["bug", "error", "broken", "not working", "crash", "failing", "exception", "500", "TypeError", "unexpected", "wrong output"],
    },
    "code-review": {
      id: "code-review",
      type: "skill",
      description:
        "Systematic code review — understand the change before judging it. Context first, strategic reading, severity-ranked findings.",
      invoke: "code-review",
      keywords: ["review", "PR", "code quality", "feedback"],
    },
    "receiving-code-review": {
      id: "receiving-code-review",
      type: "skill",
      description:
        "Handling code review feedback with technical rigor — verification before implementing.",
      invoke: "receiving-code-review",
      keywords: ["review feedback", "comments", "requested changes", "address review"],
    },
    "verification": {
      id: "verification",
      type: "skill",
      description:
        "Verify that work is actually complete — run tests, check edge cases, confirm nothing is broken. Use before claiming any task is done. Evidence over assertions.",
      invoke: "verification",
      keywords: ["is it done", "does it work", "run the tests", "check it", "make sure", "confirm working"],
    },

    // Product sub-skills
    "backlog-refinement": {
      id: "backlog-refinement",
      type: "skill",
      description:
        "Refine product backlog stories to make them sprint-ready. " +
        "Use when someone says 'refine the backlog', 'groom these stories', " +
        "'split this epic', 'write acceptance criteria', 'are these stories ready', " +
        "or 'clean up the backlog'. Covers story splitting, acceptance criteria, " +
        "and backlog health checks.",
      invoke: "backlog-refinement",
      keywords: [
        "refine the backlog",
        "groom stories",
        "write acceptance criteria",
        "split this epic",
        "is this story ready",
        "backlog health",
        "user stories",
        "story splitting",
        "sprint-ready",
        "backlog cleanup",
      ],
    },
    "sprint-planning": {
      id: "sprint-planning",
      type: "skill",
      description:
        "Plan a sprint — set a sprint goal, calculate team capacity, and select stories that fit. " +
        "Use when someone says 'plan the sprint', 'what fits in this sprint', " +
        "'start a new sprint', 'do capacity planning', or 'handle sprint carryovers'. " +
        "Selects and commits stories for a sprint iteration.",
      invoke: "sprint-planning",
      keywords: [
        "plan the sprint",
        "sprint goal",
        "what fits in this sprint",
        "capacity planning",
        "start a new sprint",
        "sprint carryover",
        "how much can the team take on",
        "scope the sprint",
      ],
    },
    "roadmap-planning": {
      id: "roadmap-planning",
      type: "skill",
      description:
        "Create and maintain product roadmaps — connect vision to execution with Now/Next/Later or outcome-based planning. " +
        "Use when someone says 'build a roadmap', 'what should we build next', " +
        "'run quarterly planning', 'update the roadmap', or 'prioritize initiatives'. " +
        "Plans which initiatives to pursue and when.",
      invoke: "roadmap-planning",
      keywords: [
        "build a roadmap",
        "what should we build next",
        "quarterly planning",
        "update the roadmap",
        "prioritize initiatives",
        "product roadmap",
        "Now Next Later",
        "strategic planning",
      ],
    },
    "retrospective": {
      id: "retrospective",
      type: "skill",
      description:
        "Run retrospectives and post-incident reviews that produce real action items. " +
        "Use when someone says 'run a retro', 'what went well', 'what should we improve', " +
        "'post-mortem', 'lessons learned', or 'start stop continue'. " +
        "Covers sprint retros, project retros, team health checks, and pre-mortems.",
      invoke: "retrospective",
      keywords: [
        "run a retro",
        "sprint retrospective",
        "what went well",
        "what should we improve",
        "post-mortem",
        "lessons learned",
        "start stop continue",
        "team health check",
        "after-action review",
        "blameless review",
      ],
    },
    "okr-setting": {
      id: "okr-setting",
      type: "skill",
      description:
        "Create and manage OKRs — translate strategy into measurable quarterly objectives and key results. " +
        "Use when someone says 'set OKRs', 'write objectives', 'score key results', " +
        "'run an OKR check-in', 'define success criteria for the quarter', or 'set team goals'. " +
        "Measures and tracks goals, not deciding what to build.",
      invoke: "okr-setting",
      keywords: [
        "set OKRs",
        "write objectives",
        "key results",
        "score OKRs",
        "OKR check-in",
        "quarterly goals",
        "team goals",
        "define success criteria",
        "track progress against objectives",
      ],
    },
    "product-definition": {
      id: "product-definition",
      type: "skill",
      description:
        "Define the product before engineering begins — write personas, map user journeys, prioritize a feature backlog, and scope an MVP. Use when a PM needs to define who the users are and what the product should do, not when an engineer is building something.",
      invoke: "product-definition",
      keywords: ["persona", "user journey", "MVP scope", "product manager", "who are the users", "define the product", "prioritize backlog"],
    },

    // Business sub-skills
    "metrics-review": {
      id: "metrics-review",
      type: "skill",
      description:
        "Run product metrics reviews — weekly business reviews, monthly performance, and diagnostic investigations. " +
        "Use when someone says 'review the metrics', 'why did this metric drop', " +
        "'run a weekly business review', 'analyze the funnel', 'churn spiked', " +
        "or 'what happened to signups'. Analyzes data and trends.",
      invoke: "metrics-review",
      keywords: [
        "review the metrics",
        "why did this metric drop",
        "weekly business review",
        "monthly performance review",
        "funnel analysis",
        "churn spiked",
        "retention declining",
        "signups are down",
        "KPI review",
        "product analytics",
      ],
    },
    "opportunity-research": {
      id: "opportunity-research",
      type: "skill",
      description:
        "Evaluate a new opportunity — customer problem, technical capability, or market signal. GO/YELLOW/RED recommendation.",
      invoke: "opportunity-research",
      keywords: ["opportunity", "evaluate", "idea", "worth pursuing"],
    },
    "opportunity-score": {
      id: "opportunity-score",
      type: "skill",
      description:
        "Score opportunities against Desirability/Viability/Feasibility/Adaptability framework.",
      invoke: "opportunity-score",
      keywords: ["score", "prioritize", "rank", "framework"],
    },
    "market-analysis": {
      id: "market-analysis",
      type: "skill",
      description:
        "TAM/SAM/SOM market sizing and competitive landscape analysis.",
      invoke: "market-analysis",
      keywords: ["market size", "TAM", "competition", "competitive"],
    },
    "business-case": {
      id: "business-case",
      type: "skill",
      description:
        "Evidence-based investment case — revenue model, unit economics, GTM strategy, financial projections.",
      invoke: "business-case",
      keywords: ["business case", "revenue", "unit economics", "investment"],
    },
    "startup-pitch": {
      id: "startup-pitch",
      type: "skill",
      description:
        "Create and refine startup pitch materials — elevator pitches, one-liners, " +
        "positioning statements, cold email pitches, one-pagers, and full pitch decks. " +
        "Builds from core narrative outward: nail the two-sentence pitch first, then " +
        "expand into every format. Supports multiple deck frameworks (Kawasaki, Sequoia, " +
        "YC, corporate innovation). Use when pitching a product to investors, preparing " +
        "for demo day, explaining a startup in one sentence, writing a cold outreach " +
        "email, creating an investor deck, building a one-pager, or pitching an internal " +
        "initiative to executives.",
      invoke: "startup-pitch",
      keywords: [
        "pitch my product",
        "elevator pitch",
        "pitch deck",
        "how do I explain my startup",
        "investor deck",
        "demo day pitch",
        "positioning statement",
        "cold email pitch",
        "one-pager",
        "present to investors",
        "internal innovation pitch",
        "one-liner for my company",
      ],
    },
    "customer-discovery": {
      id: "customer-discovery",
      type: "skill",
      description:
        "Synthesize customer research — interview transcripts, surveys, support tickets — using JTBD and empathy mapping.",
      invoke: "customer-discovery",
      keywords: ["customer", "interview", "survey", "JTBD", "empathy"],
    },
    "experiment-design": {
      id: "experiment-design",
      type: "skill",
      description:
        "Design experiments to test riskiest assumptions. Hypotheses and experiment cards with pre-committed success criteria.",
      invoke: "experiment-design",
      keywords: ["experiment", "hypothesis", "test assumption", "validate"],
    },
    "innovation-status": {
      id: "innovation-status",
      type: "skill",
      description:
        "Auto-generate portfolio status reports by scanning existing artifacts.",
      invoke: "innovation-status",
      keywords: ["status", "report", "portfolio", "update"],
    },

    // AI Engineering sub-skills
    "ai-agent-building": {
      id: "ai-agent-building",
      type: "skill",
      description:
        "Building AI agents with Claude — Agent SDK, tool design, orchestration patterns, and eval-driven testing.",
      invoke: "ai-agent-building",
      keywords: ["agent", "Agent SDK", "orchestration", "tool design"],
    },
    "eval-driven-dev": {
      id: "eval-driven-dev",
      type: "skill",
      description:
        "Eval-driven development for AI agents — eval suite design, grader selection, statistical confidence, transcript review.",
      invoke: "eval-driven-dev",
      keywords: ["eval", "evaluation", "grader", "non-deterministic", "agent testing"],
    },
    "tool-discovery": {
      id: "tool-discovery",
      type: "skill",
      description:
        "Scout for tools that expand capabilities — MCP servers, APIs worth wrapping, software worth adopting.",
      invoke: "tool-discovery",
      keywords: ["tool", "MCP server", "API", "integration", "discover"],
    },
    "mcp-builder": {
      id: "mcp-builder",
      type: "skill",
      description:
        "Build an MCP server to wrap an API, local app, or service so Claude Code can use it as a tool. Use when someone says 'create an MCP server', 'wrap this API', or 'make this service available to Claude'.",
      invoke: "mcp-builder",
      keywords: ["build MCP server", "create MCP", "wrap API as MCP", "new MCP server"],
    },

    // Software Design additions
    "cli-builder": {
      id: "cli-builder",
      type: "skill",
      description:
        "Create a CLI tool or command-line application from scratch. " +
        "Use when someone says 'create a CLI', 'make a CLI tool', 'I need a command-line tool', " +
        "'add CLI subcommands and flags', 'build a CLI app', or 'convert this to a CLI'. " +
        "Handles CLI-specific concerns: subcommand trees, flag and argument parsing with clap or commander, " +
        "help text generation, exit codes, JSON and table output modes, and agent-friendly structured output.",
      invoke: "cli-builder",
      keywords: [
        "create a CLI tool",
        "make a CLI app",
        "command-line tool",
        "CLI subcommands and flags",
        "argument parsing clap commander",
        "new CLI application",
        "CLI for agents",
        "command-line interface",
        "convert to CLI",
        "CLI exit codes",
        "I need a CLI",
      ],
    },

    // Delivery additions
    "git-ops": {
      id: "git-ops",
      type: "skill",
      description:
        "Git operations beyond commits and PRs — push, rebase, merge, conflict resolution, branch management, and recovery. " +
        "Use when someone says 'rebase this', 'merge branches', 'resolve conflicts', " +
        "'fix detached HEAD', 'recover from bad git state', 'push this branch', " +
        "or when git feels broken. Not for staging or commit messages.",
      invoke: "git-ops",
      keywords: [
        "rebase",
        "merge branches",
        "resolve conflicts",
        "fix detached HEAD",
        "push this branch",
        "git is broken",
        "recover git state",
        "force push",
        "branch management",
        "set up remote",
      ],
    },

    // Infrastructure sub-skills
    "boilerplate-cicd": {
      id: "boilerplate-cicd",
      type: "skill",
      description:
        "Project scaffolding and CI/CD — golden path templates for TypeScript/Node.js projects.",
      invoke: "boilerplate-cicd",
      keywords: ["scaffold", "template", "CI/CD", "GitHub Actions", "new project", "setup"],
    },
    "cloud-infrastructure": {
      id: "cloud-infrastructure",
      type: "skill",
      description:
        "Design cloud infrastructure architectures on AWS — deployment, hosting, service selection.",
      invoke: "cloud-infrastructure",
      keywords: ["AWS", "cloud", "deploy", "infrastructure", "hosting", "production"],
    },
    "git-worktrees": {
      id: "git-worktrees",
      type: "skill",
      description:
        "Creating isolated workspaces with git worktrees for parallel branches and subagent isolation.",
      invoke: "git-worktrees",
      keywords: ["worktree", "isolated", "parallel branch", "workspace"],
    },

    // Meta sub-skills
    "skill-creator": {
      id: "skill-creator",
      type: "skill",
      description:
        "Create or improve skills following agent-building best practices.",
      invoke: "skill-creator",
      keywords: ["create skill", "new skill", "improve skill", "skill quality"],
    },
    "skill-eval": {
      id: "skill-eval",
      type: "skill",
      description:
        "Test and validate skills — blind A/B comparison, baseline testing, grading against assessment criteria.",
      invoke: "skill-eval",
      keywords: ["test skill", "validate skill", "compare skills", "A/B"],
    },
    "skill-maintenance": {
      id: "skill-maintenance",
      type: "skill",
      description:
        "Evolve skills based on real-world usage — reads LEARNINGS.md logs and applies targeted updates.",
      invoke: "skill-maintenance",
      keywords: ["update skill", "fix skill", "skill learning", "evolve"],
    },
    "orchestrator": {
      id: "orchestrator",
      type: "skill",
      description:
        "Skill routing and workflow guidance. Detailed guidance on skill sequencing, tiers, and red flags.",
      invoke: "orchestrator",
      keywords: ["which skill", "routing", "workflow", "what skill should I use"],
    },
    "skill-graph": {
      id: "skill-graph",
      type: "skill",
      description:
        "Manage the skill router's embedding graph. Use when adding a new skill to the routing graph, when a skill isn't being routed to correctly, when diagnosing why the wrong skill triggers, or when tuning embedding descriptions for better semantic matching.",
      invoke: "skill-graph",
      keywords: ["add skill to graph", "skill not routing", "wrong skill triggers", "tune embeddings", "graph node", "routing accuracy", "skill-graph.ts"],
    },

    // Delivery sub-skills
    "commit-and-pr": {
      id: "commit-and-pr",
      type: "skill",
      description:
        "Create a git commit and open a pull request. Use only when the user literally asks for a commit or PR — 'git commit', 'commit this', 'open a PR', 'create a pull request', 'git push and open PR'.",
      invoke: "commit-and-pr",
      keywords: [
        "git commit",
        "commit this",
        "open a PR",
        "open a pull request",
        "create a pull request",
        "git push and open PR",
      ],
    },
    "parallel-agents": {
      id: "parallel-agents",
      type: "skill",
      description:
        "Dispatching multiple agents for independent problems — 2+ tasks without shared state.",
      invoke: "parallel-agents",
      keywords: ["parallel", "concurrent", "multiple agents", "independent tasks"],
    },
    "sp-kanban": {
      id: "sp-kanban",
      type: "skill",
      description:
        "Manage tasks on Super Productivity kanban board — create, organize, and track tasks.",
      invoke: "sp-kanban",
      keywords: ["kanban", "task board", "Super Productivity", "track tasks"],
    },
    "kanban-breakdown": {
      id: "kanban-breakdown",
      type: "skill",
      description:
        "Break down conversation or meeting notes into well-structured kanban cards.",
      invoke: "kanban-breakdown",
      keywords: ["meeting notes", "action items", "cards", "break down tasks"],
    },

    // Visualization & file format skills
    "presentation": {
      id: "presentation",
      type: "skill",
      description:
        "Create browser-rendered scrollable presentations for demos, meetings, and stakeholder updates. Use when someone says 'make a presentation', 'create slides', 'build a deck', or needs to present information visually.",
      invoke: "presentation",
      keywords: ["presentation", "slides", "deck", "demo", "stakeholder update", "meeting slides"],
    },
    "architecture-diagram": {
      id: "architecture-diagram",
      type: "skill",
      description:
        "Generate interactive architecture diagrams rendered in the browser. Use when someone says 'draw a diagram', 'visualize the architecture', 'show how components connect', or needs a visual system overview.",
      invoke: "architecture-diagram",
      keywords: ["diagram", "visualize", "architecture diagram", "system diagram", "show components", "draw"],
    },
    "refactor": {
      id: "refactor",
      type: "skill",
      description:
        "Refactor code. Use only when the user literally asks to refactor — 'refactor this', 'refactor this function', 'refactor src/foo.ts', 'let's refactor this code'.",
      invoke: "refactor",
      keywords: [
        "refactor this",
        "refactor this function",
        "refactor this file",
        "refactor this code",
        "refactor this module",
      ],
    },
    "pdf": {
      id: "pdf",
      type: "skill",
      description:
        "Read, parse, extract data from, or generate PDF files. Use when working with .pdf documents.",
      invoke: "pdf",
      keywords: ["PDF", "pdf file", "read PDF", "parse PDF"],
    },
    "pptx": {
      id: "pptx",
      type: "skill",
      description:
        "Create, read, or edit PowerPoint files (.pptx). Use when working with PowerPoint presentations.",
      invoke: "pptx",
      keywords: ["PowerPoint", "pptx", "slides file", ".pptx"],
    },
    "mermaid": {
      id: "mermaid",
      type: "skill",
      description:
        "Create diagrams using Mermaid syntax — flowcharts, sequence diagrams, ERDs, and more. Use when someone wants a quick diagram in markdown-compatible format.",
      invoke: "mermaid",
      keywords: ["mermaid", "flowchart", "sequence diagram", "ERD", "diagram code"],
    },

    // Security sub-skills
    "app-security": {
      id: "app-security",
      type: "skill",
      description:
        "Application and agent security auditing — OWASP Top 10, SAST, dependency vulnerabilities, MCP/agent-specific attack surfaces, and API security. Use when auditing code for security issues, hardening an API, or assessing agent/MCP server security.",
      invoke: "app-security",
      keywords: ["OWASP", "SAST", "vulnerability", "XSS", "injection", "security audit", "dependency scan", "CVE", "agent security"],
    },
    "infra-security": {
      id: "infra-security",
      type: "skill",
      description:
        "Network and system security — host hardening, network assessment, firewall auditing, CIS benchmarks, and service exposure analysis. Use when hardening a system, checking for exposed services, or auditing configurations against security baselines.",
      invoke: "infra-security",
      keywords: ["hardening", "firewall", "CIS", "nmap", "network scan", "exposed services", "system security", "lynis"],
    },

    // Data & ML sub-skills
    "data-modeling": {
      id: "data-modeling",
      type: "skill",
      description:
        "Design database schemas and data models. Use when deciding what tables, columns, relationships, or indexes to create. Covers relational, graph, document, and time-series paradigms. Handles questions like 'how should I structure this data', 'what's the right schema for this', or 'design a database for X'.",
      invoke: "data-modeling",
      keywords: ["design a database", "database schema", "table structure", "columns", "foreign key", "many-to-many", "one-to-many", "ERD", "normalize", "index", "migration", "what tables do I need", "data model", "relational", "graph model", "document store"],
    },
    "ml-experiment": {
      id: "ml-experiment",
      type: "skill",
      description:
        "Build and train machine learning models — classifiers, regressors, anomaly detectors, clustering. Use when someone says 'train a model', 'build a classifier', 'predict X from Y', or 'detect anomalies'. Covers problem framing, feature engineering, baseline selection, model evaluation, and the decision to ship or abandon.",
      invoke: "ml-experiment",
      keywords: ["train a model", "build a classifier", "predict", "detect anomalies", "machine learning", "ML", "classification", "regression", "clustering", "feature engineering", "accuracy", "precision", "recall", "scikit-learn", "model performance"],
    },

    // Naming (in product macro — naming is a product/brand decision)
    "naming": {
      id: "naming",
      type: "skill",
      description:
        "Choose a name for a project, product, tool, library, or brand. " +
        "Use when someone says 'what should we call this', 'name this project', " +
        "'I need a name for', 'rename this', or 'what's a good name'. " +
        "Covers naming briefs, volume generation, evaluation rubrics, " +
        "registry availability checking, and linguistic screening.",
      invoke: "naming",
      keywords: [
        "what should we call this",
        "name this project",
        "I need a name for",
        "rename",
        "what's a good name",
        "project name",
        "brand name",
        "product name",
        "CLI tool name",
        "package name",
        "naming",
      ],
    },

    // ── Cross-Cutting Reference Skills ──────────────────────────────
    // These are not matched by user prompts. They are loaded as active
    // guidance when a referencing skill is invoked.

    "coding-standards": {
      id: "coding-standards",
      type: "reference",
      description:
        "Universal coding quality bar — the rubric for all code written or reviewed. Covers correctness, security, readability, and efficiency. Referenced by skills that write or evaluate code, not invoked directly by users.",
      invoke: "coding-standards",
      keywords: [],
    },
    "rust-quality": {
      id: "rust-quality",
      type: "reference",
      description:
        "Rust code quality rules for AI build context. Prevents common AI-generated Rust mistakes — ownership band-aids, unwrap abuse, async deadlocks, non-idiomatic APIs. Referenced by build skills when implementing Rust verticals, not invoked directly by users.",
      invoke: "rust-quality",
      keywords: [],
    },
    "communication-protocol": {
      id: "communication-protocol",
      type: "reference",
      description:
        "How to present information, ask questions, and pace conversations with users. Covers chunking, progressive disclosure, decision scaling, and fatigue awareness. Referenced by skills that interact with users, not invoked directly.",
      invoke: "communication-protocol",
      keywords: [],
    },

    // File format skills (in delivery macro)
    "docx": {
      id: "docx",
      type: "skill",
      description: "Create, read, edit, or manipulate Word documents (.docx files).",
      invoke: "docx",
      keywords: ["Word", "docx", "document", "Word doc"],
    },
    "xlsx": {
      id: "xlsx",
      type: "skill",
      description: "Work with spreadsheet files — .xlsx, .xlsm, .csv, .tsv.",
      invoke: "xlsx",
      keywords: ["spreadsheet", "Excel", "xlsx", "csv"],
    },
  },

  edges: [
    // ── software-design contains ──
    { from: "software-design", to: "design", rel: "contains" },
    { from: "software-design", to: "architecture", rel: "contains" },
    { from: "software-design", to: "tdd", rel: "contains" },
    { from: "software-design", to: "test-planning", rel: "contains" },
    { from: "software-design", to: "plan", rel: "contains" },
    { from: "software-design", to: "build", rel: "contains" },
    { from: "software-design", to: "ship", rel: "contains" },
    { from: "software-design", to: "ui-ux-design", rel: "contains" },
    { from: "software-design", to: "frontend-build", rel: "contains" },
    { from: "software-design", to: "frontend-design", rel: "contains" },
    { from: "software-design", to: "research", rel: "contains" },
    { from: "software-design", to: "parallel-agents", rel: "contains" },

    // ── quality contains ──
    { from: "quality", to: "systematic-debugging", rel: "contains" },
    { from: "quality", to: "code-review", rel: "contains" },
    { from: "quality", to: "receiving-code-review", rel: "contains" },
    { from: "quality", to: "verification", rel: "contains" },
    { from: "quality", to: "research", rel: "contains" },

    // ── product contains ──
    { from: "product", to: "product-definition", rel: "contains" },
    { from: "product", to: "backlog-refinement", rel: "contains" },
    { from: "product", to: "sprint-planning", rel: "contains" },
    { from: "product", to: "roadmap-planning", rel: "contains" },
    { from: "product", to: "retrospective", rel: "contains" },
    { from: "product", to: "okr-setting", rel: "contains" },
    { from: "product", to: "research", rel: "contains" },

    // naming in product (naming is a product/brand decision)
    { from: "product", to: "naming", rel: "contains" },

    // ── business contains ──
    { from: "business", to: "metrics-review", rel: "contains" },
    { from: "business", to: "opportunity-research", rel: "contains" },
    { from: "business", to: "opportunity-score", rel: "contains" },
    { from: "business", to: "market-analysis", rel: "contains" },
    { from: "business", to: "business-case", rel: "contains" },
    { from: "business", to: "customer-discovery", rel: "contains" },
    { from: "business", to: "experiment-design", rel: "contains" },
    { from: "business", to: "innovation-status", rel: "contains" },
    { from: "business", to: "startup-pitch", rel: "contains" },
    { from: "business", to: "research", rel: "contains" },

    // ── ai-engineering contains ──
    { from: "ai-engineering", to: "ai-agent-building", rel: "contains" },
    { from: "ai-engineering", to: "eval-driven-dev", rel: "contains" },
    { from: "ai-engineering", to: "prompt-engineering", rel: "contains" },
    { from: "ai-engineering", to: "tool-discovery", rel: "contains" },
    { from: "ai-engineering", to: "mcp-builder", rel: "contains" },
    { from: "ai-engineering", to: "research", rel: "contains" },

    // ── infrastructure contains ──
    { from: "infrastructure", to: "boilerplate-cicd", rel: "contains" },
    { from: "infrastructure", to: "cloud-infrastructure", rel: "contains" },
    { from: "infrastructure", to: "git-worktrees", rel: "contains" },
    { from: "infrastructure", to: "research", rel: "contains" },

    // cli-builder, test-writer in software-design
    { from: "software-design", to: "cli-builder", rel: "contains" },
    { from: "software-design", to: "test-writer", rel: "contains" },

    // data-modeling in software-design, ml-experiment in ai-engineering
    { from: "software-design", to: "data-modeling", rel: "contains" },
    { from: "ai-engineering", to: "ml-experiment", rel: "contains" },

    // ── security contains ──
    { from: "security", to: "app-security", rel: "contains" },
    { from: "security", to: "infra-security", rel: "contains" },
    { from: "security", to: "research", rel: "contains" },

    // ── meta contains ──
    { from: "meta", to: "skill-creator", rel: "contains" },
    { from: "meta", to: "skill-eval", rel: "contains" },
    { from: "meta", to: "skill-maintenance", rel: "contains" },
    { from: "meta", to: "orchestrator", rel: "contains" },
    { from: "meta", to: "research", rel: "contains" },
    { from: "meta", to: "prompt-engineering", rel: "contains" },
    { from: "meta", to: "skill-graph", rel: "contains" },

    // ── delivery contains ──
    { from: "delivery", to: "git-ops", rel: "contains" },
    { from: "delivery", to: "commit-and-pr", rel: "contains" },
    { from: "delivery", to: "parallel-agents", rel: "contains" },
    { from: "delivery", to: "sp-kanban", rel: "contains" },
    { from: "delivery", to: "kanban-breakdown", rel: "contains" },
    { from: "delivery", to: "docx", rel: "contains" },
    { from: "delivery", to: "xlsx", rel: "contains" },
    { from: "delivery", to: "pdf", rel: "contains" },
    { from: "delivery", to: "pptx", rel: "contains" },
    { from: "delivery", to: "mermaid", rel: "contains" },
    { from: "delivery", to: "presentation", rel: "contains" },
    { from: "delivery", to: "architecture-diagram", rel: "contains" },

    // simplify belongs in software-design (post-build polish)
    { from: "software-design", to: "refactor", rel: "contains" },

    // ── Ordering: precedes ──
    { from: "design", to: "build", rel: "precedes" },
    // build invokes simplify after each vertical commit, then simplify precedes ship for final pass
    { from: "build", to: "refactor", rel: "precedes" },
    { from: "refactor", to: "ship", rel: "precedes" },
    { from: "ship", to: "commit-and-pr", rel: "precedes" },
    { from: "plan", to: "build", rel: "precedes" },
    { from: "test-planning", to: "test-writer", rel: "precedes" },
    { from: "test-writer", to: "build", rel: "precedes" },
    { from: "test-planning", to: "tdd", rel: "precedes" },
    { from: "roadmap-planning", to: "backlog-refinement", rel: "precedes" },
    { from: "backlog-refinement", to: "sprint-planning", rel: "precedes" },
    { from: "opportunity-research", to: "opportunity-score", rel: "precedes" },
    { from: "opportunity-research", to: "market-analysis", rel: "precedes" },
    { from: "market-analysis", to: "business-case", rel: "precedes" },
    { from: "product-definition", to: "startup-pitch", rel: "precedes" },
    { from: "business-case", to: "startup-pitch", rel: "precedes" },
    { from: "startup-pitch", to: "communication-protocol", rel: "references" },
    { from: "research", to: "skill-creator", rel: "precedes" },
    { from: "research", to: "design", rel: "precedes" },

    // ── Requirements: requires ──
    { from: "systematic-debugging", to: "verification", rel: "requires" },
    { from: "build", to: "verification", rel: "requires" },
    { from: "code-review", to: "verification", rel: "requires" },

    // ── Cross-cutting: references ──
    // coding-standards: any skill that writes or evaluates code
    { from: "build", to: "coding-standards", rel: "references" },
    { from: "tdd", to: "coding-standards", rel: "references" },
    { from: "code-review", to: "coding-standards", rel: "references" },
    { from: "systematic-debugging", to: "coding-standards", rel: "references" },
    { from: "frontend-build", to: "coding-standards", rel: "references" },
    { from: "frontend-design", to: "coding-standards", rel: "references" },
    { from: "mcp-builder", to: "coding-standards", rel: "references" },
    { from: "receiving-code-review", to: "coding-standards", rel: "references" },
    { from: "refactor", to: "coding-standards", rel: "references" },
    { from: "cli-builder", to: "coding-standards", rel: "references" },
    { from: "test-writer", to: "coding-standards", rel: "references" },
    { from: "build", to: "rust-quality", rel: "references" },

    // parallel-agents & ai-agent-building: build uses subagents for parallel execution
    { from: "build", to: "parallel-agents", rel: "references" },
    { from: "build", to: "ai-agent-building", rel: "references" },

    // communication-protocol: any skill that interacts with the user
    { from: "design", to: "communication-protocol", rel: "references" },
    { from: "research", to: "communication-protocol", rel: "references" },
    { from: "systematic-debugging", to: "communication-protocol", rel: "references" },
    { from: "architecture", to: "communication-protocol", rel: "references" },
    { from: "product-definition", to: "communication-protocol", rel: "references" },
    { from: "plan", to: "communication-protocol", rel: "references" },
    { from: "opportunity-research", to: "communication-protocol", rel: "references" },
    { from: "customer-discovery", to: "communication-protocol", rel: "references" },
  ],
};
