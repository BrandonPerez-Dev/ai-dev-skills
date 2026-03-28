---
name: cloud-infrastructure
description: >-
  Design cloud infrastructure architectures on AWS through structured conversation.
  Use when the user asks to plan deployment, design cloud architecture, figure out
  how to host a system, choose between AWS services, plan infrastructure for a new
  project, or prepare for production deployment. Also use when asked about compute
  choices (Lambda vs Fargate vs EC2), networking, cost optimization, or scaling.
  Guides decisions iteratively with checkpoints — does not dump a complete architecture.
  Produces a structured infrastructure spec that feeds into the architecture-diagram skill.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - Skill
  - WebSearch
  - WebFetch
---

# Cloud Infrastructure

Start with the simplest thing that works. Add complexity only when you can name the problem it solves.

<HARD-GATE>
This is a CONVERSATION, not a deliverable. Do NOT produce a complete infrastructure
architecture in one shot. Work through decisions one at a time with the user. Present
one component or trade-off, get their input, incorporate it, then move to the next.
The user is a collaborator with institutional knowledge you don't have — platform team
preferences, security requirements, budget constraints, team dynamics. Extract that
knowledge through dialogue, don't guess past it.
</HARD-GATE>

<HARD-GATE>
Do NOT propose infrastructure without first understanding organizational constraints.
Every company has a platform team, approved services, security requirements, and
preferred patterns. Designing in a vacuum produces architectures that get rejected
in review. Ask first, design second.
</HARD-GATE>

## When to Use

| Situation | Approach |
|-----------|----------|
| Greenfield project needs hosting | Full design flow — all 5 phases |
| Adding infrastructure to existing system | Start at Phase 2 (workload), skip constraints already known |
| Evaluating a specific choice (e.g., "Lambda or Fargate?") | Jump to decision framework in references, present trade-offs |
| Preparing for a platform team review | Phase 1 (constraints) + Phase 5 (spec output) |
| Cost optimization | Phase 4 focused on cost model |

## Decision Sequencing

Infrastructure decisions have dependencies. Wrong order = expensive rework.

```
Phase 1: Organizational Constraints  (what's mandated?)
    ↓
Phase 2: Workload Classification     (what kind of thing is this?)
    ↓
Phase 3: Component Mapping           (which AWS services for each component?)
    ↓
Phase 4: Cost & Scaling Model        (what does it cost, how does it grow?)
    ↓
Phase 5: Infrastructure Spec         (concrete output for diagram + IaC)
```

**Why this order matters:**
- Choosing Fargate before knowing the platform team mandates EKS = wasted work
- Choosing stateless compute before understanding session requirements = redesign
- Sizing instances before knowing the cost model = sticker shock in review

## Process

### Phase 1: Discover Organizational Constraints

Before any technical decisions, understand the landscape. Ask the user:

1. **Platform team standards** — What's approved? What's mandated? What's forbidden?
2. **Auth & identity** — Cognito? Okta? Internal SSO? What does the org use?
3. **Secrets management** — Secrets Manager? Parameter Store? Vault? What's standard?
4. **Hosting patterns** — ECS? EKS? Lambda? What does the platform team support?
5. **Logging & observability** — CloudWatch? Datadog? Splunk? New Relic?
6. **Networking** — Existing VPCs? Transit gateways? VPN requirements?
7. **CI/CD** — GitHub Actions? CodePipeline? Jenkins? ArgoCD?
8. **Security** — Compliance requirements? Data residency? Encryption standards?

**Discovery tools:**
- Ask the user directly (fastest, most reliable)
- `aws organizations describe-organization` — account structure
- `aws ecs list-clusters` / `aws eks list-clusters` — what's already running
- `aws secretsmanager list-secrets` — what secret store is in use
- Future: Confluence MCP for internal docs, AWS MCP for live inventory

Record findings in `references/platform-standards.md`. This accumulates over time — each conversation fills in more.

**CHECKPOINT:** Present what you've learned about constraints before proceeding.

"Here's what I understand about your platform constraints:
- Compute: [known/unknown]
- Auth: [known/unknown]
- Secrets: [known/unknown]
- Logging: [known/unknown]

What am I missing? What would the platform team push back on?"

### Phase 2: Classify the Workload

Not all workloads are the same. Classification drives every downstream decision.

| Dimension | Options | Implications |
|-----------|---------|-------------|
| **Duration** | Short (<15min) / Long (hours) / Persistent | Lambda ceiling, connection timeouts |
| **Statefulness** | Stateless / Session-sticky / Fully stateful | Load balancing, failover strategy |
| **Connection type** | Request-response / SSE streaming / WebSocket | ALB config, timeout settings |
| **Sidecar needs** | None / Co-located processes / Shared filesystem | Container orchestration choice |
| **Multi-tenancy** | Single-tenant / Shared infra / Isolated per customer | VPC design, credential isolation |

For AI agent workloads specifically, read `references/aws-agent-workloads.md` — it covers the constraints that differ from standard web applications.

**CHECKPOINT:** Present workload classification and get confirmation.

"Based on what you've described, this workload is:
- [Duration]: because [reason]
- [Statefulness]: because [reason]
- [Connection type]: because [reason]

This means [key implication]. Does that match your understanding?"

### Phase 3: Map Components to Services

For each component in the system, select an AWS service. **One component at a time.** Do NOT present a table of 10 components with pre-selected services. Walk through each decision as a conversation turn.

**For each component:**

1. Name the component and its role
2. Present 2 viable options with trade-offs (not 5 options — decision fatigue)
3. State which you'd recommend and why
4. Ask: "Does this align with what your platform team uses? Any constraints I should know?"
5. Wait for response before moving to the next component

**Key references:**
- Compute decisions (Lambda vs Fargate vs EC2) → `references/compute-decision-framework.md`
- AI agent specifics (SSE, sidecars, sessions) → `references/aws-agent-workloads.md`
- Team capacity constraints → `references/team-capacity.md`

**CHECKPOINT after mapping all components:**

"Here's the component map:
| Component | AWS Service | Why |
|-----------|------------|-----|
| [each one] | [service] | [1-line rationale] |

Anything feel wrong? Any platform team concerns?"

### Phase 4: Cost & Scaling Model

Present back-of-envelope costs. AI workloads have a specific cost profile — see `references/aws-agent-workloads.md`.

For each component:
- Estimated monthly cost at current scale
- What drives cost up (scaling dimension)
- Break point where architecture needs to change

**CHECKPOINT:** Present cost estimate before finalizing.

### Phase 5: Produce Infrastructure Spec

Generate a structured spec that:
1. Lists every component, its AWS service, and configuration
2. Shows connections between components (what talks to what, over what protocol)
3. Groups components into logical layers (frontend, compute, data, external)
4. Maps to the architecture-diagram skill's node types (ui, agent, gateway, mcp, external, data)

**Output format:**

```markdown
## Infrastructure Spec: [Project Name]

### Organizational Constraints
- Platform: [what's mandated]
- Auth: [solution]
- Secrets: [solution]
- Logging: [solution]

### Components
| Component | AWS Service | Config | Cost Est. |
|-----------|------------|--------|-----------|
| [name] | [service] | [key config] | [$/mo] |

### Connections
| From | To | Protocol | Notes |
|------|-----|----------|-------|
| [source] | [target] | [HTTP/SSE/gRPC] | [timeout, auth] |

### Diagram Nodes
[Ready for architecture-diagram skill — node types, groups, edges]

### Open Questions
[What still needs platform team input]

### Cost Summary
- Monthly estimate: $X at current scale
- Primary cost driver: [what]
- Scale inflection point: [when architecture needs to change]
```

After spec is approved, offer to invoke the **architecture-diagram** skill to visualize it.

## Bias Guards

| Thought | Reality | Do Instead |
|---------|---------|------------|
| "Let's use Kubernetes" | K8s operational overhead is massive for small teams | Start with ECS/Fargate unless K8s is mandated |
| "We need multi-region from day 1" | Multi-region doubles complexity and cost | Single region + backups until traffic justifies it |
| "Let's add a service mesh" | Service meshes add weeks of setup and ongoing maintenance | Direct service-to-service until you have >10 services |
| "Serverless everything" | Some workloads (long-running, stateful) are bad fits for Lambda | Match compute to workload characteristics |
| "The platform team won't care" | Platform teams always care. Unapproved services get blocked | Ask first, design second |
| "Let's design for 10x scale" | Premature scaling adds complexity NOW for hypothetical LATER | Design for current + 3x. Redesign when you hit 3x |

## Anti-Patterns

| Anti-Pattern | What Happens | This Skill Prevents It By |
|--------------|-------------|--------------------------|
| Designing in a vacuum | Architecture gets rejected by platform team | Phase 1 mandates constraint discovery first |
| Big bang architecture | 50-service design that takes 6 months to build | Progressive complexity — start simple, add layers |
| Resume-driven development | Choosing K8s/Istio/Kafka because it looks good, not because it's needed | Team capacity constraints + bias guards |
| Copy-paste from a blog post | Architecture doesn't fit your specific workload | Workload classification drives service selection |
| Ignoring token costs | $500/mo compute bill + $5000/mo LLM bill = wrong optimization target | AI-specific cost model in Phase 4 |

## Guidelines

- **Constraints before creativity.** Organizational mandates are non-negotiable. Find them first.
- **Two options, not seven.** Present the realistic choice, not every possible option. Decision fatigue kills design conversations.
- **Name the problem before adding complexity.** Every additional service, every additional pattern, every additional layer — can you name the specific problem it solves? If not, don't add it.
- **Team size is a constraint.** A 2-person team cannot operate Kubernetes, a service mesh, and a multi-region deployment. Design for the team you have.
- **Token costs dominate AI workloads.** In a typical AI agent system, 70% of cost is LLM inference. Optimizing compute without optimizing prompts is looking under the streetlight.
- **Checkpoint relentlessly.** Every phase ends with user confirmation. The cost of pausing to confirm is low. The cost of designing the wrong architecture is weeks.

Follow the communication-protocol skill for all user-facing output and interaction.
