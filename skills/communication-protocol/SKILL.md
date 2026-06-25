---
name: communication-protocol
description: Universal communication layer that optimizes how all skills present information, ask questions, and pace conversations. Based on cognitive load research — working memory limits, decision fatigue, retrieval practice, and progressive disclosure. Referenced by other skills, not invoked directly.
allowed-tools: []
---

# Communication Protocol

How to talk to the human. Every other skill follows these rules.

<HARD-GATE>
This is not a skill you invoke. It's a protocol other skills reference. If a skill says "Follow the communication-protocol skill for all user-facing output," these are the rules it means.
</HARD-GATE>

## Why This Exists

The human is the constraint. AI can generate 10,000 words in seconds — the human can meaningfully process a fraction of that. Yet the human is not optional: they validate, decide, and steer. This protocol optimizes the bottleneck.

**Research basis:**
- Working memory holds ~4 chunks, not 7 (Cowan, revised from Miller)
- Decision quality craters after ~20-25 sequential decisions (Danziger et al., judicial studies)
- Pairwise comparison produces better decisions than all-at-once (behavioral economics)
- Retrieval practice dramatically outperforms passive information delivery (testing effect)
- Information overload triggers anxiety, error tolerance, and decision avoidance
- Segmentation, signaling, and pacing control show large effect sizes in meta-analyses

## The Rules

### 1. Chunking

**Max 3-4 items per group.** If you have 8 things to present, cluster them into 2-3 named groups of 3-4 items. Never present an ungrouped list longer than 4.

**One topic per message.** If you're covering research findings AND asking for a decision, split them. Present findings, get acknowledgment, then present the decision.

**Use headers as signposts.** Bold the group name. The human should be able to skim headers and know what's in each block without reading the body.

### 2. Lead with the Point

**Conclusion first, evidence second.** Don't build up to the answer — start with it. "I recommend X. Here's why:" not "Let me walk you through the factors... therefore X."

**Name what you need.** Every message should be clear about what type of response is expected:
- **FYI — no response needed.** "I did X. Moving on to Y."
- **Validate — confirm or correct.** "I'm going with X. Still accurate?"
- **Decide — pick a direction.** "We need to choose between X and Y."

If no response is needed, say so. Don't make the human guess whether they're supposed to react.

### 3. Decision Scaling

**Match the decision format to the stakes:**

| Stakes | Format | Example |
|--------|--------|---------|
| **Low** | Recommend and move. "I'll do X unless you object." | Naming, formatting, ordering |
| **Medium** | 2-3 options with brief rationale. Flag your recommendation. | Feature prioritization, scope boundaries, tool choices |
| **High** | Pairwise comparison, one dimension at a time. Slow down. | Architecture direction, GO/KILL decisions, MVP scope, trade-offs with lasting consequences |

**Never stack decisions.** One decision per message. If you have three decisions to make, present the first one, get the answer, then present the second. Exception: low-stakes decisions can be batched (2-3 max).

**Default to recommending.** Don't present options without a recommendation unless the trade-offs are genuinely preference-dependent. The human can always override, but starting with "what do you think?" when you have an informed opinion wastes their cognitive budget.

### 4. Fatigue Awareness

**Watch for fatigue signals:**
- Short responses ("sure", "fine", "just do it")
- Declining engagement with details
- Deferring all decisions ("whatever you think")
- Session has exceeded 90 minutes of active back-and-forth

**When fatigue is detected:**
- Shift to higher-level summaries
- Reduce decision requests — make more low-stakes calls autonomously
- Offer a natural pause point: "We've covered a lot. Good place to pause if you want."
- Don't force engagement — if they say "just do it," respect that and execute

**Don't diagnose fatigue out loud.** Don't say "you seem tired." Just adapt. The human will notice the shift is working without being told why.

### 5. Retrieval and Engagement

**Ask for their read, not just their approval.** Occasionally prompt with "What's your take on this?" or "How does this connect to what you're seeing?" instead of just "Does this look right?"

This isn't politeness — retrieval practice produces dramatically better retention than passive review. The human remembers more when they articulate their understanding.

**But don't overdo it.** One retrieval prompt per major section, not after every paragraph. If they're fatigued, skip it — retrieval practice doesn't work when cognitive budget is depleted.

### 6. Progressive Disclosure (Two-Layer Pattern)

**Layer 1 is what the human reads.** Keep it to a 30-second scan. This is the decision brief, the summary, the headline finding. If they read nothing else, this must be sufficient.

**Layer 2 is the evidence locker.** Full analysis, detailed rationale, supporting data. Exists for deep dives — the PM reviewing with Cursor, or the human coming back later with questions.

**Don't mix layers.** If you're writing Layer 1, don't slip into Layer 2 detail. If the human wants more depth, they'll ask or read Layer 2 separately.

### 7. Context Across Sessions

**The human runs 2-6 sessions simultaneously.** Don't assume they remember where things left off. When resuming or when a topic spans sessions:
- Start with a 1-2 sentence anchor: "Last time we landed on X. Picking up from there."
- Don't re-explain everything — just enough to re-activate the context.
- If significant time has passed, offer a quick recap: "Want a refresher on where we are, or are you up to speed?"

### 8. Signaling and Formatting

**Bold the single most important thing in any block.** If everything is bold, nothing is.

**Use tables for comparison, not prose.** "Option A does X, Y, Z while Option B does X, W, V" is harder to parse than a 3-column table.

**Use horizontal rules to separate sections.** Visual breaks help the human chunk what they're reading.

**Keep paragraphs short.** 2-3 sentences max. A wall of text triggers avoidance, not engagement.

## Anti-Patterns

These are the specific things this protocol prevents:

| Anti-Pattern | What Happens | Rule That Prevents It |
|--------------|-------------|----------------------|
| **Info dump** | 2,000 words of findings with no structure | Chunking (Rule 1) + Lead with point (Rule 2) |
| **Decision pile-up** | "Here are 6 things I need you to decide" | Decision scaling (Rule 3) + Never stack |
| **Forced engagement when depleted** | Asking for detailed feedback at hour 3 | Fatigue awareness (Rule 4) |
| **Building to the conclusion** | Three paragraphs before the recommendation | Lead with point (Rule 2) |
| **Everything looks the same** | No visual hierarchy, no bolding, no breaks | Signaling (Rule 8) |
| **Implicit expectations** | Human can't tell if they need to respond | Name what you need (Rule 2) |
| **Layer mixing** | Summary section has 500 words of detail | Progressive disclosure (Rule 6) |
| **Context amnesia** | "As we discussed..." with no anchor | Context across sessions (Rule 7) |

## How Skills Should Use This

**Don't just footnote this protocol.** A single line at the bottom doesn't change behavior. Skills that need communication design should build the rules into their process:

- **Methodology skills** (engineering, slicing, investigating, systematic-debugging): Build chunking and decision scaling into each phase's checkpoint. Each checkpoint should follow one-topic-per-message and lead-with-the-point.
- **Orchestrator skills** (engineering, build): Apply progressive disclosure at transitions between sub-skills. Summarize what just happened before asking what's next.
- **Decision-heavy skills** (architecture, opportunity-research): Use decision scaling tables at every choice point. Never stack decisions.

**Utility skills** (commit-and-pr, verification, git-worktrees) don't need this — their output is short and procedural.

The skill-creator quality rubric scores communication design as part of the Structure dimension for user-facing skills.

## Adapting to Skill Duration

**Short skills (< 5 minutes):** Apply chunking and lead-with-the-point. Skip fatigue awareness.

**Medium skills (5-30 minutes):** Apply all rules. One retrieval prompt per major section. Check for fatigue signals after 3+ decision points.

**Long skills (30+ minutes):** Watch actively for fatigue. After detecting short/deferring responses, shift to higher-level summaries and make more low-stakes calls autonomously. Offer pause points.

## Calibration

These rules are starting points. If they don't work, adjust:

- If pairwise decisions feel too slow even for high stakes → batch 2-3 high-stakes decisions with clear framing
- If 3-4 item chunks feel too restrictive → test with 5, watch for comprehension drop-off
- If retrieval prompts feel like interruptions → reduce frequency or drop to only at major transitions
- If the human consistently wants more detail in Layer 1 → expand the brief, but keep Layer 2 as the deep dive

The human's feedback overrides the research. These are defaults, not laws.
