# Worked Example: Checkout API Outage

This shows the skill applied end-to-end: raw events in, finished postmortem out.

## Step 1-2: Raw events file (`events.txt`)

```
# Checkout API outage - 2026-06-08
2026-06-08T14:02:00Z | deploy-bot | start    | Deploy v812 shipped to checkout-service
2026-06-08T14:06:00Z | datadog    |          | DB CPU begins climbing past 70%
2026-06-08T14:10:00Z | datadog    | detect   | Alert: API 5xx rate > 5% (fired late; threshold tuned for old traffic)
2026-06-08T14:12:00Z | priya      | ack      | On-call acknowledged page, opened war room
2026-06-08T14:18:00Z | priya      |          | Identified v812 as suspect via deploy log correlation
2026-06-08T14:24:00Z | priya      | mitigate | Rolled back to v811 (manual; no auto-rollback)
2026-06-08T14:31:00Z | datadog    |          | 5xx rate falling
2026-06-08T14:53:00Z | priya      | resolve  | Error rate at baseline, incident closed
```

## Step 2-3: Run the script

```
$ python3 scripts/timeline_builder.py examples/events.txt --metrics
Incident metrics
================
Incident start         : 2026-06-08T14:02:00Z
Detected               : 2026-06-08T14:10:00Z
Mitigated              : 2026-06-08T14:24:00Z
Resolved               : 2026-06-08T14:53:00Z
Time to detect (TTD)   : 8m 0s
Time to mitigate (TTM) : 22m 0s
Time to resolve (TTR)  : 51m 0s
Total duration         : 51m 0s
```

## Finished postmortem (excerpt)

### Summary
A deploy to checkout-service shipped a query missing an index, saturating the database and causing a 40% 5xx error rate for 51 minutes. ~12,000 checkout attempts failed. The systemic root cause was the absence of pre-production query-performance testing combined with no automatic deploy rollback.

### Impact
- **Users affected:** ~40% of checkout traffic, ~12,000 failed checkout attempts.
- **Duration:** 2026-06-08 14:02 - 14:53 UTC (51 min).
- **Business/SLA impact:** Estimated ~$18k in deferred/lost orders; monthly availability error budget ~30% consumed in one event.

### Root Cause Analysis
- **Symptom:** Checkout API 5xx rate spiked to ~40%.
- **Trigger:** Deploy v812 introduced an unindexed query.
- **Five Whys:** 5xx -> query timeouts -> DB CPU saturation -> unindexed full table scans under load -> regression not caught pre-prod -> **CI has no representative-load / EXPLAIN gate.**
- **Root causes:** (a) No automated pre-production query-performance detection; (b) no automatic rollback on error-rate breach.

### Contributing Factors
- Alert fired ~8 min late: 5xx threshold still tuned for last year's traffic baseline (detection gap).
- No DB-saturation runbook; responder diagnosed from scratch (knowledge gap).
- Rollback was fully manual, adding minutes to mitigation (mitigation gap).

### Detection & Response Review
- **Detected:** auto-alert, but ~8 min late and after CPU had already saturated. TTD should be < 3 min for this class.
- **What went well:** deploy-log correlation made the culprit obvious within 6 min of ack; war room spun up immediately; rollback was clean once decided.

### Action Items

| # | Action | Type | Owner | Priority | Due | Ticket |
|---|---|---|---|---|---|---|
| 1 | Add CI stage running EXPLAIN/load analysis on changed queries; fail build on full-table-scan regressions | Prevent | Sam | P0 | 2026-06-15 | OPS-482 |
| 2 | Add auto-rollback for checkout-service on 5xx > 5% sustained 2 min | Mitigate-faster | Sam | P0 | 2026-06-18 | OPS-485 |
| 3 | Retune 5xx alert threshold to current traffic; add DB CPU > 80% leading-indicator alert | Detect-faster | Priya | P1 | 2026-06-20 | OPS-481 |
| 4 | Write DB-saturation playbook and link from on-call dashboard | Mitigate-faster | Lee | P1 | 2026-06-22 | OPS-483 |

### Blameless note
Nothing here attributes the incident to the engineer who wrote the query. The query slipped through because the *system* had no gate for query-performance regressions and no automatic safety net — those are the fixes.
