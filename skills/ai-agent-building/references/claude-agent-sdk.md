# Claude Agent SDK Reference

Verified against official documentation (June 2026 refresh). Sources: platform.claude.com, GitHub repos, [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents).

## Installation

```bash
# TypeScript
npm install @anthropic-ai/claude-agent-sdk

# Python
pip install claude-agent-sdk
```

## Basic Usage

`query()` returns an **async iterator** of messages — NOT a Promise. Use `for await`.

**TypeScript:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Fix the failing test in src/utils.test.ts",
  options: {
    systemPrompt: "You are a code repair agent.",
    allowedTools: ["Read", "Edit", "Bash", "Glob", "Grep"],
    maxTurns: 10,
  },
})) {
  if (message.type === "assistant") {
    for (const block of message.content) {
      if (block.type === "text") console.log(block.text);
    }
  }
  if (message.type === "result") {
    console.log("Done:", message.result);
  }
}
```

**Python:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Fix the failing test in src/utils.test.ts",
    options=ClaudeAgentOptions(
        system_prompt="You are a code repair agent.",
        allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],
        max_turns=10,
    ),
):
    if hasattr(message, "result"):
        print("Done:", message.result)
```

## Options

```typescript
interface Options {
  allowedTools?: string[];             // Tool whitelist (GRANT, not fence — see permissions note below)
  disallowedTools?: string[];          // Tool blacklist
  permissionMode?: "default" | "acceptEdits" | "bypassPermissions";
  systemPrompt?: string;               // System prompt for the agent
  maxTurns?: number;                   // Max conversation turns
  resume?: string;                     // Session ID to resume
  mcpServers?: Record<string, MCPServerConfig>;  // MCP server configs
  agents?: Record<string, AgentDefinition>;      // Subagent definitions
  hooks?: Record<HookEventName, HookMatcher[]>;  // Lifecycle hooks
  env?: Record<string, string>;        // Environment variables
  skills?: "all" | string[];           // Skill loading (replaces deprecated allowedTools: ["Skill"])
  effort?: "low" | "medium" | "high" | "xhigh" | "max";  // Adaptive thinking budget — see below
}
```

**`allowedTools` is a GRANT, not a FENCE** ([GH #37683](https://github.com/anthropics/claude-code/issues/37683), confirmed in [Claude Code skills docs](https://code.claude.com/docs/en/skills)). Listing tools pre-approves them while the agent runs — but does NOT block Claude from using unlisted tools. To actually block tools, use `disallowedTools` or permission deny rules.

**`skills` (replaces `allowedTools: ["Skill"]`)** — the old pattern of including `"Skill"` in `allowedTools` is deprecated. Use `skills: "all"` to load all skills, or `skills: ["skill-a", "skill-b"]` to load specific ones. The Skill tool is still callable; the discovery mechanism is what changed.

## Adaptive Thinking (Claude 4.x)

The 4.x architecture is **adaptive thinking** — Claude decides when and how much to think based on the configured `effort` and query complexity. This replaces manual `budget_tokens` and most "think step by step" scaffolding.

**`budget_tokens` is deprecated** on Opus 4.6 / Sonnet 4.6, and **returns 400 on Opus 4.7+**. Migrate to `effort`:

| Effort | When to use |
|---|---|
| `max` | Intelligence-demanding tasks; risk of overthinking simple work |
| `xhigh` (4.7+) | Best default for most coding and agentic tasks; the Opus 4.7 default |
| `high` | Minimum for intelligence-sensitive work; the Sonnet 4.6 default |
| `medium` | Cost-sensitive workloads |
| `low` | Latency-sensitive, scoped, non-intelligence-sensitive |

**Stop telling Claude 4.x to "think step by step."** Per current Anthropic docs, those instructions were scaffolding for older-model limitations and are no longer load-bearing — delete them and raise the effort level instead.

**Prefilled responses are deprecated on Claude 4.6+** (return 400). If you previously used prefill to force JSON, switch to Structured Outputs or a direct instruction ("Respond in valid JSON.").

## MCP Server Configuration

MCP is the production standard for agentic tool integration in 2026 (10,000+ public servers, donated to the Agentic AI Foundation under the Linux Foundation December 2025). For new tools and integrations, **author them as MCP servers by default** — the ecosystem effect plus governance neutrality means bespoke per-integration wiring pays a long-term integration tax.

`mcpServers` is a **Record** (object with server names as keys), not an array.

**stdio (local process):**
```typescript
mcpServers: {
  github: {
    command: "npx",
    args: ["-y", "@modelcontextprotocol/server-github"],
    env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN }
  }
}
```

**HTTP/SSE (remote):**
```typescript
mcpServers: {
  docs: {
    type: "http",
    url: "https://api.example.com/mcp",
    headers: { Authorization: `Bearer ${token}` }
  }
}
```

Tool naming convention: `mcp__<server-name>__<tool-name>`. Use `allowedTools: ["mcp__github__*"]` to allow all tools from a server.

## Subagents

`agents` is a **Record** with agent names as keys. `Task` must be in `allowedTools` to invoke subagents. Subagents cannot spawn their own subagents.

```typescript
for await (const message of query({
  prompt: "Review the codebase and run tests",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "Task"],
    agents: {
      "code-reviewer": {
        description: "Review code for correctness and security. Use for code quality analysis.",
        prompt: "You are a code review specialist. Focus on correctness, security, and maintainability.",
        tools: ["Read", "Glob", "Grep"],
        model: "opus"
      },
      "test-runner": {
        description: "Run test suites and analyze failures. Use for test execution.",
        prompt: "You run tests and analyze failures. Report pass/fail counts and root causes.",
        tools: ["Bash", "Read", "Grep"]
      }
    }
  }
})) { /* ... */ }
```

## Hooks

Hooks intercept lifecycle events for validation, logging, or transformation.

**Hook events** (both TypeScript and Python): `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PermissionRequest`, `Notification`

**TypeScript-only**: `SessionStart`, `SessionEnd`, `Setup`, `TeammateIdle`, `TaskCompleted`, `ConfigChange`, `WorktreeCreate`, `WorktreeRemove`

**Configuration:**
```typescript
for await (const message of query({
  prompt: "Refactor the auth module",
  options: {
    hooks: {
      PreToolUse: [
        {
          matcher: "Write|Edit",           // Regex — match tool names
          hooks: [protectSensitiveFiles],   // Array of callbacks
          timeout: 60                       // Seconds (default 60)
        }
      ],
      PostToolUse: [
        { hooks: [auditLogger] }           // No matcher = matches all
      ]
    }
  }
})) { /* ... */ }
```

**Hook callback signature:**
```typescript
type HookCallback = (
  input: HookInput,
  toolUseID: string | undefined,
  context: { signal: AbortSignal }
) => Promise<HookOutput>;

interface HookOutput {
  systemMessage?: string;         // Inject into conversation
  continue_?: boolean;            // Continue execution?
  hookSpecificOutput?: {
    hookEventName: string;
    permissionDecision?: "allow" | "deny" | "ask";  // PreToolUse
    permissionDecisionReason?: string;
    updatedInput?: object;        // Modify tool input
    additionalContext?: string;   // PostToolUse
  };
}
```

**Example — block destructive commands:**
```typescript
async function protectSensitiveFiles(input, toolUseID, context) {
  const filePath = input.input?.file_path || input.input?.command || "";
  if (filePath.includes(".env") || filePath.includes("credentials")) {
    return {
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Cannot modify sensitive files"
      }
    };
  }
  return {
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow"
    }
  };
}
```

## Session Resume

Each `query()` starts a new session. Capture `session_id` from messages to resume later.

```typescript
let sessionId: string | undefined;

// First session
for await (const message of query({ prompt: "Read the auth module" })) {
  if ("session_id" in message) sessionId = message.session_id;
}

// Resume with full context preserved
if (sessionId) {
  for await (const message of query({
    prompt: "Now refactor what you found",
    options: { resume: sessionId }
  })) { /* ... */ }
}
```

## Built-in Tools

| Tool | Purpose |
|------|---------|
| Read | Read files (supports images, PDFs, notebooks) |
| Write | Create new files |
| Edit | Modify existing files (exact string replacement) |
| Glob | Find files by pattern |
| Grep | Search file contents (regex, ripgrep-based) |
| Bash | Run shell commands (with timeout and sandboxing) |
| WebSearch | Search the web |
| WebFetch | Fetch URL content (HTML → markdown) |
| Task | Launch subagents for parallel work |

**Principle of least privilege.** Start with minimal tools, add as needed. An agent with `Bash` can do almost anything — restrict unless required.

**Response truncation.** Claude Code truncates tool responses at **25,000 tokens** by default. For tools that can return more, implement pagination, filtering, and `response_format` enums rather than relying on truncation — the agent can't tell truncated success from full success without an explicit signal.

## Prompt Caching for Agentic Workloads

Anthropic prompt caching (launched August 14, 2024) is the cheapest single optimization for any agentic workload with stable prompt prefixes (system prompts, tool descriptions, persona, few-shot examples).

- **Explicit opt-in** via `cache_control` annotations
- **Minimum prefix length**: 1024 tokens (Sonnet 4.6, Opus 4.x), 2048 tokens (Haiku 4.5)
- **Cache hit**: 10% of base input cost (90% savings on cached portion)
- **Cache write**: 25% premium
- **Default TTL**: 5 minutes, extendable to 1 hour

For agentic loops where the system prompt + tool descriptions are reused across many tool-call turns within a session, caching the static prefix is essentially free latency and substantial cost reduction. Build for it from day one on any production agent.
