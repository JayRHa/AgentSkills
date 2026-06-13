# Writing & Ranking Hypotheses

A hypothesis is only useful if it is **falsifiable** and **discriminating**.

## What makes a good hypothesis
- **Falsifiable**: predicts a concrete observation that could prove it wrong.
  - Bad: "Something's wrong with the cache." (untestable, vague)
  - Good: "On a cache miss, `get_user()` returns `None` and the caller dereferences it." (predicts: log a miss → see None → see the crash)
- **Specific**: names a value, line, function, condition, or ordering.
- **Predictive**: states what an experiment will show *before* you run it.
- **Discriminating**: its experiment rules out other hypotheses, not just confirms this one.

## Ranking which to test first
Score each candidate by **(probability it's true) × (information gained) ÷ (cost to test)**. Test the cheapest experiment that splits the hypothesis space most evenly — like binary search. A 30-second test that eliminates half the candidates beats a 10-minute test that confirms your favorite.

## The log format
Keep a running table. Each row is one experiment.

| # | Hypothesis | Prediction (if true) | Experiment | Result | Verdict |
|---|---|---|---|---|---|
| 1 | Cache miss returns None | Forcing a miss logs `user=None` then crashes | Clear cache, hit endpoint, log return value | `user=None`, crash reproduced | CONFIRMED |
| 2 | DB is down | Connection error in logs | Check DB health + logs | DB healthy, no conn errors | REJECTED |

Rules:
- Fill in **Prediction before Experiment** runs. No editing predictions after results.
- A REJECTED hypothesis is a win — record it; it stops you re-testing.
- Stop generating hypotheses once one is CONFIRMED *and* explains every observation. If it explains the crash but not why it's intermittent, you have an unexplained gap → keep going.
