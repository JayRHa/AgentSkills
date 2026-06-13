# Error Taxonomy and Failure-Mode Checklist

Classify every possible failure into one of three buckets. The bucket determines the reaction.

## The Three Buckets

| Bucket | Meaning | Default reaction |
|---|---|---|
| **Transient** | Temporary; a retry has a real chance of success | Retry with backoff + jitter, bounded |
| **Permanent** | Will not succeed on retry; the request itself is wrong or the resource is gone | Fail fast; surface clear, actionable error |
| **Ambiguous** | Outcome unknown — the operation may or may not have applied | Retry only if idempotent; otherwise reconcile/alert |

## Operational vs Programmer Errors

Orthogonal but critical distinction:

- **Operational errors** — expected runtime conditions of a healthy program: network timeout, 503, file not found, invalid user input, rate limit. **Handle these.**
- **Programmer errors (bugs)** — violated invariants: null dereference, calling with wrong type, index out of bounds, unreachable branch hit. **Do not "handle" these — fail fast and fix the code.** Catching them broadly hides corruption.

Rule: recover from operational errors; crash loudly on programmer errors.

## Failure-Mode Checklist (per remote/IO operation)

Walk this list for every call that crosses a boundary:

- [ ] Connection refused / host unreachable / DNS failure
- [ ] Connect timeout (couldn't establish socket)
- [ ] Read/request timeout (no response in time)
- [ ] Connection reset mid-stream
- [ ] TLS / certificate error
- [ ] Auth failure / token expired mid-request
- [ ] Rate limited (429) — honor `Retry-After`
- [ ] Server error 500 / 502 / 503 / 504
- [ ] Client error 400 / 401 / 403 / 404 / 409 / 422
- [ ] Malformed / unparseable response body
- [ ] Schema/contract mismatch (missing field, wrong type)
- [ ] Partial response / truncated stream
- [ ] Empty result vs error (is "not found" an error?)
- [ ] Duplicate delivery (at-least-once queues)
- [ ] Out-of-order delivery
- [ ] Disk full / quota exceeded / out of memory
- [ ] Deadlock / lock timeout (DB)
- [ ] Constraint violation (unique, FK)
- [ ] Serialization failure / write conflict (DB)
- [ ] Cancellation (client disconnected, context cancelled)

## HTTP Status Classification

| Status | Class | Retryable? | Notes |
|---|---|---|---|
| 400 Bad Request | Permanent | No | Fix the request |
| 401 Unauthorized | Permanent | No* | Re-auth then retry once if token expired |
| 403 Forbidden | Permanent | No | Authorization issue |
| 404 Not Found | Permanent | No | Resource absent (often not an "error") |
| 408 Request Timeout | Transient | Yes | |
| 409 Conflict | Permanent | Usually no | May need reconcile/re-read |
| 422 Unprocessable | Permanent | No | Validation failure |
| 429 Too Many Requests | Transient | Yes | Honor `Retry-After`; back off hard |
| 500 Internal Error | Transient | Cautiously | Often retryable; may be non-idempotent server bug |
| 502 Bad Gateway | Transient | Yes | |
| 503 Service Unavailable | Transient | Yes | Honor `Retry-After` |
| 504 Gateway Timeout | Transient/Ambiguous | Yes if idempotent | Upstream may have applied the write |

*401: retry only after refreshing credentials, and only once, to avoid lockout loops.

## Database Error Classification

| Condition | Class | Action |
|---|---|---|
| Connection lost / pool timeout | Transient | Retry with backoff |
| Lock wait timeout | Transient | Retry (with jitter to avoid re-collision) |
| Deadlock detected | Transient | Retry the whole transaction |
| Serialization failure (SERIALIZABLE/REPEATABLE READ) | Transient | Retry the transaction |
| Unique constraint violation | Permanent | Surface as conflict; may indicate idempotent re-insert |
| Foreign key violation | Permanent | Caller bug or missing parent |
| Query syntax / undefined column | Programmer error | Fix code; do not retry |
| Disk full | Permanent (until ops fix) | Alert; fail fast |

## Network Error Classification (sockets)

| Error | Class | Notes |
|---|---|---|
| `ECONNREFUSED` | Transient | Service down/restarting; back off |
| `ECONNRESET` | Transient/Ambiguous | Mid-flight reset; write may have applied |
| `ETIMEDOUT` | Transient/Ambiguous | For writes, treat as ambiguous |
| `EHOSTUNREACH` / `ENETUNREACH` | Transient | Routing/transient infra |
| DNS `ENOTFOUND` | Often permanent | Config error vs transient resolver blip |
| `EPIPE` | Transient/Ambiguous | Peer closed connection |

## The Ambiguous Case (read this twice)

A timeout or connection reset on a **write** means you do **not** know whether it applied. Options:

1. **Make it idempotent** (idempotency key / conditional write) so a retry is safe — preferred.
2. **Reconcile**: query the resource to determine the actual state before acting.
3. **Fail and alert** if neither is possible; never blindly retry a non-idempotent write.

Never assume an ambiguous write failed. "Card declined" UX after a successful charge is exactly this bug.
