# Worked Example: Instrumenting a Python (Flask) Checkout Service

Goal: take a bare Flask service and add the three pillars + an availability and latency SLO with burn-rate alerts. Stack: OpenTelemetry SDK -> OTel Collector -> Prometheus (metrics) + Tempo (traces) + Loki (logs).

## Starting point
```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.post("/checkout")
def checkout():
    charge_card()       # external payment provider call
    reserve_inventory() # internal service call
    return jsonify(status="ok")
```
No logs we can query, no metrics, no traces. An on-call engineer can't answer "are users failing checkout right now?"

## 1. Structured logging with trace correlation
```python
import json, logging, sys
from opentelemetry import trace

class JsonTraceFormatter(logging.Formatter):
    REDACT = {"password", "authorization", "token", "card_number"}
    def format(self, record):
        span = trace.get_current_span().get_span_context()
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%03dZ"),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "checkout-api",
            "env": "prod",
            "trace_id": format(span.trace_id, "032x") if span.is_valid else None,
            "span_id": format(span.span_id, "016x") if span.is_valid else None,
        }
        for k, v in getattr(record, "fields", {}).items():
            payload[k] = "***" if k in self.REDACT else v
        return json.dumps(payload)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonTraceFormatter())
log = logging.getLogger("checkout"); log.addHandler(handler); log.setLevel(logging.INFO)
```
Now `log.info("checkout completed", extra={"fields": {"order.value": 49.90}})` emits queryable JSON carrying the active `trace_id`.

## 2. Tracing (auto + manual spans) and metrics
```python
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

FlaskInstrumentor().instrument_app(app)   # auto spans + http.* attributes
tracer = trace.get_tracer("checkout")
meter = metrics.get_meter("checkout")

req_counter = meter.create_counter(
    "http_server_requests_total", description="total checkout requests")
latency = meter.create_histogram(
    "http_server_request_duration_seconds", unit="s")

@app.post("/checkout")
def checkout():
    import time; start = time.perf_counter()
    status = "200"
    try:
        with tracer.start_as_current_span("charge_card") as s:
            s.set_attribute("payment.provider", "stripe")
            charge_card()
        with tracer.start_as_current_span("reserve_inventory"):
            reserve_inventory()
        log.info("checkout completed", extra={"fields": {"order.value": 49.90}})
        return jsonify(status="ok")
    except Exception as e:
        status = "500"
        trace.get_current_span().record_exception(e)
        log.error("checkout failed", extra={"fields": {"reason": str(e)}})
        raise
    finally:
        # route template, NOT raw path -> bounded cardinality
        labels = {"job": "checkout-api", "http.route": "/checkout", "status": status}
        req_counter.add(1, labels)
        latency.record(time.perf_counter() - start, labels)
```
Note: `http.route` (template) and `status` are low-cardinality labels. `order.value` and `payment.provider` are high cardinality, so they go on **spans/logs**, never metric labels.

## 3. Define the SLOs (see templates/slo-spec.md)
- **Availability SLO:** 99.9% of `/checkout` requests return non-5xx over 30 days.
  - SLI = `non-5xx / total`. Budget = 0.1%.
- **Latency SLO:** 95% of `/checkout` requests complete < 300ms over 30 days.

## 4. Generate burn-rate alerts
```bash
python3 scripts/gen_slo_alerts.py \
  --service checkout --job checkout-api --slo 99.9 \
  --metric http_server_requests_total --error-selector 'status=~"5.."' \
  --runbook https://runbooks.example.com/checkout > checkout_slo_rules.yml
```
This emits recording rules (`job:slo_errors:ratio_rate5m_checkout`, ...) and four paired-window alerts (page at 14.4x and 6x; ticket at 3x and 1x).

## 5. Sanity-check the budget during an incident
A bad deploy causes a 1.44% error ratio:
```bash
python3 scripts/check_slo_burn.py --slo 99.9 --error-ratio 0.0144
```
Output (abridged):
```
Burn rate            : 14.40x
Time to exhaust full budget at this rate: 50.0h
Alert tiers that would FIRE now:
  [FIRE] page   1h/5m    threshold burn 14.4x
  [FIRE] page   6h/30m   threshold burn 6.0x
  [FIRE] ticket 1d/1h    threshold burn 3.0x
  [FIRE] ticket 3d/6h    threshold burn 1.0x
```
The fast-burn page fires correctly. During normal operation (error-ratio 0.0002) no tier fires — no noise.

## 6. On-call payoff
Page fires (metric) -> click latency exemplar -> open the slow **trace** -> see `charge_card` span took 2.9s with an error -> pivot to logs by `trace_id` -> `reason="payment_provider_timeout"`. Root cause in minutes, not guesswork.
