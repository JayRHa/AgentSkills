# HTTP Semantics Reference

## Method Properties
| Method | Safe | Idempotent | Cacheable | Typical use |
|--------|------|-----------|-----------|-------------|
| GET    | yes  | yes       | yes       | Read a resource/collection |
| HEAD   | yes  | yes       | yes       | Metadata/existence check |
| OPTIONS| yes  | yes       | no        | Capabilities / CORS preflight |
| POST   | no   | no        | rarely    | Create, non-idempotent actions |
| PUT    | no   | yes       | no        | Full replace / create-at-known-URI |
| PATCH  | no   | no*       | no        | Partial update (*can be made idempotent) |
| DELETE | no   | yes       | no        | Remove a resource |

Safe = no intended side effects. Idempotent = N identical requests have the same effect as one.

## Status Code Map
### 2xx Success
- `200 OK` — request succeeded, body returned.
- `201 Created` — resource created; include `Location` header pointing to it.
- `202 Accepted` — accepted for async processing; return a status resource URL.
- `204 No Content` — success, no body (DELETE, empty PUT/PATCH).

### 3xx Redirection / Conditional
- `301`/`308` — permanent move (`308` preserves method).
- `302`/`307` — temporary (`307` preserves method).
- `304 Not Modified` — conditional GET with `If-None-Match`/`If-Modified-Since` matched.

### 4xx Client Errors
- `400 Bad Request` — malformed syntax / unparseable.
- `401 Unauthorized` — missing/invalid authentication. Send `WWW-Authenticate`.
- `403 Forbidden` — authenticated but not permitted.
- `404 Not Found` — resource does not exist (or hidden for privacy).
- `405 Method Not Allowed` — include `Allow` header.
- `406 Not Acceptable` — cannot satisfy `Accept`.
- `409 Conflict` — state conflict (duplicate, version mismatch).
- `410 Gone` — resource permanently removed (use for sunset endpoints).
- `412 Precondition Failed` — `If-Match`/`If-Unmodified-Since` failed.
- `415 Unsupported Media Type` — bad `Content-Type`.
- `422 Unprocessable Entity` — syntactically valid but semantically invalid.
- `428 Precondition Required` — demand conditional requests (force `If-Match`).
- `429 Too Many Requests` — rate limited; include `Retry-After`.

### 5xx Server Errors
- `500 Internal Server Error` — unexpected failure.
- `502 Bad Gateway` / `503 Service Unavailable` (+`Retry-After`) / `504 Gateway Timeout`.

## 400 vs 422 vs 409
- `400` — can't parse the request at all (broken JSON, wrong content type).
- `422` — parsed fine, but values are invalid (negative age, unknown enum, failed business rule on input).
- `409` — request is valid but conflicts with current server state (email already taken, stale version).

## Key Headers
### Caching & Conditional Requests
- `Cache-Control: max-age=..., private|public, no-store` — caching policy.
- `ETag: "<hash>"` — version identifier of the representation.
- `If-None-Match: "<etag>"` — conditional GET → `304` if unchanged.
- `If-Match: "<etag>"` — conditional write → `412` if changed (optimistic locking).
- `Last-Modified` / `If-Modified-Since` — timestamp-based alternative to ETag.
- `Vary` — which request headers affect the response (e.g., `Accept`, `Authorization`).

### Content Negotiation
- `Accept` / `Content-Type` — media types (`application/json`, `application/problem+json`).
- `Accept-Language`, `Content-Language`.

### Rate Limiting (use the IETF `RateLimit` fields and/or `X-RateLimit-*`)
- `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`.
- `Retry-After: <seconds|http-date>` on `429`/`503`.

### Reliability
- `Idempotency-Key: <client-uuid>` — dedupe retried POSTs.
- `Location` — created/redirected resource URL.

## Content Types
- Default to `application/json`.
- Errors: `application/problem+json` (RFC 9457).
- Use `application/merge-patch+json` (RFC 7386) or `application/json-patch+json` (RFC 6902) to make PATCH semantics explicit.
