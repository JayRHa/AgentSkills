# Worked Example: Checkout Conversion A/B Test

A complete walkthrough from hypothesis to decision.

## 1. Hypothesis
> Replacing the 2-step checkout with a 1-step checkout will increase completed-purchase rate by at least **+5% relative**, because it removes a drop-off point.

- Primary metric (OEC): completed-purchase rate among users who reach checkout.
- Guardrails: refund rate, page-load latency, average order value.
- Baseline (last 4 weeks): 10.0%.
- MDE: +5% relative -> 10.0% -> 10.5% (absolute +0.5pp).
- alpha 0.05, power 0.80, two-sided.

## 2. Sample size
```
python scripts/abtest.py size --baseline 0.10 --mde-rel 0.05 --daily-per-arm 4000
```
Output (abridged):
```
  baseline rate        : 10.0000%
  target rate          : 10.5000%
  MDE (absolute)       : +0.5000%
  alpha / power        : 0.05 / 0.8
  REQUIRED N per arm   : 57,962
  REQUIRED N total     : 115,924
  est. duration        : 15 days (round to 3 full week(s))
```
Decision: run for **3 full weeks** to reach N and cover seasonality.

## 3. Run untouched
No peeking-with-action for 3 weeks. Assignment is by user id (sticky).

## 4. SRM check (before looking at the result)
Observed arrivals: control 58,010, treatment 57,914; planned 50/50.
```
python scripts/abtest.py srm --observed 58010,57914 --split 0.5,0.5
```
```
  chi-square         : 0.0795 ...
  p-value            : 0.778...
  VERDICT            : no SRM detected; split looks healthy.
```
Good — the experiment is trustworthy. Proceed.

## 5. Significance test
Control converted 5,801 of 58,010; treatment 6,253 of 57,914.
```
python scripts/abtest.py prop --c-conv 5801 --c-n 58010 --t-conv 6253 --t-n 57914
```
```
  control            : 5,801/58,010 = 10.0000%
  treatment          : 6,253/57,914 = 10.7972%
  absolute lift      : +0.7972%
  relative lift      : +7.97%
  95% CI (absolute) : [+0.4399%, +1.1545%]
  z statistic        : 4.3735
  p-value (2-sided)  : 0.000012
  result             : SIGNIFICANT at alpha=0.05
```

## 6. Interpretation
- The effect is statistically significant (p ~ 0.00001).
- 95% CI on absolute lift: [+0.44pp, +1.15pp]. The **entire CI is above the +0.5pp MDE? No** — the lower bound (+0.44pp) is just under the +0.5pp MDE, but comfortably above 0 and the estimated lift (+0.80pp, +8% relative) exceeds the MDE.
- Guardrails checked: refund rate flat, latency flat, AOV flat. No regressions.
- Segment check (mobile vs desktop): both positive, no Simpson's reversal.
- Effect stable across weeks 1-3 (no novelty-only spike).

## 7. Decision
**Ship the 1-step checkout.** A real, ~+8% relative lift in completed purchases with a CI excluding zero, healthy SRM, no guardrail regressions, and consistent segment behavior.

## 8. One-line summary for stakeholders
> 1-step checkout increased completed-purchase rate by +0.80pp (10.0% -> 10.8%), 95% CI [+0.44pp, +1.15pp], p<0.0001, over 3 weeks / ~116k users, SRM clean, guardrails flat. Shipping.
