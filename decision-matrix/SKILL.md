---
name: decision-matrix
description: Builds a weighted decision matrix to compare options against criteria with transparent, reproducible scoring and sensitivity analysis. Use this skill when the user needs to choose between multiple options, compare alternatives, "help me decide", "which should I pick", weigh trade-offs, evaluate vendors/tools/candidates/houses/job offers, run a pros-and-cons or scoring analysis, rank choices objectively, or justify a recommendation with numbers. Triggers include "decision matrix", "weighted scoring", "compare these options", "pugh matrix", "trade study", and "how do I choose between X and Y".
license: MIT
---

# Decision Matrix

## Overview

A weighted decision matrix (a.k.a. weighted scoring model, Pugh matrix, or trade study)
turns a fuzzy "which should I pick?" question into a transparent, defensible number.
You list the **options** (the things you choose between), the **criteria** (what matters),
assign each criterion a **weight** (how much it matters), score every option on every
criterion, and compute a weighted total. The highest total is the recommended choice.

Keywords: decision making, weighted scoring, trade-off analysis, multi-criteria decision
analysis (MCDA), Pugh matrix, vendor selection, job offer comparison, prioritization.

Use this skill whenever someone must choose among 2+ discrete alternatives and wants the
reasoning to be explicit rather than a gut feel. Do **not** force a matrix on a binary
yes/no decision or a problem with a single dominant constraint — say so instead.

## Workflow

Follow these steps in order. Confirm with the user at steps 1–4 before computing.

1. **Frame the decision.** State the single question being answered (e.g. "Which CRM
   should we adopt?"). One decision per matrix. If the user has bundled several
   decisions, split them.

2. **List the options.** Gather 2–7 concrete alternatives. Fewer than 2 is not a
   decision; more than ~7 becomes noisy — shortlist first. Always consider adding a
   baseline "do nothing / status quo" option when relevant.

3. **Elicit the criteria.** Ask what factors matter. Aim for 4–8 criteria. Each must be:
   - **Distinct** (not measuring the same thing twice — avoid double-counting).
   - **Discriminating** (options actually differ on it; drop criteria where all score equally).
   - **Phrased so higher = better** (rename "Cost" → "Affordability", or mark it as a cost
     criterion to invert — see references/scoring-guide.md).

4. **Set weights.** Assign each criterion a weight reflecting its importance. Use any
   consistent scale (1–5, or percentages summing to 100). Normalize internally so totals
   are comparable. Capture **must-have constraints** separately as pass/fail gates, not
   weights — a dealbreaker should eliminate an option, not just dock points (see
   references/scoring-guide.md, "Constraints vs. criteria").

5. **Score each option × criterion.** Use a fixed scale (default 1–5; 1 = poor, 5 = excellent).
   Score one criterion across all options at a time (column-wise) to keep scoring calibrated.
   Note the rationale for extreme scores.

6. **Compute.** Weighted score = Σ(weight × score) per option, normalized to a 0–100 index.
   Use scripts/decision_matrix.py to do this reproducibly from a JSON or CSV file rather
   than doing arithmetic by hand.

7. **Sanity-check & sensitivity.** Ask: "Does the winner feel right?" If the top two are
   within ~5%, the decision is a near-tie — flag it and run sensitivity analysis (vary the
   most subjective weights/scores; see the script's `--sensitivity` flag). State which
   assumptions the result hinges on.

8. **Report.** Present the ranked table, the winner, the margin, the key drivers, and the
   risks/caveats. Use templates/report.md. Be explicit that the matrix informs the
   decision — it does not replace judgment.

## Scoring Scale (default)

| Score | Meaning            |
|------:|--------------------|
| 5     | Excellent / best in class |
| 4     | Good / above average |
| 3     | Adequate / acceptable |
| 2     | Weak / below average |
| 1     | Poor / unacceptable on this axis |

Keep the scale consistent across all criteria. For details on normalizing mixed units
(dollars, days, ratings) and handling cost-style criteria, see references/scoring-guide.md.

## Worked Example (abbreviated)

Choosing a project-management tool across Cost, Ease of use, Integrations, Support.

| Criterion     | Weight | Tool A | Tool B | Tool C |
|---------------|:------:|:------:|:------:|:------:|
| Affordability |   3    |   5    |   3    |   2    |
| Ease of use   |   5    |   3    |   5    |   4    |
| Integrations  |   4    |   3    |   4    |   5    |
| Support       |   2    |   4    |   3    |   5    |
| **Weighted**  |        | **47** | **52** | **52** |

Tool B and Tool C tie at 52. That is the signal to stop and look deeper: Tool C wins on
the highest-weight-adjacent criteria but loses on cost; Tool B is balanced. Run sensitivity
on the Ease-of-use weight. See examples/tool-selection.md for the full walkthrough,
including the JSON input and the script output.

## Best Practices

- **Weight before you score.** Set weights and criteria *before* seeing the options'
  scores, to avoid rationalizing a pre-chosen winner.
- **Score column-wise**, one criterion at a time across all options, for calibration.
- **Separate gates from scores.** Must-haves are pass/fail filters applied first.
- **Show your work.** Always surface the table and weights, never just the final number.
- **Treat near-ties as ties.** A 1-point gap on a subjective 1–5 scale is noise.
- **Run sensitivity on the squishy inputs** — the weights and scores you were least sure of.
- **Keep criteria independent** to avoid silently double-counting one concern.

## Common Pitfalls

- **Fudging weights to get the answer you wanted.** If you adjust inputs after seeing
  results, say so explicitly and re-justify.
- **Too many criteria.** Beyond ~8, low-weight noise drowns the signal. Consolidate.
- **Non-discriminating criteria.** If every option scores the same, the criterion adds
  nothing — drop it.
- **Mixing cost and benefit directions.** Forgetting to invert a "lower is better"
  criterion silently rewards the worst option. See references/scoring-guide.md.
- **False precision.** Reporting 73.42 implies accuracy the inputs don't have. Round and
  present margins, not decimals.
- **Ignoring dealbreakers.** A weighted average can let a strong option survive a fatal
  flaw. Apply hard constraints first.

## Supporting Files

- `references/scoring-guide.md` — scales, normalization of mixed units, cost vs. benefit
  criteria, weighting methods (direct, ranking, pairwise/AHP), and constraints vs. criteria.
- `scripts/decision_matrix.py` — stdlib Python tool. Computes weighted scores and rankings
  from JSON/CSV, prints a formatted table, supports cost criteria and `--sensitivity`.
- `examples/tool-selection.md` — full worked example with input file and script output.
- `templates/report.md` — fill-in template for presenting the decision and recommendation.
