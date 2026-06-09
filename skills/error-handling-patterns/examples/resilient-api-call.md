# Worked Example: A Resilient API Client

Goal: call a flaky payment-status API correctly. Combine timeout, retry with
backoff+jitter, a circuit breaker, idempotency, and a cache fallback — and
reason about behavior under each failure mode.

## Requirements

- Read endpoint: `GET /payments/{id}` (idempotent — safe to retry).
- Write endpoint: `POST /payments` (NOT idempotent unless given an idempotency key).
- Latency p99 ≈ 400 ms. Budget per request: 2 s total.
- If the service is down, the product page must still render (degrade to cache).

## Step 1 — Classify failures

| Failure | Class | Reaction |
|---|---|---|
| connect/read timeout | transient (ambiguous for POST) | retry GET; retry POST only with key |
| 429 / 503 | transient | back off, honor `Retry-After` |
| 500 / 502 / 504 | transient | retry (bounded) |
| 400 / 401 / 404 / 422 | permanent | fail fast, surface error |
| breaker open | shed | fail fast -> cache fallback |

## Step 2 — The client (Python, using scripts/retry.py)

```python
import requests
from retry import RetryPolicy, retry, CircuitBreaker, CircuitOpenError, RetryError

BUDGET_S = 2.0
CONNECT_TIMEOUT, READ_TIMEOUT = 1.0, 1.0

class TransientHTTP(Exception):
    def __init__(self, status, retry_after=None):
        super().__init__(f"transient HTTP {status}")
        self.status, self.retry_after = status, retry_after

class PermanentHTTP(Exception):
    def __init__(self, status):
        super().__init__(f"permanent HTTP {status}")
        self.status = status

breaker = CircuitBreaker(failure_threshold=5, reset_timeout=10.0,
                         counted_exceptions=(TransientHTTP, requests.RequestException))

def _classify(resp):
    s = resp.status_code
    if s < 400:
        return resp
    if s in (408, 429) or s >= 500:
        ra = resp.headers.get("Retry-After")
        raise TransientHTTP(s, float(ra) if ra and ra.isdigit() else None)
    raise PermanentHTTP(s)            # 4xx -> do not retry

policy = RetryPolicy(
    max_attempts=4, base=0.1, cap=1.0, deadline=BUDGET_S,
    retryable=(TransientHTTP, requests.Timeout, requests.ConnectionError),
    retry_after=lambda e: getattr(e, "retry_after", None),
)

@retry(policy)
def _get(session, payment_id):
    resp = session.get(f"https://api/payments/{payment_id}",
                       timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    return _classify(resp)

def get_payment_status(session, payment_id, cache):
    try:
        with breaker:                       # fail fast if open
            resp = _get(session, payment_id)
        data = resp.json()
        cache.set(payment_id, data)         # refresh cache on success
        return {"status": data["status"], "degraded": False}
    except (CircuitOpenError, RetryError, PermanentHTTP) as err:
        cached = cache.get(payment_id)       # GRACEFUL DEGRADATION
        if cached is not None:
            return {"status": cached["status"], "degraded": True}
        # last resort: clean, actionable error (never a stack trace to the user)
        return {"status": "unknown", "degraded": True, "error": str(err)}
```

## Step 3 — Idempotent writes

```python
import uuid

def create_payment(session, amount, idem_key=None):
    idem_key = idem_key or str(uuid.uuid4())   # caller can pass a stable key
    # Same key on retry => server dedupes => safe to retry the POST.
    @retry(policy)
    def _post():
        resp = session.post("https://api/payments",
                            json={"amount": amount},
                            headers={"Idempotency-Key": idem_key},
                            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        return _classify(resp)
    return _post().json()
```

## Step 4 — Behavior under each failure mode

| Scenario | What happens | Outcome |
|---|---|---|
| 1 transient 503, then 200 | retry waits `random(0, 0.1)`s, succeeds | success, cache refreshed |
| Repeated 503 within 2 s budget | up to 4 attempts, deadline stops it | `RetryError` -> serve cache (degraded) |
| 503 with `Retry-After: 1` | waits 1 s (server hint) before retry | honors server |
| 404 | `PermanentHTTP`, no retry | clean error, no wasted attempts |
| 5 consecutive failures | breaker opens | subsequent calls FAST-FAIL -> cache |
| Breaker open, cooldown passes | half-open trial; success closes it | self-heals |
| POST times out (ambiguous) | retried with SAME idempotency key | no double charge |
| Service fully down, cache warm | breaker open + cache hit | page renders with stale data flagged `degraded:true` |
| Service down, cold cache | clean `status: unknown` error | no crash, no hang |

## Why this is correct

- **Bounded**: per-attempt timeout (1 s connect + 1 s read) AND total deadline (2 s).
- **Safe retries**: only transient errors; POST retried only because of the idempotency key.
- **No retry storm**: full jitter decorrelates clients; breaker stops retries when down.
- **Always responsive**: degradation guarantees a fast, clean response even in total outage.
- **Observable**: `degraded` flag + typed errors make metrics/alerting trivial.
