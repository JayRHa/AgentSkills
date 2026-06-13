---
name: observability-setup
description: Instruments applications with structured logging, metrics, and distributed traces, then derives SLIs, SLOs, error budgets, and alerts that page only on user-facing pain. Use this skill when the user asks to "add observability", "instrument my app", "set up OpenTelemetry/OTel", "add structured logging", "expose Prometheus metrics", "add tracing", "define SLOs/SLIs", "set up alerting", "reduce alert noise", "build a Grafana dashboard", or wants the three pillars (logs/metrics/traces) wired into a service.
license: MIT
---

# Observability Setup

## Overview

Observability is the ability to ask arbitrary questions about a system's behavior from the outside, using its telemetry. This skill instruments a service across the **three pillars** — structured logs, metrics, and distributed traces — then turns raw signals into **SLIs**, **SLOs**, **error budgets**, and **actionable alerts**. The goal is not "more dashboards" but the ability to answer *"is the user in pain, and where?"* in under five minutes.

**Keywords:** observability, OpenTelemetry, OTel, structured logging, JSON logs, Prometheus, metrics, RED method, USE method, distributed tracing, spans, trace context, correlation ID, SLI, SLO, error budget, burn rate, alerting, Alertmanager, Grafana, on-call, golden signals, cardinality, exemplars.

Standardize on **OpenTelemetry (OTel)** for instrumentation — it is vendor-neutral and emits to Prometheus, Tempo, Loki, Datadog, Honeycomb, etc. Keep instrumentation code free of vendor SDKs; push vendor choice to the OTel Collector.

## Workflow

1. **Inventory the service.** Identify language/runtime, request entry points (HTTP/gRPC/queue), critical user journeys, downstream dependencies, and the existing telemetry backend (or pick one). Read `references/instrumentation-patterns.md` for per-pillar guidance.
2. **Add structured logging first.** Emit one JSON event per request with a stable schema (timestamp, level, message, `trace_id`, `span_id`, service, plus event-specific fields). Never log secrets/PII. Logs become useful only once they are queryable and correlated to traces.
3. **Instrument metrics using RED + USE.** For request-driven services apply **RED** (Rate, Errors, Duration); for resources apply **USE** (Utilization, Saturation, Errors). Use the four golden signals (latency, traffic, errors, saturation) as the checklist. Watch label **cardinality**.
4. **Add distributed tracing.** Auto-instrument the framework, propagate W3C `traceparent` across service boundaries, and add manual spans around meaningful business operations. Attach `trace_id` to every log line and metric exemplar so you can pivot signal → signal.
5. **Wire the OTel Collector.** Run a collector (agent + gateway) to receive OTLP, batch, sample, and export. This decouples app code from backends and centralizes sampling/redaction. See `references/instrumentation-patterns.md`.
6. **Define SLIs and SLOs.** Pick 1–3 SLIs per user journey (availability, latency, correctness). Set realistic SLO targets and a measurement window. Use `references/slo-cookbook.md` and the template in `templates/slo-spec.md`.
7. **Compute error budgets and burn-rate alerts.** Alert on *budget burn rate*, not on raw thresholds. Use multi-window multi-burn-rate alerts to balance fast detection against false pages. Generate rules with `scripts/gen_slo_alerts.py`.
8. **Validate and reduce noise.** Run `scripts/check_slo_burn.py` against live metrics to sanity-check. Ensure every alert is actionable, links to a runbook, and pages a human only when users are affected. Everything else is a ticket or a dashboard.

## Decision Framework

### Which pillar answers which question?
| Question | Pillar |
|---|---|
| "How many users are affected, how bad, since when?" | **Metrics** (aggregate, cheap, alertable) |
| "Why is *this specific* request slow / failing?" | **Traces** (per-request causal path) |
| "What exactly happened in this code path?" | **Logs** (high-detail, high-cost, sampled) |

Rule of thumb: **alert on metrics, diagnose with traces, confirm with logs.** All three must share `trace_id`.

### What to make an SLI?
Pick SLIs that track what a user actually experiences at the service boundary, expressed as `good events / valid events`:
- **Availability:** `non-5xx responses / total responses`
- **Latency:** `requests faster than threshold / total requests` (threshold-based, NOT an average)
- **Correctness/freshness:** domain-specific (e.g., `jobs completed within SLA / total jobs`)

Do **not** SLO on CPU, memory, or queue depth — those are causes, not symptoms. They belong on USE dashboards.

### Alert severity routing
| Burn rate / condition | Window | Action |
|---|---|---|
| Fast burn (≈14.4x, ~2% budget in 1h) | 1h + 5m | **Page** on-call |
| Slow burn (≈3x, ~5% budget in 6h) | 6h + 30m | **Page** (lower urgency) or ticket |
| Trend / saturation approaching limit | 1–3d | Ticket / dashboard |
| Informational | — | Dashboard only, never paged |

## Worked Example

See `examples/instrument-flask-service.md` for an end-to-end pass over a Python web service: JSON logging with trace correlation, OTel auto + manual spans, RED metrics, an availability + latency SLO, and the generated burn-rate alerts.

## Best Practices

- **One log schema, enforced.** Centralize a logger that always emits JSON with required fields. Inject `trace_id`/`span_id` automatically so humans never set them by hand.
- **Semantic conventions.** Use OTel semantic attribute names (`http.request.method`, `http.response.status_code`, `service.name`, `db.system`) so backends and dashboards work out of the box.
- **Tame cardinality.** Never put unbounded values (user IDs, request IDs, full URLs, emails) in metric labels — they explode time-series count and cost. Put them in logs/trace attributes instead. Use route templates (`/users/{id}`), not raw paths.
- **Sample traces intelligently.** Head-sample low-value traffic; tail-sample to keep all errors and slow requests. Always keep 100% of error traces.
- **SLOs over SLAs internally.** Set internal SLOs stricter than any contractual SLA so you get warning before breaching customer commitments.
- **Error budget drives prioritization.** Budget remaining → ship features. Budget exhausted → freeze risky changes and burn down reliability work.
- **Every alert has a runbook link.** An alert with no documented response is noise. Include the dashboard URL, likely causes, and first diagnostic step.
- **Symptom-based alerts, cause-based dashboards.** Page on user pain (the SLO); use cause metrics (CPU, GC, pool saturation) to diagnose after the page fires.
- **RED for services, USE for resources.** Apply both checklists deliberately rather than dashboarding whatever the library exposes.

## Common Pitfalls

- **Logging averages and alerting on them.** Averages hide tail latency. Use histograms and percentiles (p95/p99), and SLI as a ratio of requests under threshold.
- **Alert per host / per pod.** A 50-node fleet generates 50 pages for one bad deploy. Alert on the *aggregate user-facing SLI*.
- **Threshold alerts with no budget context.** `error_rate > 1%` pages constantly during normal blips. Burn-rate alerts only fire when the budget is genuinely at risk.
- **Unbounded label cardinality.** `http_requests_total{user_id="..."}` will OOM Prometheus. Keep label sets small and bounded.
- **Traces without propagation.** Forgetting to forward `traceparent` headers breaks the trace at every service hop, leaving disconnected single-service spans.
- **Logging secrets/PII.** Tokens, passwords, full card numbers, and personal data in logs are a security incident. Redact at the logger and again at the collector.
- **Instrumenting everything, prioritizing nothing.** 200 metrics nobody looks at is not observability. Start from user journeys and the golden signals.
- **No `valid events` denominator.** An SLI of "errors" without "total valid events" can't compute a meaningful budget. Always define both numerator and denominator, and what counts as *valid*.
