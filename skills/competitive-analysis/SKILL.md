---
name: competitive-analysis
description: Analyzes competitors and market position through structured data collection, feature/pricing comparison matrices, SWOT, positioning maps, and actionable strategic recommendations. Use this skill when the user asks to "analyze competitors", "do a competitive analysis", "compare us against X and Y", "build a competitor matrix", "find our market positioning", "size up the competition", "create a battlecard", or evaluate market gaps and differentiation opportunities.
license: MIT
---

# Competitive Analysis

## Overview

Keywords: competitive analysis, competitor research, market positioning, SWOT, feature comparison, pricing analysis, battlecard, differentiation, market gap, positioning map, win/loss, moat, go-to-market.

This skill turns scattered impressions about "the competition" into a rigorous, decision-grade analysis. It covers the full arc: define scope, identify the right competitors, collect structured evidence, build comparison matrices, derive positioning, and produce concrete recommendations (where to compete, how to differentiate, what to fix).

Use it for product strategy, sales enablement (battlecards), fundraising decks, market-entry decisions, and quarterly competitive reviews. The goal is always a defensible conclusion backed by a traceable evidence trail — not vibes.

Bundled resources:
- `references/frameworks.md` — Porter's Five Forces, SWOT, positioning maps, JTBD, value-curve, perceptual mapping, moat taxonomy, with when-to-use guidance.
- `references/data-sources.md` — where to find legitimate competitive intel, and the ethics/legal guardrails.
- `scripts/compare_matrix.py` — stdlib-only tool that ingests a competitor JSON/CSV and emits a weighted scored comparison matrix in Markdown.
- `templates/competitive-analysis-report.md` — fill-in report template.
- `templates/battlecard.md` — one-page sales battlecard template.
- `examples/saas-pm-tool-analysis.md` — a complete worked example.

## Workflow

Follow these steps in order. Do not skip scoping — most weak analyses fail because the question was never sharpened.

1. **Scope the question.** Pin down the decision the analysis must serve (e.g., "Should we move upmarket?", "What do we say when a prospect mentions Asana?"). Write a one-sentence objective and name the audience (product, sales, exec, investor). The objective dictates which framework and depth you use.

2. **Define the market and segment.** State the category, the buyer, the geography, and the job-to-be-done. Ambiguity here makes every comparison apples-to-oranges. Capture this as the "Market Definition" block.

3. **Identify competitors across three tiers.**
   - Direct: same solution, same buyer (head-to-head).
   - Indirect: different solution, same job (e.g., spreadsheets vs. a PM tool).
   - Aspirational/adjacent: where the category is moving, or who could enter.
   Aim for 3-6 named competitors plus the "do nothing / status quo" option, which is often the real competitor.

4. **Collect structured evidence.** For each competitor, fill the same fields (see `templates/competitive-analysis-report.md` and the dimension list below). Use only legitimate sources — see `references/data-sources.md`. Cite every non-obvious claim with a source and a date; intel decays fast. Flag estimates explicitly as `[est]`.

5. **Build the comparison matrix.** Choose the evaluation dimensions that matter to the buyer, assign weights summing to 100, and score each competitor 1-5 per dimension. Use `scripts/compare_matrix.py` to compute weighted totals deterministically and render the table. Never eyeball weighted scores by hand.

6. **Derive positioning.** Plot competitors on a 2x2 perceptual map using the two axes the buyer actually cares about (e.g., ease-of-use vs. power; price vs. breadth). Identify white space (unoccupied, valuable quadrants) and red oceans (crowded). See `references/frameworks.md`.

7. **Run SWOT and Five Forces** for the subject company against this landscape. Keep each cell to evidence-backed bullets, not adjectives.

8. **Synthesize recommendations.** Convert findings into 3-5 prioritized, specific actions with rationale and a rough effort/impact tag. Distinguish "defend" (table-stakes gaps to close) from "differentiate" (wedges to widen).

9. **Package for the audience.** Produce the report (`templates/competitive-analysis-report.md`) and, if sales is the audience, a battlecard per top competitor (`templates/battlecard.md`).

## Standard Comparison Dimensions

Pick the subset relevant to your buyer; do not pad the matrix.

- Core capabilities / feature coverage
- Pricing model and total cost of ownership
- Target segment & ideal customer profile (ICP)
- Ease of use / time-to-value
- Integrations & ecosystem
- Performance / scale / reliability
- Security, compliance, certifications
- Support & customer success
- Brand strength & market share
- Go-to-market motion (PLG, sales-led, channel)
- Customer sentiment (review scores, churn signals)
- Roadmap momentum & funding/runway

## Scoring & Weighting Framework

Score each dimension 1-5 from the **buyer's** perspective (not yours):

| Score | Meaning |
|-------|---------|
| 5 | Best-in-class; a reason to buy on its own |
| 4 | Strong; clearly above average |
| 3 | Adequate; meets table stakes |
| 2 | Weak; a noticeable gap |
| 1 | Absent or a dealbreaker |

Weights must sum to 100 and reflect what drives the purchase decision for your defined segment. A high weighted total in a low-weight dimension is noise; concentrate weight on the 3-4 dimensions that actually swing deals. Run `scripts/compare_matrix.py --help` for the input format.

## Worked Mini-Example

Objective: "As a mid-market SaaS PM tool, where can we differentiate vs. Asana, Monday, and Linear?"

1. Market: project/work management for 50-500 person software teams.
2. Tiers: Direct = Asana, Monday, Linear; Indirect = Jira, spreadsheets; Status quo = email + Slack.
3. Dimensions weighted: Ease-of-use (25), Dev workflow fit (25), Price (20), Integrations (15), Reporting (15).
4. Matrix (via script) shows Linear wins dev-fit, Monday wins ease, all weak on cross-team reporting.
5. Positioning map (dev-depth vs. cross-team breadth) reveals white space: "dev-grade speed with PM-grade reporting."
6. Recommendation: wedge on unified dev+exec reporting; defend on integrations (table stakes). See `examples/saas-pm-tool-analysis.md` for the full version.

## Best Practices

- **Start from the buyer's decision, not the feature list.** Buyers compare jobs-done and outcomes, not checkbox grids.
- **Cite and date everything.** A pricing claim without a date is a future error. Mark inferences `[est]`.
- **Compare on the same fields for everyone.** Asymmetric data hides bias and breaks the matrix.
- **Include the status quo / "do nothing."** It wins more deals than any named competitor.
- **Weight before you score.** Decide what matters, then rate — not the reverse.
- **Separate facts from interpretation.** Keep an evidence table; put opinions only in the synthesis.
- **Find white space, not just a ranking.** The output is "where to play," not "who's #1."
- **Refresh on a cadence.** Treat the analysis as a living doc; re-verify quarterly.

## Common Pitfalls

- **Cherry-picking dimensions** where you happen to win — produces a flattering but useless analysis.
- **Feature-counting bias:** more features ≠ better; bloat is often a weakness.
- **Stale data** presented as current; competitor pricing and positioning change monthly.
- **Ignoring indirect competitors** and the status quo, which capture most lost deals.
- **Vague SWOT** filled with adjectives ("innovative", "robust") instead of evidence.
- **No recommendation:** a matrix without "so what / now what" is a report, not an analysis.
- **Unethical collection:** posing as a customer to extract confidential info, scraping behind logins against ToS, or using a competitor's paid trial under false pretenses. See `references/data-sources.md` for the line.
- **Confirmation bias toward the home team:** score from the buyer's eyes; have someone red-team the result.
