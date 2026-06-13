# Key Result Formulas

A **Key Result** is quantitative, has a baseline and a target, and measures an **outcome**. It is graded 0.0-1.0 at period end.

## The Formula

> **{verb} {metric} from {baseline} to {target} by {deadline}.**

Every part matters:
- **verb** — direction of change (Increase, Reduce, Grow, Cut, Raise, Lower, Reach, Sustain).
- **metric** — the measurable quantity, defined unambiguously (include the unit and the segment).
- **baseline** — where it is today. Without this the KR is unscoreable.
- **target** — where it should be at period end.
- **deadline** — within the OKR period.

## Metric Types

| Type | Pattern | Example |
|------|---------|---------|
| Growth | from X to Y | ARR from $4.2M to $5.0M |
| Reduction | from X to Y (lower is better) | Churn from 4.1% to 2.5% |
| Ratio / rate | % of population | Activation from 38% to 55% |
| Threshold | reach / stay above-below | Keep p95 latency under 200ms |
| Count to target | reach N | Reach 50 enterprise logos |
| Milestone (binary) | achieve / certify | Achieve SOC 2 Type II (use sparingly) |

## Counter-Balancing Key Results

For almost any headline metric, a team can win the number while degrading something else. Add a **quality / guardrail KR** to prevent gaming.

| Headline KR | Risk | Counter-balance KR |
|-------------|------|--------------------|
| Increase shipping velocity | Bugs spike | Keep change-failure rate under 10% |
| Grow signups | Junk users | Keep day-7 activation above 40% |
| Cut support response time | Quality drops | Keep CSAT above 90% |
| Increase sales bookings | Bad-fit deals churn | Keep 90-day logo retention above 95% |
| Reduce infra cost | Reliability suffers | Sustain 99.9% uptime |

At least one KR per objective should be a counter-balance or quality measure when the others are pure growth/speed metrics.

## Verb Bank

- Up: Increase, Grow, Raise, Lift, Expand, Reach, Drive, Boost.
- Down: Reduce, Cut, Lower, Decrease, Shrink, Eliminate.
- Hold: Sustain, Maintain, Keep above/below.

## Quality Checklist for One KR

- [ ] Has a number (not done/not-done, unless an approved milestone).
- [ ] Has a baseline.
- [ ] Has a target.
- [ ] Has a deadline inside the period.
- [ ] Measures an outcome, not an activity.
- [ ] Is not a vanity metric (ties to real value).
- [ ] Defines the metric precisely (unit + segment + source).
- [ ] Owner can influence it within the period.

## Confidence & Ambition

- **Committed KR:** expected to reach 1.0 (100%). Used for must-deliver work.
- **Aspirational / stretch KR:** target set so that ~0.7 is a great result. If you regularly score 1.0 on stretch KRs, you are sandbagging.
- State the type and a starting confidence (e.g., "5/10 confidence") next to each.

## Grading (period end)

- 1.0 = target fully met or exceeded.
- 0.7 = solid progress, typical "good" stretch result.
- 0.3 = made a real dent.
- 0.0 = no meaningful progress.
Compute score = (actual - baseline) / (target - baseline), clamped to [0, 1].
