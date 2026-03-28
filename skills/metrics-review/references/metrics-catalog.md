# Metrics Catalog

Reference benchmarks by category. Use these as starting points — every product needs its own baselines, but these prevent "is this good?" conversations from stalling a review.

## Acquisition

| Metric | What It Measures | Benchmark | Watch Out For |
|---|---|---|---|
| **CAC** | Cost to acquire one customer | Varies by channel; track trend, not absolute | Rising CAC with flat LTV = unsustainable |
| **LTV:CAC ratio** | Unit economics health | >= 3:1 healthy; < 1:1 burning cash | Blended ratio hides channel-level problems — segment by channel |
| **Conversion by channel** | Channel quality | Organic > Paid (typically) | High-volume low-conversion channels inflate top-of-funnel vanity metrics |
| **Payback period** | Time to recover CAC | < 12 months for SaaS | Long payback + high churn = never recovering the investment |

## Activation

| Metric | What It Measures | Benchmark | Watch Out For |
|---|---|---|---|
| **Activation rate** | % of signups reaching value | 37.5% average; 50%+ best-in-class | Defining activation too loosely (e.g., "completed onboarding" vs. "experienced core value") |
| **Time-to-value** | How fast users hit the aha moment | Shorter is better; measure in minutes/hours, not days | Long TTV with decent activation = users who survive are good, but you're losing the rest |
| **Aha moment** | The action that predicts retention | Product-specific; find via cohort analysis | Correlation != causation — forcing the aha action doesn't guarantee retention |

## Engagement

| Metric | What It Measures | Benchmark | Watch Out For |
|---|---|---|---|
| **DAU/MAU (stickiness)** | How often monthly users return daily | 20% decent; 50%+ exceptional (messaging apps) | High stickiness can mask flat growth — you're retaining but not acquiring |
| **Feature adoption** | % of users using a specific feature | Varies; track adoption curves over time | Low adoption != bad feature. Could be discoverability, not value. |
| **Session depth** | Actions per session | Product-specific | Depth without outcome = user is lost, not engaged |
| **L7/L28** | Active days in last 7/28 days | Distribution matters more than average | Average hides bimodal distribution (power users + dormant) |

## Retention

| Metric | What It Measures | Benchmark | Watch Out For |
|---|---|---|---|
| **Cohort retention curves** | How many users remain over time | Curve should flatten, not keep declining | If the curve never flattens, you don't have product-market fit |
| **Churn rate (monthly)** | % of customers lost per month | B2B SaaS avg: 3.5% monthly | Logo churn vs. revenue churn tell different stories |
| **Gross Revenue Retention (GRR)** | Revenue kept from existing customers (excl. expansion) | 85%+ good; 95%+ excellent | GRR < 80% means your base is eroding faster than you can expand |
| **Net Revenue Retention (NRR)** | Revenue from existing customers incl. expansion | Median 106%; 120%+ best-in-class | NRR > 100% masks logo churn — you're growing revenue but losing customers |
| **Day 1 / Day 7 / Day 30** | Short-term retention checkpoints | D1: 40%+; D7: 20%+; D30: 10%+ (consumer) | B2B benchmarks are higher; consumer benchmarks vary wildly by category |

## Revenue

| Metric | What It Measures | Benchmark | Watch Out For |
|---|---|---|---|
| **MRR waterfall** | New + Expansion - Contraction - Churn = Net MRR change | Net positive = growing | Contraction hiding behind new business — "growing" while existing base shrinks |
| **Expansion revenue %** | Revenue growth from existing customers | 20-30% of new MRR from expansion is healthy | Over-reliance on expansion means new business engine is weak |
| **LTV by cohort** | Lifetime value segmented by signup cohort | Should be stable or increasing | Declining LTV by cohort = product quality or market fit is degrading |
| **ARPU** | Average revenue per user | Track trend; absolute varies by market | ARPU increasing via price hikes vs. value delivery — different stories |

## Performance

| Metric | What It Measures | Benchmark | Watch Out For |
|---|---|---|---|
| **p50/p95/p99 latency** | Response time distribution | p50 < 200ms; p99 < 1s (web); product-specific for AI | p50 is fine but p99 is terrible = 1% of users having a bad time |
| **Error rate** | % of requests that fail | < 0.1% for critical paths | Low error rate + high error impact = rare but catastrophic |
| **Uptime** | System availability | 99.9% = 8.7 hours downtime/year | Uptime doesn't capture degraded performance — "up but slow" isn't up |
| **Apdex score** | User satisfaction with performance | > 0.9 good; < 0.7 concerning | Blends tolerance thresholds — check the raw latency distribution too |
