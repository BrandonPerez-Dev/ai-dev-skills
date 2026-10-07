# Quality attributes — scenarios, ranking, response measures

Reference for the auto-architecture skill. Load in round 0 (Frame) and whenever the top-3 qualities change.
Sources: Bass, Clements & Kazman, *Software Architecture in Practice* 4e (2021); Keeling, *Design It!* (2017,
read second-hand); ISO/IEC 25010 for terms; Richards & Ford, *Fundamentals of Software Architecture* 2e (2025).

## Why only three

Qualities conflict: every gain in one is paid for in another. Pick a few driving qualities and aim for the
"least worst" architecture for them (Richards & Ford). The node's rule budget caps this at **3 quality
scenarios** (gate G3). Everything else is either implicit or explicitly a non-goal.

## Vocabulary (ISO/IEC 25010 terms)

Use these names on the page so the person learns one consistent vocabulary:

| Quality | Ask the person |
|---|---|
| Performance efficiency (time behaviour, capacity) | How fast, for how many, on what hardware? |
| Reliability (availability, fault tolerance, recoverability) | What happens when a dependency is down? How much data loss is acceptable? |
| Security (confidentiality, integrity, accountability) | Who must never see or change what? What must be traceable? |
| Maintainability (modularity, modifiability, testability) | What is most likely to change in the next year? |
| Compatibility (interoperability) | What must this talk to that you do not control? |
| Portability (adaptability, replaceability) | What would you want to swap out later? |
| Usability | Which user task must stay fast and obvious? |

Add, when relevant: **cost** (run cost per month or per unit), **operability** (who is woken at 3 a.m.), and
**agent-buildability** (how well coding agents handle the chosen stack — see `technology-selection.md`).

## The scenario template

Every candidate quality is written as a six-part scenario. The **response measure** is what makes it testable;
a scenario without a number is not accepted (gate G4).

| Part | Example |
|---|---|
| Source | A returning customer |
| Stimulus | Places an order |
| Artifact | Place-order use case |
| Environment | Normal load, 50 rps, on the reference box |
| Response | Order accepted and confirmed |
| **Response measure** | p95 < 300 ms |

One-line form for the page: *"Under normal load (50 rps), a customer placing an order gets confirmation with
p95 < 300 ms."*

## Round 0: the mini quality-attribute workshop

Bring 6–10 candidate scenarios drafted from the frame. For each, the person answers two questions:
- **Importance** — high / medium / low to the business.
- **Difficulty** — high / medium / low for the architecture (you propose this; the person can overrule).

Prompts to draft candidates:
- What would make a user leave? (performance, usability)
- What would make the news, or lose a customer's data? (security, reliability)
- What will change first? (modifiability)
- What will the bill look like at 10× today? (cost, scalability)
- What breaks when the payment / email / LLM provider is down? (fault tolerance)

## The utility tree

Arrange the rated scenarios as a tree: quality → refinement → scenario (importance, difficulty). The top 3 are
the (high, high) ones first, then (high, medium). Show the tree on the round-0 page; the person picks the final
three and gives each its number.

```
Utility
├── Performance
│   └── Order confirmation p95 < 300 ms at 50 rps          (H, M)
├── Reliability
│   └── Payment outage → 503 within 2 s, order stays pending (H, H)
└── Integrity
    └── Exactly-once order creation under client retry       (H, H)
```

## Where each top-3 scenario goes next

Each becomes a row in `spec/architecture-invariants.md` with a fitness kind (see `boundary-rules.md`):
- `structural` — enforced by a boundary rule in lint;
- `test` — an integration or load test (latency and load go to the verification-planning check catalogue);
- `manual: <reason>` — a named review question, visible as a gap.

## Tactics

When a deep-dive round targets one quality, draw options from the tactics in `design-concepts.md` § Tactics.
