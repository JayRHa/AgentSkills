# SLO Cookbook — SLIs, SLOs, Error Budgets, Burn-Rate Alerts

## Definitions
- **SLI (Service Level Indicator):** a measured ratio of good behavior. `SLI = good_events / valid_events`.
- **SLO (Service Level Objective):** the target for an SLI over a window. e.g. *99.9% of valid requests succeed over 28 days*.
- **Error budget:** `1 - SLO`. At 99.9%, budget = 0.1% of events may fail. The budget is permission to take risk.
- **SLA:** an external contract with penalties. Always set internal SLOs **stricter** than any SLA.

## Step 1 — Choose SLIs per user journey
For each critical journey (e.g. "checkout", "search", "login"), define at the service boundary:

| SLI type | good_events | valid_events |
|---|---|---|
| Availability | responses with status < 500 | all responses (exclude client 4xx if appropriate) |
| Latency | requests with duration <= T | all valid requests |
| Quality/Correctness | results passing a correctness check | all results |
| Freshness | data served within max staleness | all reads |

**Latency must be threshold-based, not an average.** Define explicit thresholds, e.g. "95% of requests < 300ms AND 99% < 1s".

### What NOT to SLO on
CPU, memory, GC pauses, queue depth, replica count. These are *causes*. They live on USE dashboards and inform diagnosis, never the SLO.

## Step 2 — Pick a target and window
| Target | Allowed downtime / 30 days | Typical use |
|---|---|---|
| 99% | ~7h 18m | internal / best-effort |
| 99.9% | ~43m | standard production service |
| 99.95% | ~21m | important customer-facing |
| 99.99% | ~4m | critical infra (costly!) |

Use a **rolling 28- or 30-day window**. Every extra nine roughly multiplies the operational cost — target only what users actually need.

## Step 3 — Error budget math
```
budget_fraction      = 1 - SLO_target          # e.g. 1 - 0.999 = 0.001
budget_events        = budget_fraction * total_valid_events_in_window
budget_consumed      = bad_events_so_far / budget_events
budget_remaining     = 1 - budget_consumed
```
Policy: budget remaining → ship features. Budget exhausted → freeze risky changes, prioritize reliability.

## Step 4 — Burn-rate alerting (the right way)
A **burn rate** of 1 exhausts the entire budget exactly at the end of the window. Higher burn = faster exhaustion.
```
burn_rate = (bad_events / total_valid_events) / (1 - SLO_target)
          = observed_error_ratio / error_budget
```
Example: SLO 99.9% (budget 0.001). If current error ratio is 0.0144, burn rate = 14.4 → you'd burn the whole 30-day budget in ~50 hours.

### Multi-window, multi-burn-rate (Google SRE recommended)
Combine a long and short window per alert so it fires fast but auto-resolves when the spike ends. Standard thresholds for a 30-day SLO:

| Severity | Long window | Short window | Burn rate | Budget spent to fire |
|---|---|---|---|---|
| Page (fast) | 1h | 5m | 14.4 | ~2% in 1h |
| Page (slow) | 6h | 30m | 6 | ~5% in 6h |
| Ticket | 24h | 1h | 3 | ~10% in 1d |
| Ticket | 72h | 6h | 1 | ~10% in 3d |

The alert fires only when **both** windows exceed the threshold — the short window prevents alerting on a spike that already recovered.

## Step 5 — Recording rules
Precompute the SLI as a Prometheus recording rule so alert queries are cheap and consistent:
```yaml
groups:
  - name: slo:checkout
    interval: 30s
    rules:
      - record: job:slo_errors:ratio_rate5m
        expr: |
          sum(rate(http_server_requests_total{job="checkout",status=~"5.."}[5m]))
          / sum(rate(http_server_requests_total{job="checkout"}[5m]))
      # repeat for 30m, 1h, 6h, 1d, 3d windows used by burn-rate alerts
```

## Step 6 — Alert hygiene checklist
- [ ] Alert maps to a user-facing SLI (symptom, not cause).
- [ ] Multi-window burn-rate, not a static threshold.
- [ ] Fires on the aggregate, not per-host/per-pod.
- [ ] Has a `severity` label that routes correctly (page vs ticket).
- [ ] Annotation includes a runbook URL and dashboard link.
- [ ] Has been tested against a historical incident (would it have fired? would it have flapped?).

## Worked numbers
- SLO = 99.9% over 30 days. Budget = 0.1% of requests.
- At 1M requests/day → 30M/window → budget = 30,000 failed requests.
- A bad deploy causing 5% errors for 1 hour at 12 req/s ≈ 43,200 reqs × 5% = 2,160 bad → ~7.2% of budget in one hour → fast-burn page fires correctly.
