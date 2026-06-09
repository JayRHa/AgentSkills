# Instrumentation Patterns — The Three Pillars

This reference gives concrete, vendor-neutral patterns for logs, metrics, and traces using OpenTelemetry (OTel) and Prometheus conventions. Keep app code free of vendor SDKs; let the OTel Collector route to your backend.

## 1. Structured Logging

### Required schema (every log line)
| Field | Example | Notes |
|---|---|---|
| `timestamp` | `2026-06-08T10:30:00.123Z` | RFC 3339, UTC, millisecond precision |
| `level` | `INFO` | one of TRACE/DEBUG/INFO/WARN/ERROR |
| `message` | `request completed` | static, low-cardinality string |
| `service` | `checkout-api` | matches `service.name` resource attr |
| `trace_id` | `4bf92f3577b34da6...` | for log <-> trace correlation |
| `span_id` | `00f067aa0ba902b7` | current span |
| `env` | `prod` | deploy environment |

Event-specific fields (`http.route`, `http.response.status_code`, `duration_ms`, `customer_tier`) go alongside, never replacing, the required fields.

### Rules
- Emit **JSON**, one object per line (ndjson). Humans grep; machines parse.
- **Never** interpolate variable data into `message`. Put variables in fields so they are queryable: `message="payment failed"` + `reason="insufficient_funds"`, not `message="payment failed: insufficient_funds for user 42"`.
- Inject `trace_id`/`span_id` from the active span context automatically via a logging filter/processor.
- Redact secrets at the logger: maintain a denylist of keys (`password`, `authorization`, `token`, `ssn`, `card_number`) that are masked before serialization.
- Log levels: ERROR = needs human attention; WARN = degraded but handled; INFO = state transitions / request summary; DEBUG = sampled, off in prod by default.

### Sampling
High-volume INFO/DEBUG should be head-sampled (e.g., 1 in N) or driven by trace sampling so a sampled trace keeps its logs. Always keep 100% of ERROR/WARN.

## 2. Metrics — RED + USE + Golden Signals

### The four golden signals (SRE)
1. **Latency** — distribution of request durations (split success vs error latency).
2. **Traffic** — demand (requests/sec, messages/sec).
3. **Errors** — rate of failed requests.
4. **Saturation** — how full the most constrained resource is.

### RED (request-driven services)
- **Rate** — `http_server_requests_total` (counter), rate over time.
- **Errors** — same counter filtered by `status` class, or a dedicated errors counter.
- **Duration** — `http_server_request_duration_seconds` (histogram) → percentiles.

### USE (resources: CPU, memory, disk, pools, queues)
- **Utilization** — % time the resource was busy.
- **Saturation** — queued/waiting work (run queue, connection pool wait).
- **Errors** — error events for the resource (evictions, OOM kills, dropped packets).

### Metric type cheat sheet
| Type | Use for | Example |
|---|---|---|
| Counter | monotonic totals | `requests_total`, `errors_total` |
| Gauge | point-in-time value | `queue_depth`, `inflight_requests` |
| Histogram | distributions → percentiles | `request_duration_seconds` |

### Naming & labels (Prometheus + OTel)
- Unit-suffixed names: `_seconds`, `_bytes`, `_total`.
- Use OTel semantic attributes: `http.request.method`, `http.route`, `http.response.status_code`.
- **Cardinality budget:** total series = product of label cardinalities. Keep each label small and bounded. Forbidden labels: user id, request id, raw path, email, full URL, free text.
- Use **route templates** (`/orders/{id}`) so all order lookups share one series.
- **Exemplars:** attach a `trace_id` to histogram buckets so a slow latency bucket links straight to an example trace.

## 3. Distributed Tracing

### Concepts
- **Trace** = one request's journey; a tree of **spans**.
- **Span** = a timed operation with a name, start/end, status, and attributes.
- **Context propagation** = passing `traceparent`/`tracestate` (W3C Trace Context) across process boundaries (HTTP headers, message metadata).

### Pattern
1. **Auto-instrument** the web framework, HTTP client, DB driver, and queue client first — this covers most spans for free.
2. Add **manual spans** around meaningful business operations the framework can't see: `span("charge_card")`, `span("reserve_inventory")`. Set status to ERROR and record the exception on failure.
3. Add attributes that aid diagnosis (`order.value`, `payment.provider`) — high cardinality is fine on spans (unlike metric labels).
4. **Propagate** context on every outbound call. Verify with a multi-service test that one trace spans all hops.

### Sampling strategy
| Strategy | Where | When |
|---|---|---|
| Head (probabilistic) | SDK / agent | cheap, decides up front; e.g., 10% of traffic |
| Tail | Collector | keep all errors + slow traces, drop boring ones |
| Always-on errors | both | never drop a trace whose root span errored |

Recommended: low head sample for baseline + tail-sampling in the collector that retains 100% of error/slow traces.

## 4. OTel Collector topology

```
  app (OTLP) --> otel-collector (agent, per-node)
                      |  receive: otlp
                      |  process: batch, memory_limiter, redaction, tail_sampling
                      v
               otel-collector (gateway)
                      |--> Prometheus / remote_write   (metrics)
                      |--> Tempo / Jaeger              (traces)
                      '--> Loki / Elasticsearch        (logs)
```
Benefits: app emits OTLP only; batching/retry/redaction/sampling are centralized; backend swaps need zero app redeploys.

## Correlation: the payoff
With `trace_id` in logs, exemplars on metrics, and propagated trace context, the on-call flow becomes:
1. SLO alert fires (metric) → 2. open exemplar → jump to a representative slow/error **trace** → 3. find the failing span → 4. pivot to that span's **logs** by `trace_id`. Five-minute diagnosis instead of guesswork.
