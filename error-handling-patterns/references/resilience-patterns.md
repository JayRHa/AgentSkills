# Resilience Patterns: Deep Reference

How retries, backoff, timeouts, circuit breakers, bulkheads, and idempotency work and compose.

## 1. Exponential Backoff with Jitter

Problem: many clients failing at once and retrying on the same schedule create a synchronized **retry storm** (thundering herd) that re-overloads the recovering service.

Solution: randomize delays so clients decorrelate.

Formulas (let `base` = initial delay, `cap` = max delay, `n` = attempt index from 0):

- **No jitter**: `delay = min(cap, base * 2^n)` — backs off but stays synchronized. Avoid.
- **Full jitter** (recommended default): `delay = random(0, min(cap, base * 2^n))`.
- **Equal jitter**: `temp = min(cap, base * 2^n); delay = temp/2 + random(0, temp/2)`.
- **Decorrelated jitter**: `delay = min(cap, random(base, prev_delay * 3))`. Good for self-clocking, often slightly fewer calls.

AWS Architecture Blog ("Exponential Backoff And Jitter") found **full jitter** and **decorrelated jitter** both minimize total work and completion time; full jitter is the simplest solid default.

Guardrails:
- Cap attempts (3–5 typical) AND enforce an absolute deadline.
- Cap individual delay (e.g., 20–30s).
- Honor server `Retry-After` over your computed delay.
- Only back off on transient errors.

## 2. Retry Budgets and Amplification

Naive per-request retries amplify load: 3 retries can triple traffic to a struggling dependency, deepening the outage. Mitigations:

- **Retry budget / token bucket**: allow retries only while retries stay under, e.g., 10% of total requests. When exhausted, fail fast without retrying.
- **No retries on retries**: don't let each layer in a call chain multiply retries (layer A retries 3x, B retries 3x = 9x). Retry at *one* layer, ideally the outermost that owns the operation, or pass a "do not retry" flag downstream.
- **Circuit breaker** as the hard stop when a dependency is clearly down.

## 3. Timeouts vs Deadlines

- **Timeout**: per-call max duration. Simple but doesn't bound *total* latency across a chain (A→B→C each 10s = up to 30s).
- **Deadline**: an absolute instant computed once at the edge and propagated. Each hop computes `remaining = deadline - now` and uses it (or fails immediately if already past). This bounds end-to-end latency — the correct approach for microservices.

Set timeouts from data: connect timeout short (1–3s); read timeout ≈ dependency p99 + margin. Too tight → false failures; too loose → cascading slowness.

## 4. Circuit Breaker

States:
- **Closed**: requests pass; track failures (count or rolling error rate).
- **Open**: trip when failures exceed threshold; reject immediately for a `reset_timeout` (fail fast or fall back). Protects the downed dependency and frees caller resources.
- **Half-open**: after cooldown, allow limited trial requests. Success(es) → Closed; any failure → Open again.

Tuning:
- Threshold: e.g., 50% error rate over a rolling window of ≥20 requests, or N consecutive failures.
- Reset timeout: a few seconds to tens of seconds; longer for expensive dependencies.
- Count timeouts and 5xx as failures; do NOT count 4xx client errors (those are your fault, not the dependency's).
- Per-dependency breakers, never one global breaker.

Interaction with retries: the breaker is the outer guard. When open, skip retries entirely and go straight to fallback.

## 5. Bulkheads

Isolate resources so one failing dependency can't sink the ship:
- Separate connection pools / thread pools / semaphores per dependency.
- Concurrency limits per downstream so a slow one can't consume all workers.
- Named after ship compartments: a breach floods one compartment, not the whole hull.

Without bulkheads, a single slow dependency holding threads can exhaust the pool and make *every* endpoint hang — classic cascading failure.

## 6. Idempotency (the foundation of safe retries)

An operation is idempotent if applying it N times has the same effect as once. Required for retrying writes.

Techniques:
- **Idempotency key**: client sends a unique key; server dedupes and returns the original result on replay. (Stripe-style.)
- **Conditional writes**: `If-Match`/ETag, compare-and-swap, optimistic version columns.
- **Natural idempotency**: PUT (set to value), DELETE (gone is gone), upserts.
- **Dedup store**: record processed message IDs (for at-least-once queues).

For ambiguous failures (timeout on a write), idempotency makes the retry safe instead of duplicating the effect.

## 7. Dead Letter Queues & Outbox

- **DLQ**: after max retries, move the message to a dead-letter queue for inspection/replay instead of dropping it or blocking the main queue.
- **Transactional outbox**: write the domain change and an outbox event in the same DB transaction; a relay publishes events reliably. Avoids the dual-write problem (DB committed but event lost).

## 8. How They Compose (request flow)

```
request
  └─ bulkhead (acquire concurrency slot for this dependency; else shed load)
      └─ circuit breaker (open? -> fail fast -> fallback)
          └─ retry loop (bounded attempts + deadline + budget)
              └─ single attempt with timeout/deadline
                  └─ remote call
          on exhausted/permanent error -> fallback (cache/default/queue/clean error)
```

Order matters: breaker outside retries (don't retry into an open breaker); timeout inside each attempt; bulkhead outermost so load shedding happens before any work.

## 9. Observability

Emit and alert on:
- error rate by class (transient/permanent), per dependency
- retry count and retry-success rate
- circuit breaker state transitions and time-in-open
- timeout count and p99/p999 latency
- fallback / degraded-mode activations
- DLQ depth

Use correlation IDs to trace a failure across services. Log each error once, at the boundary with full context.
