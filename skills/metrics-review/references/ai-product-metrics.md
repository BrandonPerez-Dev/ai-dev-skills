# AI/Agent Product Metrics Supplement

AI products break standard metrics assumptions. Accuracy is not a feature — it's a spectrum. User trust is not binary — it degrades with each bad output and recovers slowly. These metrics supplement the standard catalog for any product with AI/agent components.

## Why AI Products Need Additional Metrics

| Dimension | Traditional Software | AI / Agent Product |
|---|---|---|
| **Correctness** | Deterministic — same input, same output | Probabilistic — same input, different outputs |
| **Failure mode** | Crashes, errors (visible) | Hallucinations, subtle wrongness (invisible) |
| **User trust** | Binary — it works or it doesn't | Gradient — erodes with each bad output |
| **Quality over time** | Stable unless code changes | Drifts — model updates, data distribution shifts |
| **Cost structure** | Fixed per request (compute) | Variable per request (tokens, model calls, retries) |

## AI Quality Metrics

| Metric | What It Measures | How to Measure | Watch Out For |
|---|---|---|---|
| **Task completion rate** | % of tasks the AI completes successfully | End-to-end eval suite; user-reported success | "Completed" != "correct" — measure correctness separately |
| **Hallucination rate** | % of outputs containing fabricated information | LLM-as-judge evals; human spot-checks | Low hallucination rate on easy tasks masks high rate on hard tasks — segment by task complexity |
| **Faithfulness** | Does the output stay grounded in provided context? | Automated faithfulness evals; citation verification | High faithfulness + wrong context = confidently wrong |
| **Latency (AI-specific)** | Time from request to complete response | p50/p95/p99 by task type | Streaming hides true latency — measure time-to-useful-output, not time-to-first-token |

## User Trust Signals

These are the behavioral metrics that reveal whether users actually trust the AI output.

| Metric | What It Signals | Healthy Range | Red Flag |
|---|---|---|---|
| **Regeneration rate** | User rejected the output and asked again | < 10% | > 25% — users are slot-machining for a good answer |
| **Edit rate** | User modified the AI output before using it | 20-40% (some editing is expected) | > 60% — AI is a rough draft generator, not an assistant |
| **Override rate** | User explicitly chose a non-AI path | < 15% | > 30% — users don't trust the AI for this task |
| **Abandonment at AI step** | User dropped the flow at the AI interaction point | < 10% | > 20% — the AI step is a barrier, not a feature |
| **Copy rate** | User copied AI output verbatim | 30-50% for content generation | < 10% — nobody is using the output as-is |
| **Feedback rate** | Users providing thumbs up/down or corrections | 5-15% of interactions | < 1% — feedback mechanism is invisible or users gave up |

## Eval Infrastructure Metrics

Track the health of your evaluation system itself — if evals are broken, all quality metrics are suspect.

| Metric | What It Measures | Target | Why It Matters |
|---|---|---|---|
| **Eval coverage** | % of production task types covered by evals | > 80% of task types | Uncovered task types have unknown quality |
| **Grader agreement** | Inter-rater reliability of automated graders | > 85% agreement with human judges | Low agreement = grader is measuring noise, not quality |
| **Eval freshness** | How recently eval sets were updated | Updated within last quarter | Stale evals test yesterday's use cases |
| **Regression detection time** | How quickly quality drops are caught | < 24 hours for critical regressions | Slow detection = users find the problem before you do |

## Cost Efficiency Metrics

AI products have variable cost structures that traditional software doesn't. These must be tracked alongside quality.

| Metric | What It Measures | How to Track | Watch Out For |
|---|---|---|---|
| **Cost per task completion** | Total AI cost to complete one user task | Sum all model calls, retries, tool use per task | Average hides distribution — some tasks may cost 100x more |
| **Token efficiency** | Useful output tokens / total tokens consumed | Track input + output + retry tokens | Retries and long context windows silently inflate cost |
| **Human fallback rate** | % of tasks requiring human intervention | Track escalations, manual overrides | High fallback = AI is a routing layer, not an automation |
| **Cost per quality point** | Cost to achieve each percentage point of accuracy | Cost / accuracy score | Diminishing returns — going from 90% to 95% may cost 3x more than 80% to 90% |

## How to Use This in a Metrics Review

During any metrics review for an AI/agent product:

1. **Run standard metrics first** — acquisition, activation, engagement, retention, revenue still apply
2. **Layer AI quality metrics** — task completion and hallucination rate are the minimum
3. **Check trust signals** — behavioral metrics reveal what users actually think, regardless of what they say
4. **Verify eval health** — if grader agreement is low, discount all automated quality metrics
5. **Track cost efficiency** — especially after model upgrades or prompt changes

**Key principle:** AI metrics are supplemental, not replacement. A product with 99% task completion but 5% monthly churn still has a retention problem. AI quality is necessary but not sufficient for product success.
