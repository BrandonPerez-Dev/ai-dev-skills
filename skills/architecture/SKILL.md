
---
name: architecture
description: Technical design — components, data flow, API contracts, integration points, orchestration patterns. Use when defining how a system is built, choosing patterns, designing interfaces between components, or making technology decisions. Reads context/ for existing architectural truth. Contracts first, implementation second.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Task
---

# Architecture

Define the technical structure. Components, data flow, API contracts, integration points, technology decisions. **Contracts first, implementation second.**

## When to Use

- Designing a new feature or system
- Defining API contracts between client and server
- Choosing data models and storage strategies
- Planning integration with external services or AI agents
- Making technology or pattern decisions
- Choosing orchestration patterns for multi-agent systems

## Core Principle: Start with the Right Complexity

Before introducing architecture, evaluate what level you actually need:

| Level | When | Example |
|-------|------|---------|
| **Direct call** | Single-step task, no coordination | Call an API, transform data |
| **Single service with tools** | One domain, some dynamic routing | Agent with multiple tools |
| **Multi-component orchestration** | Cross-domain, security boundaries, specialization | Multiple agents, BFF, adapters |

Use the lowest level that reliably meets requirements. Every abstraction layer adds coordination overhead, latency, and failure modes. Justify each one.

## Process

### 1. Understand Constraints

- **What's decided** — read `context/` if it exists. These are the current architectural commitments (technology choices, integration patterns, infrastructure decisions). Do not re-decide what's already captured there without explicit user direction — re-opening settled decisions wastes design time and risks contradicting downstream work that already depends on them.
- **What exists** — current architecture, patterns, conventions
- **What's changing** — requirements from design phase
- **What's fixed** — tech stack, deployment, team conventions

### 2. Define Contracts First

TypeScript interfaces and API contracts before implementation. Contracts are the single source of truth.

**Where contracts live:**
- Architecture produces contracts **inline in the design conversation** — TypeScript interfaces, Zod schemas, endpoint signatures, event types. These are draft artifacts for the current discussion, not files written to disk.
- **Test-planning promotes** these contracts into `spec/<name>.md`, where they live permanently. That's the handoff point: architecture drafts, test-planning lands them.
- On greenfield, test-planning creates the initial `spec/` files using the architecture draft as seed content.
- On subsequent features, architecture drafts deltas against existing `spec/<name>.md` contracts; test-planning applies those deltas.
- **Never duplicate contracts** outside `spec/` — the spec file is the single home; everywhere else points at it.

**REST endpoints:**
```typescript
POST /api/agents/:agentId/tasks
Request: { type: 'workflow_run' }
Response: { data: { taskId: string, status: 'queued' } }
```

**SSE event streams:**
```typescript
// Event types with typed payloads
type SSEEvent =
  | { event: 'task.started', data: { taskId: string } }
  | { event: 'task.progress', data: { step: string, progress: number } }
  | { event: 'task.completed', data: { taskId: string, result: TaskResult } }
```

**Shared schemas (Zod):**
```typescript
// Single source of truth — used by both frontend and backend
const TaskSchema = z.object({
  id: z.string(),
  status: z.enum(['queued', 'running', 'completed', 'failed']),
  result: TaskResultSchema.optional(),
})
```

Shared Zod schemas in a common package ensure frontend and backend stay in sync. Changes propagate through TypeScript's type system.

### 3. Define Components

| Component | Type | Responsibility | New/Modified |
|-----------|------|----------------|--------------|
| WorkflowService | Service | Orchestrates runs | Modified |
| PodAdapter | Adapter | Translates agent API | New |

### 4. Trace Data Flow

For each vertical slice, trace how data moves through the system:

```
User action → Route → Service → Adapter → External system
                                                ↓
                                      SSE events → Client
```

For each flow, define:
- Request/response shapes (reference the contracts from step 2)
- Error cases and how they propagate
- Real-time updates (what events, when)

### 5. Identify Integration Points

Where does this connect to other systems?
- **External APIs** — endpoints, auth, rate limits, error responses
- **Databases** — schema changes, migrations, indexes
- **Event systems** — SSE events published/consumed, reconnection behavior
- **Shared types** — cross-package contracts (Zod schemas, TypeScript types)

### 6. Record Decisions

Every non-obvious architectural choice needs a decision record. **System-level decisions** (technology choices, integration patterns, infrastructure commitments that apply beyond this feature) should be written to `context/<topic>.md` — mutable, always-current, no timestamps. Feature-specific decisions stay in the per-change folder. Format decisions as a table:

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Adapter pattern for agent integration | Direct API calls | Decouples agent from platform; agents can be swapped |
| SSE for real-time events | WebSocket | Unidirectional sufficient; simpler reconnection; HTTP/2 multiplexing |

**Where decisions land:**
- **System-level decisions** → `context/<topic>.md` (mutable architectural truth, always loaded by future agents), ADR-style: the decision, its rationale, and the rejected alternatives with the why-not. Create or update the relevant topic file.
- **Slice-specific decisions** → the affected spec's `## Notes`.
- **If the project maintains `docs/adr/`** → follow that convention instead.

Capture the **why**, not just the **what**. Future developers need to understand context, not just the outcome.

## Agent Orchestration Patterns

When designing AI agent systems, choose the orchestration pattern that fits:

| Pattern | How It Works | Best For | Watch For |
|---------|-------------|----------|-----------|
| **Sequential** | Pipeline — each agent processes previous output | Step-by-step refinement with clear dependencies | Early failures propagate; no parallelism |
| **Concurrent** | Fan-out/fan-in — agents work in parallel | Independent analysis from multiple perspectives | Needs conflict resolution for contradictions |
| **Handoff** | Dynamic delegation — one active agent at a time | Right specialist emerges during processing | Infinite handoff loops |
| **Orchestrator-Worker** | Central coordinator delegates to specialists | Cross-domain tasks with clear subtask decomposition | Single point of failure in orchestrator |
| **Group Chat** | Agents contribute to shared conversation thread | Consensus-building, maker-checker validation | Conversation loops; hard to control with many agents |

**Default to single agent with tools.** Only introduce multi-agent orchestration when you can demonstrate a single agent can't reliably handle the task due to prompt complexity, tool overload, or security requirements.

## Patterns to Prefer

- **Adapter pattern** for external integrations — isolate external API specifics behind a consistent interface. Agents, payment providers, and third-party services all get adapters.
- **Service layer** for business logic — thin routes that validate and delegate. Logic lives in services, not handlers.
- **Shared Zod schemas** for cross-boundary contracts — single source of truth for data shapes, validated at system boundaries.
- **SSE for real-time** — not WebSocket unless bidirectional is required. SSE has automatic reconnection, uses standard HTTP, and multiplexes over HTTP/2.
- **BFF (Backend-for-Frontend)** when the frontend needs a different data shape than the backend provides — translate, aggregate, and protect.

## SSE Design Considerations

SSE is the primary real-time pattern for AI agent UIs. Key decisions:

- **Event types** — use named events (`event: task.progress`) with typed JSON payloads
- **Reconnection** — browsers auto-reconnect. Set `retry:` field for custom intervals. Send `id:` on events so clients can resume via `Last-Event-ID` header.
- **Heartbeat** — send a comment (`: heartbeat`) every ~15s to keep connections alive and detect drops
- **Error propagation** — send error events in-stream rather than closing the connection for recoverable errors
- **HTTP/2** — eliminates the 6-connection-per-domain limit of HTTP/1.1

## Output

Architecture produces a design artifact that feeds three destinations:

1. **Immediate:** structured markdown rendered in the design conversation (the format below). This is conversational output, not a file written to disk. Downstream skills (slicing, test-planning) read it from conversation context.
2. **Promoted by test-planning:** the Contracts section lands in `spec/<name>.md` (permanent living spec).
3. **Promoted by slicing or architecture:** system-level Decisions land in `context/<topic>.md` (with rejected alternatives); slice-specific decisions land in the affected spec's `## Notes`.

```markdown
## Architecture Overview
[1-2 sentence summary of the approach]

## Contracts
[TypeScript interfaces and Zod schemas — the source of truth]
[Note which spec/<name>.md file(s) these will land in]

## Components
[Table of components with types and responsibilities]

## Data Flow
[Step-by-step trace per vertical slice]

## Integration Points
[External systems, databases, events, shared types]

## Decisions
| Decision | Alternatives | Rationale |
|----------|-------------|-----------|

## Schema Changes
[Migrations if any]
```

## Guidelines

- **Contract first.** Define interfaces and schemas before implementing anything. Frontend and backend can build in parallel against the contract.
- **Contracts are durable artifacts.** Everything declared in the Contracts section becomes part of `spec/<name>.md` — the living system specification. Assume the contract will be read by agents doing future features, not just the current one.
- **Match existing patterns.** Don't introduce new patterns without justification. Consistency reduces cognitive load.
- **Minimum viable architecture.** Simplest thing that works. Every abstraction must justify its existence. YAGNI ruthlessly — don't design for hypothetical future requirements.
- **Flag unknowns.** Ask rather than guess. Uncertainty is cheaper to resolve through conversation than through code.
- **Design for failure.** Every API call can fail. Every connection can drop. Every external service can be slow. Define error paths explicitly, not as afterthoughts.
