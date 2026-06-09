# Experiment Report: <experiment name>

**Owner:** <name>  
**Status:** Planned | Running | Concluded  
**Dates:** <start> -> <end> (<N> days / <W> weeks)  
**Link:** <dashboard / ticket>

## 1. Hypothesis
> Changing <X> will <increase/decrease> <primary metric> by at least <MDE> because <mechanism>.

## 2. Design
| Field | Value |
|---|---|
| Primary metric (OEC) | |
| Metric type | rate / continuous |
| Baseline | |
| MDE (relative / absolute) | |
| alpha / power | 0.05 / 0.80 |
| Sided | two-sided |
| Required N per arm | |
| Planned duration | |
| Randomization unit | user / ... |
| Allocation | 50/50 |
| Variants | A (control), B (treatment) |
| Guardrail metrics + tolerances | |
| Decision rule (pre-registered) | ship iff CI lower bound > 0 and no guardrail regresses |
| Stopping policy | fixed-horizon (no peeking) / sequential |
| Multiplicity plan | n/a / Bonferroni / Benjamini-Hochberg |

## 3. Data Quality
- [ ] Ran full planned duration / sample size
- [ ] SRM check: observed split <...> vs planned <...>, p = <...>  -> PASS / FAIL
- [ ] No logging/bot/outlier anomalies

## 4. Results
| Metric | Control | Treatment | Abs. diff | Rel. lift | 95% CI | p-value |
|---|---|---|---|---|---|---|
| <OEC> | | | | | | |
| <guardrail 1> | | | | | | |

Command(s) used:
```
python scripts/abtest.py <cmd> <args>
```

## 5. Segments / Robustness
- Segment A: <result>
- Segment B: <result>
- Simpson's paradox check: <pass/fail>
- Novelty/stability over time: <stable / faded>

## 6. Interpretation
<Read from the CI first. Significant? Effect vs MDE? Practical value?>

## 7. Decision
**<Ship / Don't ship / Iterate>** because <reason grounded in CI + guardrails>.

## 8. One-line summary
> <metric> moved <effect> (<CI>), p=<...>, over <duration>/<N> users, SRM <status>, guardrails <status>. <Decision>.

## 9. Follow-ups
- <next experiment / monitoring / rollout plan>
