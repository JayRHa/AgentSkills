---
name: swot-analyzer
description: Produces a rigorous SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for a company, product, team, project, or personal decision, then converts the four quadrants into prioritized, concrete strategic actions using a TOWS cross-matrix. Use this skill when the user asks for a "SWOT analysis", "SWOT", "strengths and weaknesses", "competitive analysis", "strategic assessment", "situation analysis", "should we launch/enter/pivot", or wants help turning a SWOT into an action plan, strategy, or roadmap.
license: MIT
---

# SWOT Analyzer

## Overview

This skill builds a high-quality SWOT analysis and — critically — does not stop at four lists. It drives the analysis through to **decisions and actions** using the TOWS matrix (pairing internal factors with external factors to generate strategies).

Keywords: SWOT, TOWS, strengths, weaknesses, opportunities, threats, strategic planning, competitive analysis, situation analysis, go/no-go, market entry, business strategy.

Use this skill whenever the user wants to evaluate a situation, position, or decision and translate that evaluation into a plan.

Core principle: **Strengths and Weaknesses are INTERNAL and present-tense** (under the subject's control: people, capabilities, IP, costs, brand). **Opportunities and Threats are EXTERNAL and future-leaning** (outside control: market, competitors, regulation, technology, economy). Mixing these up is the single most common SWOT failure.

## Workflow

Follow these steps in order. Do not skip the scoping or the TOWS step.

1. **Scope the subject.** Confirm WHO/WHAT is being analyzed (company, product, team, initiative, person) and the DECISION or GOAL it serves (e.g., "decide whether to enter the EU market"). A SWOT with no decision attached is just a list. If the user did not state a goal, ask one short clarifying question or state an assumed goal explicitly.

2. **Gather evidence.** Pull facts: financials, market data, customer feedback, competitor moves, internal capabilities. Prefer specific, evidenced claims over vague adjectives. If information is missing, mark it as an assumption.

3. **Populate the four quadrants.** For each quadrant, generate factors using the prompts in `references/prompts.md`. Apply the internal/external and present/future tests. Aim for 4-8 high-signal items per quadrant, not 20 weak ones.

4. **Make each factor concrete.** Quantify where possible ("churn at 7% monthly", not "retention issues"). Attribute strengths/weaknesses to a cause. Tie opportunities/threats to a trend with a rough magnitude and time horizon.

5. **Prioritize within each quadrant.** Score each factor on Impact (1-5) and Confidence/Likelihood (1-5). Rank by Impact x Confidence. Keep the top items prominent.

6. **Run the TOWS cross-matrix.** This is where strategy emerges. Pair quadrants to produce four strategy types (see Decision Framework below and `references/tows-matrix.md`).

7. **Convert to actions.** Turn the top strategies into concrete, owned, time-bound actions. Each action: what, why (which SWOT pairing), owner, horizon (now / 90 days / 12 months), and a success metric.

8. **Summarize the strategic posture.** State whether the overall position favors aggressive growth, defensive consolidation, turnaround, or careful selectivity, based on where the weight sits across quadrants.

9. **Deliver** using `templates/swot-report.md`. Optionally run `scripts/swot_score.py` to compute priority rankings and a posture indicator from a simple JSON input.

## Decision Framework — TOWS Cross-Matrix

The TOWS matrix is the engine that turns analysis into strategy. Pair internal with external:

| Pairing | Strategy type | Question it answers |
|---|---|---|
| **S + O** (Strengths–Opportunities) | **Attack / Maxi-Maxi** | How do we use our strengths to seize opportunities? (most aggressive growth bets) |
| **S + T** (Strengths–Threats) | **Defend / Maxi-Mini** | How do we use strengths to neutralize threats? (moats, hedges) |
| **W + O** (Weaknesses–Opportunities) | **Improve / Mini-Maxi** | How do we fix weaknesses to capture opportunities? (build, hire, partner) |
| **W + T** (Weaknesses–Threats) | **Survive / Mini-Mini** | How do we minimize weaknesses to avoid threats? (exit, retrench, de-risk) |

Generate at least one strategy per cell when the factors support it. The strongest strategies usually come from S+O (offense) and W+T (the existential risks).

### Posture heuristic
- Weight concentrated in **S and O** → **Aggressive** growth posture.
- Weight in **S and T** → **Defensive** posture; protect the core.
- Weight in **W and O** → **Turnaround / build** posture; invest to qualify.
- Weight in **W and T** → **Defensive / survival** posture; cut risk, consider exit.

## Quality Checklist

Before delivering, verify against `references/checklist.md`. Highlights:
- Every S/W is internal and present; every O/T is external and trend-based.
- No factor is a vague adjective ("good team") — each is specific and, where possible, quantified.
- Opportunities are not just "do good things"; they are external openings the subject could exploit.
- Threats are not internal weaknesses in disguise.
- The TOWS matrix produced real strategies, and the top strategies became dated, owned actions with metrics.
- The output ends with a clear recommended posture and the single most important next move.

## Best Practices

- **Anchor to a decision.** Always state the goal the SWOT serves. The same subject yields a different SWOT for "raise funding" vs. "cut costs".
- **Few strong items beat many weak ones.** Cap each quadrant at ~8 and rank.
- **Quantify relentlessly.** Numbers turn opinions into evidence.
- **Separate fact from assumption.** Tag unknowns; they often become the first research actions.
- **Make opportunities and threats symmetric.** A trend is usually both an opportunity (for the prepared) and a threat (for the unprepared) — note both sides.
- **Finish with TOWS.** A SWOT that stops at four lists has done half the job.

## Common Pitfalls

- **Quadrant confusion:** putting a weakness ("we lack a mobile app") into Threats, or an external trend into Strengths. Apply the internal/external test every time.
- **Laundry lists:** 20 unranked items with no impact assessment. Prioritize.
- **Vagueness:** "strong brand", "good people" — meaningless without evidence.
- **Opportunities = wishes:** "grow revenue" is a goal, not an external opportunity. The opportunity is the external change (e.g., "incumbent exiting the SMB segment").
- **No follow-through:** four lists and no strategy or actions.
- **Static snapshot:** ignoring time horizons. Tag O/T with when they bite.

## Supporting Files

- `references/prompts.md` — generative prompts per quadrant to surface non-obvious factors.
- `references/tows-matrix.md` — deep guide to the TOWS cross-matrix with worked strategy examples.
- `references/checklist.md` — the full pre-delivery quality checklist.
- `templates/swot-report.md` — the deliverable template (SWOT grid + TOWS + action plan).
- `examples/saas-startup.md` — a complete worked example end to end.
- `scripts/swot_score.py` — stdlib Python tool that ranks factors and computes strategic posture from JSON.
