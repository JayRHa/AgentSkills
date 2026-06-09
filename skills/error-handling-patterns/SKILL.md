---
name: error-handling-patterns
description: Designs robust, production-grade error handling — choosing between result types and exceptions, implementing retries with exponential backoff and jitter, applying timeouts and deadlines, adding circuit breakers, and building graceful degradation and fallbacks. Use this skill when writing or reviewing code that calls networks/databases/external APIs, when asked to "make this resilient", "add retry logic", "handle failures", "add timeouts", "handle errors properly", "make this fault tolerant", "add a circuit breaker", "stop swallowing exceptions", or when classifying errors as transient vs permanent and deciding what to retry, fail fast, or degrade.
license: MIT
---

# Error Handling Patterns

## Overview

Robust error handling is about making explicit, deliberate decisions for every failure mode instead of letting failures propagate as unhandled crashes, silent data corruption, or hung requests. This skill provides a decision framework and concrete patterns for: distinguishing recoverable from unrecoverable errors, choosing between result types and exceptions, retrying transient failures safely, bounding latency with timeouts and deadlines, protecting failing dependencies with circuit breakers, and degrading gracefully when a dependency is down.

Keywords: error handling, exceptions, result type, Either, retry, exponential backoff, jitter, timeout, deadline, circuit breaker, bulkhead, idempotency, graceful degradation, fallback, fail fast, fault tolerance, resilience, transient errors, dead letter queue.

Apply this skill whenever code crosses a trust or failure boundary: network calls, database queries, file I/O, external APIs, message queues, subprocess execution, or any operation that can fail in ways the caller must handle.

## Core Principles

1. **Every error has exactly one owner.** At each layer, decide: handle it here, transform and rethrow, or let it propagate. Never silently swallow.
2. **Classify before you react.** A failure is either *transient* (retry may succeed) or *permanent* (retry is futile). The classification drives every other decision. See `references/error-taxonomy.md`.
3. **Fail fast on programmer errors, recover from operational errors.** Bugs (null deref, bad invariants) should crash loudly. Operational failures (timeout, 503, connection reset) should be handled.
4. **Bound everything.** Every remote call gets a timeout. Every retry loop gets a max attempt count and a deadline. Unbounded waits and unbounded retries are outages waiting to happen.
5. **Preserve context.** Wrap errors with what you were doing, but keep the original cause chain. Never throw away stack traces or root causes.
6. **Make retries safe.** Only retry operations that are idempotent or made idempotent with an idempotency key. Retrying a non-idempotent write can double-charge a customer.

## Workflow

Follow this procedure when designing or reviewing error handling for an operation:

1. **Enumerate failure modes.** List what can go wrong: timeout, connection refused, 4xx, 5xx, malformed response, partial write, auth expiry, rate limit, disk full, deserialization error. Use the checklist in `references/error-taxonomy.md`.
2. **Classify each failure** as transient (retryable), permanent (non-retryable), or ambiguous (unknown outcome — treat writes as possibly-applied).
3. **Choose the error-signaling style** for this layer using the decision table below: exceptions vs result type. Be consistent within a module.
4. **Decide the reaction per class:**
   - Transient → retry with backoff + jitter, bounded by attempts and deadline.
   - Permanent → fail fast, surface a clear, actionable error to the caller.
   - Ambiguous → only retry if idempotent; otherwise reconcile or fail and alert.
5. **Add a timeout/deadline** to every remote call. Propagate a deadline across call chains so total latency is bounded.
6. **Add a circuit breaker** around dependencies that can fail in bulk, to stop hammering a downed service and to fail fast while it recovers.
7. **Define the degraded behavior.** If the dependency is unavailable, what does the user get? Cached data, a default, reduced functionality, or a clean error? Decide explicitly.
8. **Wrap and log with context** at the boundary where you have the most information; avoid double-logging the same error at every layer.
9. **Test the failure paths.** Inject timeouts, 500s, and connection drops. Verify retries, backoff, breaker trips, and fallbacks. Failure paths are the least-tested and most important code.

## Decision Framework: Result vs Exception

Use the result/Either pattern when failures are *expected, common, and part of normal control flow*; use exceptions for *exceptional, rare, or non-local* conditions.

| Use a **Result/Either type** when… | Use an **Exception** when… |
|---|---|
| Failure is a normal outcome (parse, validate, lookup-miss) | Failure is unexpected / a violated invariant |
| The caller must always handle the failure | The error should unwind many stack frames |
| You want failures visible in the type signature | Handling far from the throw site is acceptable |
| Performance-sensitive hot paths (no stack unwinding) | Constructors / places that can't return values |
| Functional / explicit-flow codebases | Idiomatic in the language (Python, Ruby, Java checked) |

Rules of thumb:
- **Don't use exceptions for control flow** that runs on every request.
- **Don't return `null`/`-1`/`false` to mean "error"** — that loses the reason. Return a typed result.
- **Don't catch-all-and-continue.** A bare `except: pass` / `catch (e) {}` is the single most common resilience bug.
- **One style per layer.** Translate at boundaries (e.g., catch low-level exceptions, return domain results from a service).

See `references/patterns-by-language.md` for idiomatic result/exception patterns in Python, TypeScript, Go, Rust, and Java.

## Retries: Backoff and Jitter

Retries turn transient blips into successes — but naive retries cause **retry storms** and **thundering herds** that amplify outages. Rules:

1. **Only retry idempotent or idempotency-keyed operations.** GET/PUT/DELETE are typically safe; POST usually is not unless you send an idempotency key.
2. **Only retry transient/retryable errors** (timeouts, 429, 502/503/504, connection resets). Never retry 400/401/403/404/422 or validation errors.
3. **Use exponential backoff with jitter**, not fixed delays. Full jitter (`sleep = random(0, base * 2^attempt)`) is the recommended default; it decorrelates clients.
4. **Cap the delay** (e.g., max 30s) and the **attempts** (e.g., 3–5), and enforce an **overall deadline**.
5. **Respect `Retry-After`** headers from the server (429/503). The server knows best.
6. **Add a circuit breaker** so retries stop entirely when a dependency is clearly down.
7. **Budget retries.** Track a retry budget (e.g., retries ≤ 10% of requests) so retries can't dominate traffic.

Backoff comparison (base = 100ms):

| Strategy | Formula | Problem it solves / causes |
|---|---|---|
| Fixed | `delay = base` | Simple; causes synchronized retry storms |
| Exponential, no jitter | `base * 2^n` | Backs off, but clients stay synchronized |
| Exponential + full jitter | `random(0, base * 2^n)` | **Recommended.** Decorrelates clients |
| Decorrelated jitter | `min(cap, random(base, prev*3))` | Good for self-clocking clients |

Use the ready-made implementation in `scripts/retry.py` (pure stdlib, sync + async, full-jitter backoff, retryable-exception filtering, deadline support). See `examples/resilient-api-call.md` for a full worked example combining retry + timeout + circuit breaker + fallback.

## Timeouts and Deadlines

- **Every** network/DB/IO call must have a timeout. The default of "infinite" is wrong.
- Set **connect** and **read** timeouts separately; connect should be short (1–3s).
- Prefer **deadlines (absolute time) over per-call timeouts** in call chains: compute `deadline = now + budget` once, pass it down, and each call uses `remaining = deadline - now`. This bounds *total* latency, not per-hop.
- A timeout is an **ambiguous** failure for writes: the operation may have succeeded. Make writes idempotent so a retry is safe.
- Choose timeouts from latency data: roughly p99 + margin, not a guessed round number. Too-tight timeouts cause spurious failures; too-loose ones cause cascading slowness.

## Circuit Breakers and Bulkheads

A **circuit breaker** stops calls to a failing dependency to let it recover and to fail fast:
- **Closed** → calls flow; count failures.
- **Open** → after the failure threshold trips, reject immediately (fail fast / fall back) for a cooldown.
- **Half-open** → after cooldown, allow a few trial calls; success closes, failure re-opens.

A **bulkhead** isolates resources (separate connection pools / thread pools / concurrency limits per dependency) so one slow dependency can't exhaust shared capacity and take down everything.

`scripts/retry.py` includes a small thread-safe `CircuitBreaker`. See `references/resilience-patterns.md` for thresholds, tuning, and how breakers, bulkheads, retries, and timeouts compose.

## Graceful Degradation

When a dependency fails, decide the user-visible behavior *in advance*. Options, from best to worst UX:
1. **Serve from cache** (possibly stale) with a freshness indicator.
2. **Return a sensible default / reduced feature** (e.g., hide recommendations, keep checkout working).
3. **Queue for later** (write to a durable queue / outbox, process when healthy).
4. **Partial response** — return what succeeded, mark what failed.
5. **Clean, actionable error** — never a stack trace or hung spinner.

Never let a non-critical dependency failure break a critical path. Recommendation service down? The product page must still render.

## Best Practices

- Wrap-and-chain errors with context: include the operation, key identifiers, and the original cause (`raise X from err`, `fmt.Errorf("...: %w", err)`, `new Error(msg, { cause })`).
- Log an error **once**, at the boundary that has full context. Pass typed errors up; don't log-and-rethrow at every frame.
- Make failures observable: emit metrics (error rate, retry count, breaker state, timeout count) and structured logs with correlation IDs.
- Keep error messages actionable: what failed, why, and what the caller can do.
- Use idempotency keys for all external writes that may be retried.
- Centralize policy (timeouts, retry config, breaker thresholds) as configuration, not scattered magic numbers.
- Distinguish *user-facing* messages (safe, generic) from *internal* details (full diagnostics) — don't leak internals.
- Clean up resources on every path (`finally`, `defer`, context managers, RAII).

## Common Pitfalls

- **Swallowing exceptions** (`except: pass`, empty `catch`) — hides bugs and corrupts state. At minimum, log and rethrow.
- **Retrying non-idempotent writes** — double charges, duplicate orders. Use idempotency keys.
- **Retrying permanent errors** (400/401/404) — wastes time, hammers the server, delays the real failure.
- **No jitter** — synchronized clients create retry storms that DDoS your own backend.
- **Unbounded retries / no deadline** — turns a blip into a hang.
- **Missing timeouts** — one slow dependency exhausts all threads/connections; cascading failure.
- **Catching `Exception`/`Throwable` too broadly** — masks `KeyboardInterrupt`, `OutOfMemory`, programmer errors. Catch specific types.
- **Losing the cause chain** — re-raising a new error without `from`/`cause`/`%w` destroys the root cause.
- **Double logging** — the same error logged at five layers makes triage impossible.
- **Treating timeout as definite failure for writes** — leads to lost updates or unexpected duplicates.
- **No circuit breaker** — clients keep retrying a downed service, preventing its recovery.

## Bundled Resources

- `references/error-taxonomy.md` — failure-mode checklist; transient vs permanent vs ambiguous classification with HTTP/DB/network specifics.
- `references/patterns-by-language.md` — idiomatic result/exception, retry, and timeout patterns in Python, TypeScript, Go, Rust, Java.
- `references/resilience-patterns.md` — deep dive on backoff math, circuit breakers, bulkheads, idempotency, deadlines, retry budgets, and how they compose.
- `scripts/retry.py` — runnable, stdlib-only retry (sync + async) with full-jitter backoff, retryable-error filtering, deadlines, and a circuit breaker.
- `examples/resilient-api-call.md` — full worked example: a flaky API client with timeout + retry + breaker + cache fallback, and how it behaves under each failure mode.
- `templates/error-handling-review.md` — fill-in checklist/template for reviewing a code change's error handling.
