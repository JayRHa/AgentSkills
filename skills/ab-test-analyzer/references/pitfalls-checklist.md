# A/B Test Checklist (Design + Analysis)

Run this checklist twice: once before launch, once before declaring a result. Copy it into the experiment doc.

## Pre-launch (design)
- [ ] Hypothesis is written, falsifiable, and states a mechanism.
- [ ] Exactly ONE primary metric (OEC) chosen and tied to a business goal.
- [ ] Guardrail metrics listed with regression tolerances.
- [ ] Baseline rate/mean measured from recent real data.
- [ ] MDE set from business value (not from hope).
- [ ] alpha, power, and one/two-sided decided (default 0.05 / 0.80 / two-sided).
- [ ] Required sample size computed (scripts/abtest.py size).
- [ ] Duration = N / daily traffic, rounded up to whole weeks (>= 1, prefer 2).
- [ ] Randomization unit chosen (usually user) and consistent across the funnel.
- [ ] Assignment is deterministic + sticky (same user always same arm).
- [ ] Decision rule pre-registered (ship/iterate conditions).
- [ ] Stopping policy decided: fixed-horizon (no peeking) or a sequential method.
- [ ] Multiplicity plan if testing many metrics/variants (Bonferroni / BH).
- [ ] Instrumentation validated in a dry run (events fire, dedup works).

## During
- [ ] No action taken on early significance (unless using a valid sequential design).
- [ ] Only catastrophic-harm guardrails monitored for emergency stop.
- [ ] No mid-test changes to variant, traffic allocation, or targeting.

## Pre-decision (analysis)
- [ ] Ran for the full pre-planned duration / sample size.
- [ ] SRM check passed (scripts/abtest.py srm; p >= 0.001).
- [ ] No data-quality red flags (bots, double-counting, missing events, outliers).
- [ ] Correct test used for the metric type (prop / ttest / chisq).
- [ ] Effect size + confidence interval reported (not just p-value).
- [ ] Compared CI lower bound against MDE / practical threshold.
- [ ] Guardrail metrics checked for regressions.
- [ ] Key segments checked for Simpson's paradox / heterogeneous effects.
- [ ] Novelty effect ruled out (effect stable over the run, not just early).
- [ ] Multiplicity correction applied if multiple metrics/variants tested.
- [ ] Conclusion stated honestly (no "proven", no p-value-as-probability-of-truth).
- [ ] Report written from templates/experiment-report.md.

## Red flags that should STOP a ship decision
- SRM detected (broken assignment).
- Result only appears after peeking-driven early stop.
- Win reverses in major segments.
- Win driven by a handful of outliers.
- A guardrail regressed beyond tolerance.
- The CI includes effects too small to justify the change.
