# Scoring & Weighting Reference

Deep reference for building defensible decision matrices. Load this when you need to
normalize mixed units, handle cost criteria, choose a weighting method, or decide whether
something is a criterion or a hard constraint.

## 1. The core formula

For each option `o`:

```
weighted_total(o) = Σ_c  ( weight(c) × score(o, c) )
```

Where `c` ranges over criteria. To make totals comparable and intuitive, normalize:

```
index(o) = 100 × weighted_total(o) / (Σ_c weight(c) × max_score)
```

This yields a 0–100 index where 100 means an option scored the maximum on every criterion.

## 2. Scoring scales

Pick ONE scale and use it for every criterion.

| Scale | When to use |
|-------|-------------|
| 1–5   | Default. Good granularity, low fatigue. |
| 1–10  | When you need to express finer differences and have real data. |
| 0–4   | Pugh-style relative scoring vs. a baseline (−2..+2 also common). |

Default 1–5 anchors:

- **5** Excellent / best in class
- **4** Good / above average
- **3** Adequate / meets the bar
- **2** Weak / below average
- **1** Poor / barely acceptable

Reserve 1 and 5 for genuine extremes so the middle stays meaningful.

## 3. Cost (lower-is-better) criteria

Many real criteria are "lower is better": price, latency, risk, lead time. Two clean ways
to handle them:

**A. Rename to a benefit.** "Cost" → "Affordability". Then score normally (cheapest = 5).
Simple and readable. Preferred for qualitative scoring.

**B. Mark as a cost criterion and invert.** Keep raw numbers, then invert during scoring:

```
score = (max_raw − raw) / (max_raw − min_raw) × (scale_max − 1) + 1
```

The `decision_matrix.py` script supports this via `"direction": "cost"` on a criterion.
Never leave a cost criterion un-inverted — it silently rewards the worst option.

## 4. Normalizing mixed units

When scores come from real measurements in different units (dollars, GB, days, star
ratings), map each criterion's raw values onto the common scale before weighting.

**Min–max normalization (benefit direction):**

```
score = (raw − min) / (max − min) × (scale_max − scale_min) + scale_min
```

**For cost direction**, swap so the minimum raw value gets `scale_max`.

Guidance:
- Normalize **within a criterion** (per column), never across criteria.
- If one option is a wild outlier, consider capping/winsorizing before normalizing, or it
  will compress everyone else into a narrow band.
- Document the min/max you used so the scoring is reproducible.

## 5. Weighting methods

| Method | How | Best for |
|--------|-----|----------|
| **Direct rating** | Assign each criterion a weight on a fixed scale (1–5) or a % that sums to 100. | Fast, most decisions. |
| **Rank then convert** | Rank criteria 1..n by importance, then use rank-sum or rank-reciprocal weights. | When absolute weights are hard but ordering is clear. |
| **Pairwise (AHP-lite)** | Compare each pair: which matters more and by how much (1–9). Derive weights from the comparison matrix. | High-stakes, group decisions needing rigor and a consistency check. |

**Rank-sum weights** for n criteria, criterion at rank r (1 = most important):
```
weight(r) = (n − r + 1) / Σ(1..n)
```

**AHP consistency:** when using pairwise comparisons, check the Consistency Ratio (CR). A
CR > 0.10 means your judgments contradict each other — revisit the comparisons.

Always **normalize weights** (divide by their sum) before reporting, so a weight reads as
"share of the decision."

## 6. Constraints vs. criteria — the most important distinction

- A **criterion** is something you trade off: more is better, less is worse, on a gradient.
- A **constraint** is a hard gate: a minimum/maximum that, if violated, eliminates the
  option entirely regardless of how good it is elsewhere.

Examples of constraints: "must be SOC 2 compliant", "budget ceiling $50k", "must run
on-prem", "start date before Q3".

**Process:** apply constraints FIRST as pass/fail filters. Only options that pass all gates
enter the weighted matrix. This prevents a strong-but-fatally-flawed option from winning on
average. Never model a dealbreaker as merely a low score — a 1 still contributes points.

## 7. Sensitivity analysis

The matrix output is only as trustworthy as its squishiest inputs. After computing:

1. Identify the 1–3 weights/scores you were least confident about.
2. Perturb each (±1 score point, or ±25% weight) and recompute.
3. If the winner is stable across perturbations → robust decision, recommend confidently.
4. If the winner flips → the decision hinges on that assumption. Surface it; gather more
   data on that specific input rather than trusting the matrix.

A result that flips under small, reasonable perturbations is a **near-tie** dressed up as a
winner. Treat top options within ~5 index points as effectively tied.

## 8. Group decisions

- Have each stakeholder weight independently, then average (or discuss divergences — the
  disagreement itself is signal).
- Scores should be calibrated together or by the person closest to the data.
- Record dissent. A 6–1 vote and a 4–3 vote have very different durability.
