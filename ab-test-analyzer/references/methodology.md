# A/B Testing Methodology Reference

Deep reference for the statistical and design decisions behind a sound experiment. Load this when planning a non-trivial test or reviewing someone else's design.

## 1. Hypothesis and the OEC
A good hypothesis is falsifiable and mechanistic:

> "Replacing the two-step checkout with a one-step checkout will increase **completed-purchase rate** by at least **2% relative**, because it removes a drop-off point."

The **Overall Evaluation Criterion (OEC)** is the single primary metric the decision hinges on. Properties of a good OEC:
- **Directly tied to the business goal** (e.g. revenue per user, retention) rather than a vanity proxy (e.g. clicks).
- **Sensitive** — moves when the product genuinely improves.
- **Hard to game** — improving it can't trivially hurt the real goal.
- **Measurable within the test window.**

Everything else falls into two buckets:
- **Guardrail metrics** — must NOT regress (latency, error rate, unsubscribe rate, revenue). Watched but not the decision driver.
- **Exploratory metrics** — for hypothesis generation only; never used to declare a win without a follow-up confirmatory test.

## 2. Errors, alpha, beta, power
| | Null true (no effect) | Null false (real effect) |
|---|---|---|
| Declare significant | Type I error (alpha) | Correct (power = 1-beta) |
| Declare not significant | Correct | Type II error (beta) |

- alpha = tolerated false-positive rate. Convention 0.05.
- power = probability of detecting a true effect of size = MDE. Convention 0.80; use 0.90 for high-stakes ships.
- There is a direct trade-off: smaller MDE, smaller alpha, or higher power all require larger samples.

## 3. Minimum Detectable Effect (MDE)
The MDE is a **design input, not a result**. It is the smallest effect that is worth the cost of shipping. Set it from business value, not from what you hope to see.
- Relative MDE: percentage change of the baseline (e.g. +5%).
- Absolute MDE: percentage-point change (e.g. +0.5pp on a 10% baseline = relative +5%).

Smaller MDE -> much larger sample (N scales ~ 1/MDE^2). Halving the MDE roughly quadruples the required sample.

## 4. Sample size formula (two proportions, equal allocation)
Per arm:

```
n = ( z_{1-alpha/2} * sqrt(2 * p_bar * (1-p_bar)) + z_{1-beta} * sqrt(p1*(1-p1) + p2*(1-p2)) )^2 / (p2 - p1)^2
```

where `p_bar = (p1+p2)/2`. The script implements exactly this. For means, replace the variance terms with the pooled standard deviation and use the standardized effect (Cohen's d).

## 5. Test duration
1. Compute required N per arm.
2. duration_days = N_per_arm / (daily eligible users per arm).
3. Round UP to whole weeks (min 1, prefer 2) to average over day-of-week effects and let novelty effects settle.
4. Cap total runtime (e.g. 4-6 weeks) — cookie churn and external changes erode validity in very long tests.

## 6. Choosing the test
- **Binary outcome, 2 arms:** two-proportion z-test (large N) or Fisher's exact (tiny N).
- **Continuous outcome, 2 arms:** Welch's t-test (does NOT assume equal variances — preferred default).
- **>2 arms, rates:** chi-square omnibus, then pairwise comparisons with correction.
- **>2 arms, means:** one-way ANOVA, then post-hoc (Tukey).
- **Skewed continuous (revenue):** consider the t-test (robust at large N by CLT), capping/winsorizing outliers, or a bootstrap.
- **Ratio metrics where the unit != randomization unit** (e.g. clicks-per-session randomized by user): use the **delta method** or bootstrap for correct variance — naive t-tests understate variance.

## 7. Multiple comparisons
Testing many metrics or variants inflates the family-wise false-positive rate. With m independent tests at alpha=0.05, P(at least one false positive) = 1 - 0.95^m (m=10 -> ~40%).

Corrections:
- **Bonferroni:** use alpha/m per test. Simple, conservative. Good for a handful of pre-specified comparisons.
- **Benjamini-Hochberg (FDR):** sort p-values ascending p(1)..p(m); find the largest k with p(k) <= (k/m)*alpha; reject all up to k. Controls the *expected proportion* of false discoveries — better power for many metrics.

The primary OEC is usually exempt (one pre-registered decision); corrections apply to the secondary/exploratory family.

## 8. Sequential testing / peeking
Fixed-horizon tests are only valid if you decide at the pre-set N. If you must monitor and stop early, use a method designed for it:
- **Group sequential** (O'Brien-Fleming, Pocock alpha-spending) — pre-allocate alpha across interim looks.
- **Always-valid p-values / mSPRT** (used by many experimentation platforms) — valid at every peek.
- **Bayesian** with a pre-committed decision rule and stopping criterion.
Never combine ad-hoc daily peeking with a fixed-horizon test.

## 9. Bayesian alternative (brief)
Instead of a p-value, model the posterior of each arm's rate (e.g. Beta-Binomial with a Beta prior) and report:
- P(treatment > control), and
- the posterior distribution of the lift / expected loss of choosing wrong.
Bayesian results are still vulnerable to optional stopping unless the decision rule (e.g. expected-loss threshold) is pre-committed. It is not a free pass to peek.

## 10. Validity threats checklist
- **SRM:** observed split != planned split (chi-square p<0.001) => bug; discard.
- **Simpson's paradox:** aggregate direction reverses within segments due to mix shifts.
- **Novelty / primacy:** behavior changes as users habituate; run long enough.
- **Interference / network effects:** treatment leaks to control (marketplaces, social) -> use cluster randomization.
- **Carryover:** in switchback/sequential designs, prior period affects current.
- **Survivorship / attrition:** differential dropout between arms biases comparison.
