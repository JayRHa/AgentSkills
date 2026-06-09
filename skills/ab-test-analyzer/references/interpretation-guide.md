# Honest Interpretation Guide

How to read results without fooling yourself or your stakeholders. Load when writing up or reviewing a conclusion.

## What a p-value IS and IS NOT
- IS: `P(observing data at least this extreme | the null hypothesis is true)`.
- IS NOT: the probability the null is true.
- IS NOT: the probability your variant is better.
- IS NOT: a measure of effect size. A tiny, useless effect can have a tiny p-value at large N.
- p = 0.06 does not mean "no effect"; p = 0.04 does not mean "big effect". The threshold is a convention, not a law of nature.

## Lead with the confidence interval
The 95% CI is the range of effects compatible with the data. Always report it and reason from it:
- CI entirely above 0 and above the MDE -> strong, ship-worthy win.
- CI entirely above 0 but includes trivially small values -> statistically real, maybe not worth shipping.
- CI straddles 0 -> inconclusive; report the range of still-plausible effects.
- Narrow CI around 0 -> good evidence the effect (if any) is small; a meaningful "flat" result.
- Wide CI around 0 -> underpowered; you learned little. Do NOT claim "no effect."

## The 2x2 of outcomes (effect size x significance)
| | Statistically significant | Not significant |
|---|---|---|
| **Large estimated effect** | Likely a real, valuable win. Verify SRM + segments, then ship. | Underpowered: a real effect may be hiding. Report wide CI; consider more data. |
| **Small estimated effect** | Real but possibly trivial. Compare CI to MDE / shipping cost. | Good evidence of little-to-no meaningful effect (if CI is tight). A useful negative result. |

## Decision rule (pre-commit before the test)
A clean rule, decided up front:
1. SRM check passes (p >= 0.001). If not, discard and debug.
2. Primary OEC: ship iff lower bound of the CI > 0 (or > a pre-set practical threshold) at alpha.
3. No guardrail metric regresses beyond its tolerance.
4. If inconclusive: do not ship; either extend (only if pre-planned for sequential) or iterate.

## Things that quietly invalidate a "win"
- You peeked daily and stopped when it hit p<0.05.
- You tested 12 metrics and reported the 1 that was significant.
- The split was 51/49 (SRM) -> assignment bug.
- The win exists only in aggregate and reverses in every segment (Simpson's).
- The win was driven by days 1-2 novelty and faded.
- A few outlier whales drove a revenue "win" (check the median / cap outliers).

## Communicating to stakeholders
State, in this order:
1. Decision (ship / don't ship / iterate) and the metric it rests on.
2. Effect size with CI in plain units ("+0.6pp conversion, 95% CI [+0.2pp, +1.0pp]").
3. Confidence basis (p-value, sample size, duration, SRM pass).
4. Caveats (segments, guardrails, assumptions).
Avoid "proven", "100% sure", or quoting the p-value as the chance of being right.
