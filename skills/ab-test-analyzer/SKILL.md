---
name: ab-test-analyzer
description: Designs and analyzes A/B tests end-to-end — frames a sharp hypothesis, computes required sample size and test duration, runs significance tests (two-proportion z-test, Welch's t-test, chi-square), reports confidence intervals and lift, and flags common pitfalls like peeking, multiple comparisons, and Simpson's paradox. Use this skill when the user mentions A/B testing, split testing, experiment design, conversion-rate experiments, statistical significance, p-values, sample size or power calculations, "did this experiment win", minimum detectable effect (MDE), or asks to interpret experiment results honestly. Includes a runnable stats script (scripts/abtest.py).
license: MIT
---

# A/B Test Analyzer

## Overview
This skill helps design and analyze controlled online experiments (A/B and A/B/n tests) with statistical rigor and honest interpretation. It covers the full lifecycle: hypothesis framing, sample-size and duration planning, choosing the right test, computing p-values and confidence intervals, and avoiding the traps that produce false wins.

Keywords: A/B test, split test, experiment, hypothesis, sample size, power, MDE, minimum detectable effect, statistical significance, p-value, confidence interval, conversion rate, lift, two-proportion z-test, t-test, chi-square, peeking, multiple comparisons, Simpson's paradox, SRM, novelty effect.

Use this skill whenever someone wants to plan an experiment, decide if a result is real, or sanity-check an analysis someone else did.

## Core Mental Model
- An A/B test estimates a **causal effect** by randomizing units (usually users) into control and treatment.
- You are testing a **null hypothesis** (no difference) against an **alternative** (there is a difference). A p-value is `P(data this extreme or more | null is true)` — NOT the probability the null is true, and NOT the probability your variant is better.
- Two error types: **Type I** (false positive, rate = alpha, typically 0.05) and **Type II** (false negative, rate = beta; **power** = 1 - beta, typically 0.80).
- **You must fix sample size and test duration BEFORE you start.** Stopping when significant ("peeking") inflates the false-positive rate dramatically.

## Workflow
Follow these steps in order. Do not skip planning steps even when only asked to "analyze results" — verify the plan was sound first.

1. **Frame the hypothesis.** Turn the vague goal into a falsifiable statement: "Changing X will increase metric M from baseline b by at least the MDE, because [mechanism]." Identify ONE primary metric (the Overall Evaluation Criterion / OEC). Pre-register guardrail metrics. See `references/methodology.md` for OEC selection.

2. **Pick the metric type.**
   - Binary / rate (conversion, click, signup) → two-proportion test.
   - Continuous (revenue per user, time on page, order value) → Welch's t-test (means).
   - More than 2 variants → chi-square (rates) or ANOVA-style + correction.

3. **Set the design parameters.**
   - Baseline rate or baseline mean (`b`).
   - Minimum Detectable Effect (MDE): the smallest lift worth detecting. Express relative (e.g. +5%) and convert to absolute.
   - alpha (default 0.05), power (default 0.80), one- vs two-sided (almost always two-sided).

4. **Compute required sample size and duration.** Run `scripts/abtest.py size`. Divide required N per arm by daily eligible traffic per arm to get duration in days. Round duration UP to full weeks to cover weekday/weekend seasonality (min 1 week, ideally 2).

5. **Run the test untouched** for the full pre-planned duration. No peeking-with-action. (You may monitor guardrails for catastrophic harm only.)

6. **Validate data quality BEFORE looking at the result.**
   - Sample Ratio Mismatch (SRM): is the actual split close to the planned split? Run `scripts/abtest.py srm`. If p < 0.001, the experiment is broken — do NOT trust the result.
   - Check for logging bugs, bot traffic, and that randomization was at the right unit.

7. **Run the significance test.** Use `scripts/abtest.py prop` (rates) or `scripts/abtest.py ttest` (means). Report: effect size (absolute + relative lift), confidence interval, p-value, and whether it crossed alpha.

8. **Interpret honestly.** A non-significant result is NOT proof of no effect — report the CI to show what effects are still plausible. A significant result with a CI that includes trivially small lifts may not be worth shipping. See `references/interpretation-guide.md`.

9. **Account for multiplicity.** If you tested multiple metrics or variants, apply a correction (Bonferroni or Benjamini-Hochberg). See `references/methodology.md`.

10. **Write it up.** Use `templates/experiment-report.md` so decisions are reproducible and reviewable.

## Choosing the Test (decision table)
| Metric | Variants | Test | Script command |
|---|---|---|---|
| Rate / proportion | 2 | Two-proportion z-test | `abtest.py prop` |
| Rate / proportion | >2 | Chi-square (then pairwise + correction) | `abtest.py chisq` |
| Continuous mean | 2 | Welch's t-test | `abtest.py ttest` |
| Continuous mean | >2 | ANOVA + post-hoc (use a stats lib) | external |
| Any | — | Sample size planning | `abtest.py size` |
| Any | — | SRM / sanity check | `abtest.py srm` |

## Quick Worked Example
Baseline conversion 10%, want to detect a relative +5% (→ 10.5% absolute), alpha 0.05, power 0.80, two-sided:

```
python scripts/abtest.py size --baseline 0.10 --mde-rel 0.05 --alpha 0.05 --power 0.80
```
→ ~ 58,000 users per arm. At 4,000 eligible users/arm/day → ~15 days → round to 2 full weeks.

After the test, control 5,800/58,000 = 10.00%, treatment 6,150/58,000 = 10.60%:
```
python scripts/abtest.py prop --c-conv 5800 --c-n 58000 --t-conv 6150 --t-n 58000
```
→ absolute lift +0.60pp, relative +6.0%, 95% CI on absolute difference, and a p-value. Decide using the CI, not just the p-value. See `examples/conversion-test.md` for the full walkthrough.

## Best Practices
- Pre-register: hypothesis, primary metric, MDE, sample size, duration, and the decision rule BEFORE launch.
- Randomize at the right unit (usually user, not session/pageview) and keep it consistent across the funnel.
- Run for whole weeks; account for day-of-week and novelty effects.
- Report effect size + confidence interval first; treat the p-value as secondary.
- Use one primary OEC; everything else is a guardrail or exploratory.
- Always run an SRM check before trusting any result.
- Prefer two-sided tests; one-sided needs strong justification.

## Common Pitfalls
- **Peeking / optional stopping:** checking daily and stopping at first significance turns a 5% false-positive rate into 20-30%+. Fix sample size up front, or use a proper sequential/Bayesian method.
- **p-hacking / metric shopping:** testing 20 metrics and reporting the one with p<0.05. Correct for multiplicity.
- **Simpson's paradox:** an aggregate winner can lose in every segment if traffic mix differs. Check key segments; beware mixing pre/post populations.
- **Sample Ratio Mismatch:** a broken split (e.g. 52/48 instead of 50/50) signals a bug that biases everything.
- **Confusing significance with importance:** with huge N, trivially small lifts become "significant." Use the MDE and the CI.
- **Confusing non-significance with "no effect":** underpowered tests fail to detect real effects. Report the CI.
- **Novelty/primacy effects:** early behavior differs from steady state; don't conclude from day 1-2.
- **Multiple comparisons across variants:** A/B/C/D testing without correction inflates false positives.

See `references/pitfalls-checklist.md` for a pre-launch and pre-decision checklist to run every time.

## Bundled Files
- `scripts/abtest.py` — runnable, stdlib-only calculator: sample size, two-proportion z-test, Welch's t-test, chi-square, SRM. Run `python scripts/abtest.py --help`.
- `references/methodology.md` — deep dive on hypotheses, OEC, power, MDE, multiplicity corrections, sequential testing, Bayesian alternative.
- `references/interpretation-guide.md` — how to read p-values, CIs, and what each outcome (sig/non-sig × big/small effect) actually means for a ship decision.
- `references/pitfalls-checklist.md` — copy-paste checklist for design and analysis review.
- `templates/experiment-report.md` — fill-in template for documenting an experiment.
- `examples/conversion-test.md` — a complete end-to-end worked example.
