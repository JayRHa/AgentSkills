# Error Handling Review — <component / PR / operation>

Reviewer: ____________   Date: ____________

Use this checklist when reviewing a change that performs network/DB/IO or any
failure-prone work. Mark each: ✅ pass / ⚠️ needs work / N/A.

## 1. Failure enumeration & classification
- [ ] All realistic failure modes enumerated (timeout, 4xx, 5xx, reset, malformed, partial)
- [ ] Each failure classified transient / permanent / ambiguous
- [ ] Programmer errors (bugs) are NOT caught-and-swallowed; they fail fast

## 2. Error signaling
- [ ] Consistent style per layer (exceptions OR result type, not mixed accidentally)
- [ ] No `null`/`-1`/`false`/empty-string used to silently mean "error"
- [ ] No bare `except:` / empty `catch {}` / ignored Promise rejections
- [ ] Errors wrapped with context AND original cause preserved (`from` / `cause` / `%w`)
- [ ] Caught exception types are specific, not blanket `Exception`/`Throwable`

## 3. Timeouts & deadlines
- [ ] Every remote/DB/IO call has an explicit timeout
- [ ] Connect and read timeouts set separately where applicable
- [ ] Deadline propagated across call chains (total latency bounded)
- [ ] Timeout values justified by latency data (not arbitrary)

## 4. Retries
- [ ] Only transient/retryable errors are retried (no 4xx, no validation)
- [ ] Only idempotent ops retried; non-idempotent writes use an idempotency key
- [ ] Exponential backoff WITH jitter (not fixed, not no-jitter)
- [ ] Bounded max attempts AND an absolute deadline
- [ ] Max delay capped; `Retry-After` honored
- [ ] Retries happen at one layer (no multiplicative nesting); retry budget considered

## 5. Circuit breaker / bulkhead (for bulk-failure-prone deps)
- [ ] Circuit breaker around the dependency (per-dependency, not global)
- [ ] Breaker counts timeouts/5xx, not client 4xx
- [ ] Bulkhead / concurrency limit prevents one slow dep exhausting the pool

## 6. Graceful degradation
- [ ] Degraded behavior defined for dependency-down (cache/default/queue/clean error)
- [ ] Non-critical dependency failure cannot break the critical path
- [ ] User sees a clean, actionable message — never a stack trace or hung spinner
- [ ] Ambiguous write failures reconciled or made idempotent (not assumed failed)

## 7. Resource cleanup
- [ ] Connections/files/locks released on every path (finally/defer/with/RAII)
- [ ] Cancellation handled (client disconnect / context cancelled)

## 8. Observability
- [ ] Each error logged once, at the boundary with full context (no double logging)
- [ ] Metrics: error rate by class, retry count, breaker state, timeout count
- [ ] Correlation/trace IDs present for cross-service debugging
- [ ] No sensitive data leaked in error messages/logs

## 9. Tests
- [ ] Failure paths tested: injected timeouts, 500s, connection drops
- [ ] Retry/backoff behavior verified (including exhaustion)
- [ ] Breaker trip + half-open recovery verified
- [ ] Fallback / degraded mode verified

## Findings

| # | Severity | Location | Issue | Suggested fix |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |

## Verdict
- [ ] Approve
- [ ] Approve with nits
- [ ] Request changes

Notes: ____________________________________________________________
