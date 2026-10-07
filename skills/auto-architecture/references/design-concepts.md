# Design concepts — styles and tactics, with their trade-offs

Reference for the auto-architecture skill. Load in round 2 (High-level shape) and in deep dives. Sources:
Richards & Ford, *Fundamentals of Software Architecture* 2e (2025); Bass, Clements & Kazman 4e (2021) tactics;
Cockburn, ports and adapters (2005); Fowler, MonolithFirst (2015). All entries are **opinion** (canonical
authors) unless marked.

## Rule for round 2

Offer 2–3 shapes, **simplest first**. Each further option must name the quality it buys and the cost it adds
over the simplest. For a new product built by one person with agents, the default first option is a **modular
monolith with ports and adapters**; anything else must justify itself against it.

## Architecture styles

| Style | What it is | Buys | Costs | Choose when |
|---|---|---|---|---|
| **Layered** | Presentation → application → domain → data, each layer calls down | Familiarity, simple start | Changes cut across all layers; tends to an anaemic domain | Small CRUD apps with little domain logic |
| **Modular monolith** | One deployable, internally split into modules by domain with enforced boundaries | Atomic refactors, one deploy, cheap transactions, boundaries an agent can see | One scaling unit, one failure domain; boundaries erode without rules | Default for a new product; north-star containers start here as modules |
| **Ports and adapters** (hexagonal) | Domain and use cases own port interfaces; adapters for DB, HTTP, providers sit outside | Testability (ports are mock seams), swappable infrastructure, one simple rule (`domain` imports nothing outside) | Extra interfaces; over-abstraction if a port has one adapter forever | Combine with modular monolith; almost always worth it at container edges |
| **Event-driven** | Components react to events through a broker or log | Decoupling in time, fan-out, audit trail | Eventual consistency, harder debugging, ordering and duplicate handling | Many independent reactions to one fact; integration with slow or flaky systems |
| **Microkernel** (plugin) | Small core plus plugins through an extension interface and registry | Extensibility without core changes | Plugin contract versioning; speculative extension points are shallow abstractions | Two or more real variants exist today, not "maybe later" |
| **CQRS** | Separate write model and read models | Read performance and shape freedom | Two models to keep in sync; usually brings eventual consistency | Read and write loads or shapes differ sharply |
| **Microservices** | Independently deployed services, each owning its data | Independent deploy and scaling, team autonomy, fault isolation | Network failure modes, distributed data, ops cost, harder refactors | Independent release cadence, ownership, or scaling need that a monolith cannot meet. Split late (MonolithFirst) |

The complexity ladder for orchestration (reuse from the existing `architecture` skill when merged): direct call
→ single service → orchestration. Move up a rung only when the lower rung fails a top-3 scenario.

## Tactics, by quality attribute

Bring these as options in deep-dive cards. Each line: tactic — what it costs.

**Availability / fault tolerance**
- Timeouts and retries with backoff — duplicate work; needs idempotency.
- Idempotency keys — storage and key design.
- Circuit breaker — degraded responses to design.
- Queue the work (outbox, job table) — eventual completion, ops of the queue.
- Redundancy (replicas, failover) — cost, consistency choices.
- Graceful degradation — product decisions about what to drop.

**Performance**
- Cache (read-through, at edge) — staleness, invalidation.
- Precompute / denormalised read model — write cost, sync.
- Batch — latency for throughput.
- Concurrency and async I/O — complexity, ordering.
- Limit demand (rate limits, backpressure) — rejected requests.

**Security**
- Authenticate and authorise at one boundary — a choke point to keep fast.
- Least privilege per component — more credentials to manage.
- Encrypt at rest and in transit — key management.
- Validate at trust boundaries — schema upkeep.
- Audit log — storage, privacy of the log itself.

**Modifiability**
- Encapsulate behind a port — an interface to maintain.
- Split by domain (bounded context) — integration between contexts.
- Defer binding (config, plugins) — runtime errors instead of compile errors.
- Reduce coupling with events — eventual consistency.

**Integrity / consistency**
- Single-writer ownership per entity — routing through the owner.
- Transactional outbox — a relay process.
- Exactly-once via idempotent consumers — key storage and expiry.

## Boundaries and data ownership (round 1 and deep dives)

- One bounded context = one module (or crate) with its own model (Evans 2003). It owns its tables; others reach
  it through its port, never its tables.
- Aggregates are consistency boundaries: one transaction changes one aggregate.
- A module one agent session can hold whole is about the right size (judgement, from Team Topologies' cognitive
  load applied to context windows).
