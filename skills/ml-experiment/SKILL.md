
---
name: ml-experiment
description: >-
  Disciplined ML experimentation for building small models — classification, regression,
  anomaly detection, clustering, time series. Use when building a model from scratch,
  evaluating whether ML is the right approach, or improving an existing model's performance.
  Covers problem framing, baseline selection, iteration discipline, evaluation methodology,
  and the decision to ship or abandon. Not for large-scale MLOps, LLM fine-tuning, or
  data engineering pipelines.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
  - ToolSearch
---

# ML Experiment

Baseline first, iterate with evidence, stop when the metric plateaus.

<HARD-GATE>
Do NOT skip the baseline. Every experiment needs a simple reference point — a rule-based heuristic, a linear model, or even a constant prediction. If you can't beat the baseline, ML isn't solving your problem. If you skip the baseline, you have no way to know if your complex model is actually adding value.
</HARD-GATE>

## Method Selection

| Problem Type | Default Baseline | Default Model | Key Metric |
|-------------|-----------------|---------------|------------|
| **Binary classification** | Logistic regression | Gradient boosting (XGBoost/LightGBM) | PR-AUC for imbalanced; ROC-AUC for balanced |
| **Multi-class classification** | Logistic regression (OVR) | Gradient boosting or random forest | Macro F1 (balanced) or weighted F1 (imbalanced) |
| **Regression** | Linear regression | Gradient boosting | MAE for interpretability; RMSE if large errors matter more |
| **Anomaly detection** | Statistical thresholds (z-score, IQR) | Isolation forest | Precision@k or F1 at chosen threshold |
| **Clustering** | K-means | HDBSCAN | Silhouette score + domain expert review |
| **Time series** | Seasonal naive (last period's value) | Prophet or LightGBM with lag features | MAPE or RMSE; always compare to naive |
| **"Is ML right for this?"** | Rule-based system | — | If rules get you 80%+ of the way, ship rules |

## Process

### Phase 1: Problem Framing

Before writing any code, answer these:

**The problem:**
- What are you predicting / detecting / grouping? State it in one sentence.
- What decision does the model's output inform? (If no decision, why build a model?)
- What does "good enough" look like? Define a target metric value.

**The data:**
- What data exists today? How much? How clean?
- What's the label source? (Human-labeled, implicit signal, derived?)
- Is there class imbalance? What's the ratio?

**The constraints:**
- Latency requirement? (Real-time inference vs batch?)
- Interpretability needed? (Regulated domain, user-facing explanations?)
- How often does the model need retraining?

**The ML sanity check:**
- Is there a pattern in the data a model could learn? (Not all problems have signal.)
- Could a rules-based approach work? (If yes, try it first — it's cheaper to maintain.)
- Is the cost of being wrong symmetric? (False positive vs false negative — which is worse?)

**Checkpoint:** "Here's how I've framed the problem. Does this match your understanding?"

### Phase 2: Data Assessment

**Explore before modeling.** Understand what you have.

- **Shape:** rows, columns, types, missing values, cardinality of categoricals
- **Target distribution:** balanced? skewed? how many classes?
- **Feature quality:** correlations with target, obvious leakage, redundant features
- **Data splits:** define train/validation/test now, before any modeling. Never touch test until final evaluation.

**Red flags to catch early:**
- Target leakage (feature that wouldn't be available at prediction time)
- Temporal leakage (future data leaking into training via random splits — use time-based splits for temporal data)
- Label noise (inconsistent or incorrect labels — spot-check a sample)
- Survivorship bias (only seeing data from successful cases)

**Checkpoint:** "Here's what the data looks like. These are the quality issues. Proceeding to baseline."

### Phase 3: Baseline

Build the simplest possible model. This is your reference point.

**Good baselines by problem type:**
- Classification → logistic regression with minimal features
- Regression → linear regression or mean/median prediction
- Time series → seasonal naive (repeat last cycle's value)
- Anomaly detection → statistical thresholds (mean ± 2σ)
- Clustering → k-means with elbow method

**Record the baseline:**
- Metric value on validation set
- Training time
- Inference time
- Number of features used

Every subsequent experiment must justify its added complexity by beating this number.

### Phase 4: Iteration

Systematic improvement, one variable at a time. Each iteration is an experiment with a hypothesis.

**Iteration order** (highest leverage first):

1. **Better features** → feature engineering, feature selection, handling missing values
2. **Better model** → try gradient boosting if baseline was linear; try neural net only if tree models plateau
3. **Hyperparameter tuning** → only after model selection; use Optuna or similar, not manual grid search
4. **More data** → if performance is still poor, the issue may be data volume or quality

**Experiment tracking:**
For each iteration, record:
- What changed (one thing)
- Hypothesis ("adding interaction features should capture X")
- Result (metric on validation set)
- Decision (keep, revert, or investigate further)

**When to escalate model complexity:**

| Current Model | Escalate When | Escalate To |
|--------------|---------------|-------------|
| Linear/logistic | Feature engineering plateaus; non-linear patterns visible | Gradient boosting (XGBoost/LightGBM) |
| Gradient boosting | Tabular data exhausted; need unstructured input (text, images) | Neural network (start small) |
| Small neural net | Underfitting with available architecture | Larger architecture or pre-trained embeddings |

**When NOT to escalate:**
- Validation metric is within 2% of target — ship the simpler model
- Training data is small (< 1K rows) — complex models overfit
- Interpretability is required — tree models with SHAP values

**Checkpoint:** "Here's where we are after N iterations. [Best metric] vs [baseline]. My recommendation is [continue/ship/stop]."

### Phase 5: Evaluation

Final evaluation on the held-out test set. You get ONE shot at this — multiple test evaluations leak information.

**Evaluation checklist:**
- [ ] Test set metric is within reasonable range of validation metric (no large gap)
- [ ] Performance checked across subgroups (does the model fail for certain categories?)
- [ ] Confusion matrix reviewed (where are the errors?)
- [ ] Error analysis: examine the worst predictions — are they data issues or model limitations?
- [ ] Calibration check for classification (predicted probabilities match observed frequencies?)

**Choosing the right metric:**

| Situation | Don't Use | Use Instead | Why |
|-----------|----------|-------------|-----|
| Imbalanced classes (< 10% positive) | Accuracy | PR-AUC, F1, precision@k | Accuracy is misleading — predicting all-negative gets 90%+ |
| Errors have asymmetric cost | Symmetric metrics (accuracy, F1) | Cost-weighted metrics or threshold optimization | A false negative in fraud detection costs more than a false positive |
| Regression with outliers | RMSE alone | MAE + RMSE together | MAE is robust to outliers; RMSE penalizes large errors |
| Ranking / recommendation | Classification metrics | NDCG, MAP, precision@k | You care about order, not just correctness |

### Phase 6: Decision

Three outcomes. Be honest about which one applies.

**Ship it:**
- Model beats baseline by a meaningful margin
- Performance is stable across subgroups
- Deployment constraints are met (latency, memory, interpretability)
- Monitoring plan exists (how will you detect drift?)

**Iterate more:**
- Model shows promise but hasn't hit target metric
- Clear hypothesis for next improvement exists
- Data or feature quality issues identified but fixable

**Abandon ML:**
- Model can't beat the baseline meaningfully
- Rules-based approach gets close enough
- Data quality is fundamentally insufficient
- Cost of maintaining an ML system outweighs the benefit

Abandoning ML is a valid outcome, not a failure. A rules-based system that's maintainable beats an ML model nobody understands.

## Bias Guards

| Trap | Reality | Do Instead |
|------|---------|------------|
| "Let me try a neural network" | Start simple. Neural nets need more data, more tuning, and are harder to debug | Gradient boosting first for tabular data; neural nets only for unstructured input |
| "Accuracy is 95%!" | With 5% positive rate, predicting all-negative gives 95% accuracy | Check precision, recall, F1, and the confusion matrix |
| "More data will fix it" | Sometimes the signal isn't in the data, or the labels are wrong | Error analysis first — understand WHY it's wrong |
| "The model is done" | Data leakage, distribution shift, and fairness issues hide in good metrics | Run the evaluation checklist; spot-check predictions manually |
| "I'll clean the data later" | Garbage in, garbage out | Data quality is Phase 2, not an afterthought |
| "This feature improves the metric" | If the feature wouldn't be available at prediction time, it's leakage | Check temporal validity of every feature |

## Anti-Patterns

| Anti-Pattern | What Goes Wrong | Prevention |
|--------------|----------------|------------|
| **No baseline** | No way to know if the model adds value; complexity without evidence | Phase 3 is mandatory |
| **Metric shopping** | Trying metrics until one looks good | Choose the metric in Phase 1 before seeing any results |
| **Test set peeking** | Evaluating on test set during iteration; inflated final score | One test evaluation, at the end, period |
| **Feature kitchen sink** | Throwing all available features in; overfitting, leakage risk | Feature engineering is deliberate; add features one at a time with hypotheses |
| **Complexity ratchet** | Each iteration adds complexity but never removes it | Periodically retrain from scratch with best feature set |
| **Ship and forget** | Model deployed with no monitoring; performance degrades silently | Define monitoring before deployment: drift detection, metric alerts |

## MCP Tools

Use `ToolSearch` to discover available ML/notebook MCP tools at the start of any experiment.

**Jupyter MCP Server** (`datalayer/jupyter-mcp-server`) — If available, use it to create and execute notebook cells, inspect outputs, and maintain kernel state. Natural workspace for ML experimentation — keeps data exploration, model training, and evaluation in one place.

**MLflow MCP Server** (`kkruglik/mlflow-mcp`) — If available, use it for experiment tracking: log metrics, compare runs, and access model registry. Valuable in Phase 4 (iteration) for systematic experiment tracking.

If neither is available, use Bash to run Python scripts directly and track experiments in a simple markdown log or CSV.

## Guidelines

- **ML is a tool, not a goal.** If rules solve the problem, ship rules. ML adds maintenance cost — it must earn its place.
- **One variable per experiment.** Change one thing, measure, decide. Changing multiple things makes it impossible to attribute improvement.
- **Simple models are features, not bugs.** Logistic regression with good features often matches gradient boosting. Ship the simpler model when performance is comparable.
- **Error analysis over metric chasing.** Understanding WHY the model is wrong is more valuable than nudging the metric up 0.5%.
- **Data quality over model quality.** An hour spent cleaning data is usually worth more than an hour tuning hyperparameters.
