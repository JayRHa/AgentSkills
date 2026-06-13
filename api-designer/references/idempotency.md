# Idempotency & Concurrency

## Why
Networks fail mid-request. Clients retry. Without protection, a retried `POST /payments` can charge twice. Idempotency makes a retry a no-op that returns the original result.

## Idempotency Keys (for unsafe POSTs)
### Contract
- Client generates a unique key per logical operation (UUIDv4/ULID) and sends `Idempotency-Key: <key>`.
- Same key + same request → return the **original** response (replay).
- Same key + **different** request body → reject with `422`/`409` (`code: IDEMPOTENCY_KEY_REUSE`).
- Keys expire after a documented window (e.g., 24h).

### Server algorithm
1. On request, look up the key in a store (Redis/DB) scoped to the authenticated principal.
2. **Miss:** insert a row `(key, request_fingerprint, status=in_progress)` atomically. If insert loses a race, treat as hit.
3. Process the request; on completion store `(status=done, response_status, response_body)`.
4. **Hit + done:** return the stored response.
5. **Hit + in_progress:** return `409 Conflict` (`code: REQUEST_IN_PROGRESS`) — client should retry later.
6. **Hit but fingerprint differs:** return `422` `IDEMPOTENCY_KEY_REUSE`.

`request_fingerprint` = hash of (method, path, normalized body). Persist the response so replays are byte-identical.

### Which methods need keys?
- `GET`/`PUT`/`DELETE` are already idempotent by HTTP definition — no key needed.
- `POST` that creates or charges → use keys.
- `PATCH` that is not naturally idempotent → use keys or design it to be idempotent (set absolute values, not deltas).

## Optimistic Concurrency (lost-update prevention)
When two clients edit the same resource, the second write can silently clobber the first.

### ETag + If-Match flow
1. `GET /orders/42` → response includes `ETag: "v7"`.
2. Client edits, then `PUT/PATCH /orders/42` with `If-Match: "v7"`.
3. Server compares `If-Match` to current ETag:
   - Match → apply update, return new `ETag`.
   - Mismatch → `412 Precondition Failed` (`code: CONFLICT_VERSION`). Client re-fetches and retries.
4. Optionally require it: respond `428 Precondition Required` to writes without `If-Match`.

ETag can be a hash of the representation or a monotonic `version` integer.

## Exactly-once-ish processing for async work
True exactly-once delivery is impossible across a network; aim for **at-least-once delivery + idempotent consumers**:
- Give every message/event a unique id.
- Consumers dedupe by id before applying side effects.
- Make side effects idempotent (upserts keyed by business id).

## Webhooks (delivering events to clients)
- Include a unique `id` and `timestamp` per event; consumers dedupe.
- Sign payloads (HMAC) with a shared secret; clients verify before processing.
- Retry with exponential backoff on non-2xx; document the retry schedule.
- Provide an endpoint to replay/list recent events.
