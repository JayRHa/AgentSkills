# Error Design — RFC 9457 Problem Details

Adopt one consistent error shape across every endpoint. RFC 9457 (obsoletes 7807) defines a standard JSON body served as `application/problem+json`.

## Standard Members
| Field | Meaning |
|-------|---------|
| `type` | URI identifying the problem type (stable, dereferenceable docs). Defaults to `about:blank`. |
| `title` | Short, human-readable summary, stable per `type`. |
| `status` | HTTP status code, duplicated for convenience. |
| `detail` | Human-readable explanation specific to this occurrence. |
| `instance` | URI identifying this specific occurrence (e.g., request id path). |

You may add extension members (e.g., `errors`, `code`, `traceId`).

## Basic Example
```json
{
  "type": "https://api.example.com/problems/insufficient-funds",
  "title": "Insufficient funds",
  "status": 422,
  "detail": "Your balance is 30 but the charge is 50.",
  "instance": "/transactions/abc123",
  "code": "INSUFFICIENT_FUNDS",
  "traceId": "7b3f..."
}
```
Response header: `Content-Type: application/problem+json`.

## Validation Errors (field-level)
Add an `errors` array with machine-usable pointers.
```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Your request body was invalid",
  "status": 422,
  "code": "VALIDATION_ERROR",
  "errors": [
    { "field": "email", "code": "FORMAT", "detail": "Must be a valid email." },
    { "field": "items[0].quantity", "code": "MIN", "detail": "Must be >= 1." }
  ]
}
```
Use JSON Pointer (`/items/0/quantity`) or dotted paths — pick one and be consistent.

## Rules
1. **One shape everywhere.** Clients write one error handler.
2. **Stable machine code.** `type` URI and/or `code` must never change meaning; use them for programmatic branching. Free-text `detail`/`title` may be localized or reworded.
3. **Right status code.** The body never substitutes for the status line. See `http-semantics.md` (400 vs 422 vs 409).
4. **Never leak internals.** No stack traces, SQL, file paths, or hostnames. Include a `traceId` so support can correlate logs.
5. **Be actionable.** `detail` should tell the caller how to fix it when possible.
6. **Don't enumerate secrets.** For auth, prefer generic messages (avoid revealing whether an account exists).

## Catalog Your Error Types
Maintain a registry table so codes are reused, not reinvented:
| code | http | type URI | when |
|------|------|----------|------|
| `VALIDATION_ERROR` | 422 | /problems/validation-error | body fails validation |
| `NOT_FOUND` | 404 | /problems/not-found | resource missing |
| `CONFLICT_VERSION` | 409 | /problems/version-conflict | ETag/If-Match mismatch |
| `RATE_LIMITED` | 429 | /problems/rate-limited | quota exceeded |
| `UNAUTHENTICATED` | 401 | /problems/unauthenticated | missing/bad credentials |
| `FORBIDDEN` | 403 | /problems/forbidden | not permitted |

## GraphQL Note
GraphQL returns `200` with a top-level `errors` array for protocol/system errors; put a stable `extensions.code` on each. Expected business errors should be modeled as typed fields in the mutation payload (`userErrors`) rather than thrown.
