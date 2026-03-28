# AI/Agent Product Roadmap Considerations

AI products break standard roadmapping assumptions. These categories belong on the roadmap as first-class initiatives — not buried in tech debt.

## Why AI Products Need Different Roadmap Items

| Dimension | Traditional Software | AI / Agent Product |
|---|---|---|
| **Feature certainty** | High (deterministic) | Low (probabilistic, model-dependent) |
| **Definition of "done"** | Feature ships, criteria met | Accuracy target reached AND maintained |
| **External invalidation** | Rare | Frequent (new model release, API pricing change, open-source can obsolete overnight) |
| **Data as infrastructure** | Not on roadmap | Data pipelines, labeling, eval sets ARE roadmap items |
| **Rollback** | Deterministic (revert deploy) | Complex (retraining, eval regression, prompt regression) |

## AI-Specific Initiative Categories

| Category | Why It's a Roadmap Item | Example Initiative |
|---|---|---|
| **Eval framework** | You can't ship what you can't measure | "Build eval suite achieving 90% grader agreement" |
| **Data pipeline / curation** | Often 2-4x engineering effort; must be sequenced | "Curate 10K labeled examples for trade classification" |
| **Trust & transparency** | User trust is a feature, not an afterthought | "Add citation sourcing to all agent recommendations" |
| **Guardrails & safety** | Compliance and safety are capabilities | "Implement PII detection with <0.1% false negative rate" |
| **Human-in-the-loop design** | Core product decision, not an eng detail | "Define escalation criteria for agent-to-human handoff" |
| **Prompt regression testing** | Changes break existing behavior silently | "Automated regression suite covering top 20 user workflows" |
| **Model drift monitoring** | Post-launch quality degrades over time | "Weekly quality scoring with automated alerting" |

## Key Principle

**Roadmap capability tiers, not model versions.** "Conversational memory" is a stable roadmap item. "Integrate GPT-5" is not — it's an implementation detail that will be wrong by next quarter. Anchor AI roadmap items to user-facing capabilities and measurable quality thresholds.

## When to Include

Don't add these categories mechanically. Include what's relevant to the product's current stage:

- **Pre-launch:** Eval framework, data pipeline, guardrails are roadmap-critical
- **Post-launch:** Model drift monitoring, prompt regression testing become relevant
- **Scaling:** Human-in-the-loop design, trust features matter at volume
