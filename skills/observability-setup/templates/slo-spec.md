# SLO Specification: <SERVICE / JOURNEY NAME>

> One spec per user journey. Fill every field. Delete the guidance in angle brackets.

## 1. Service & journey
- **Service:** <e.g. checkout-api>
- **User journey:** <e.g. "customer submits an order at /checkout">
- **Owner / team:** <team + on-call rotation>
- **Tier / criticality:** <critical | important | best-effort>

## 2. SLI definition
| Field | Value |
|---|---|
| SLI type | <availability / latency / quality / freshness> |
| Good events | <e.g. responses with status < 500> |
| Valid events | <e.g. all /checkout responses, excluding client 4xx> |
| Measurement point | <where measured: load balancer / server / client> |
| Metric source | <e.g. http_server_requests_total{job="checkout-api"}> |

**SLI formula:** `good_events / valid_events`

<For latency, state thresholds explicitly, e.g. "good = duration <= 300ms". Never use an average.>

## 3. SLO target & window
| Field | Value |
|---|---|
| Target | <e.g. 99.9%> |
| Window | <rolling 28 or 30 days> |
| Error budget | <1 - target, e.g. 0.1%> |
| Related SLA (if any) | <external contract; internal SLO must be stricter> |

## 4. Error budget policy
- **Budget healthy (>25% remaining):** ship features normally.
- **Budget low (<25% remaining):** increase change review; defer risky launches.
- **Budget exhausted (0%):** freeze feature changes; reliability work takes priority until recovered.
- **Decision owner:** <who enforces the freeze>

## 5. Alerting (burn-rate, multi-window)
| Severity | Long / short window | Burn rate | Routes to |
|---|---|---|---|
| Page (fast) | 1h / 5m | 14.4x | <on-call pager> |
| Page (slow) | 6h / 30m | 6x | <on-call pager> |
| Ticket | 1d / 1h | 3x | <ticket queue> |
| Ticket | 3d / 6h | 1x | <ticket queue> |

Generate the Prometheus rules with:
```bash
python3 scripts/gen_slo_alerts.py --service <name> --job <job> \
  --slo <target> --metric <metric> --runbook <url>
```

## 6. Dashboards & runbook
- **SLO dashboard:** <url — shows SLI, budget remaining, burn rate>
- **Cause/USE dashboard:** <url — CPU, memory, pool saturation, dependency latency>
- **Runbook:** <url — first diagnostic steps, likely causes, escalation>

## 7. Review
- **Last reviewed:** <date>
- **Next review:** <date — review SLOs quarterly or after major changes>
- **Notes / known exclusions:** <e.g. planned maintenance windows excluded>
