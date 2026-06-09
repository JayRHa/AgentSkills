# Worked Example: Orders REST API

A small but realistic walkthrough applying the workflow end to end.

## 1. Resources
Domain nouns: `Order`, `OrderItem` (owned by Order), `Customer`. Orders belong to a customer; items belong to an order.

## 2. Representation
```json
{
  "id": "ord_01HZX...",
  "customerId": "cus_01HZ...",
  "status": "pending",
  "items": [{ "sku": "BOOK-42", "quantity": 2 }],
  "total": { "currency": "USD", "amountMinor": 5980 },
  "createdAt": "2026-06-08T10:00:00Z",
  "updatedAt": "2026-06-08T10:00:00Z"
}
```
`id`, `createdAt`, `updatedAt`, `total` are read-only (server-computed). IDs are opaque ULIDs.

## 3. Operations -> HTTP
| Action | Method + Path |
|--------|---------------|
| List orders | `GET /v1/orders?limit=50&status=pending` |
| Create order | `POST /v1/orders` (+ `Idempotency-Key`) |
| Get order | `GET /v1/orders/{id}` |
| Update status | `PATCH /v1/orders/{id}` (+ `If-Match`) |
| Cancel order | `POST /v1/orders/{id}/cancel` (controller for a non-trivial state transition with side effects) |
| Delete (soft) | `DELETE /v1/orders/{id}` |

Note: `cancel` triggers refunds and inventory release, so it's an explicit controller rather than a bare `PATCH status=cancelled`.

## 4. Create — request/response
Request:
```http
POST /v1/orders HTTP/1.1
Content-Type: application/json
Idempotency-Key: 7f1c2b9e-...
Authorization: Bearer <token>

{ "customerId": "cus_01HZ...", "items": [{ "sku": "BOOK-42", "quantity": 2 }] }
```
Response:
```http
HTTP/1.1 201 Created
Location: /v1/orders/ord_01HZX...
ETag: "v1"
Content-Type: application/json

{ "id": "ord_01HZX...", "status": "pending", ... }
```
Replaying the same `Idempotency-Key` with the same body returns the identical `201` — no duplicate order.

## 5. List with cursor pagination
```http
GET /v1/orders?limit=2&sort=-createdAt HTTP/1.1
```
```json
{
  "data": [ { "id": "ord_b" }, { "id": "ord_a" } ],
  "page": { "nextCursor": "eyJjcmVhdGVkQXQiOiI...", "hasMore": true }
}
```
Next page: `GET /v1/orders?limit=2&cursor=eyJjcmVhdGVkQXQiOiI...`.

## 6. Optimistic update
```http
PATCH /v1/orders/ord_01HZX... HTTP/1.1
If-Match: "v1"
Content-Type: application/merge-patch+json

{ "status": "paid" }
```
If the order changed since `v1` was fetched:
```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/problem+json

{ "type": "https://api.example.com/problems/version-conflict",
  "title": "Order was modified", "status": 412, "code": "CONFLICT_VERSION" }
```

## 7. Validation error
```http
POST /v1/orders  (quantity 0)
```
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Your request body was invalid",
  "status": 422,
  "code": "VALIDATION_ERROR",
  "errors": [ { "field": "items[0].quantity", "code": "MIN", "detail": "Must be >= 1." } ]
}
```

## 8. Outcome
The result: consistent envelope, RFC 9457 errors, cursor pagination, idempotent creation, optimistic concurrency, URL versioning. The OpenAPI in `templates/openapi-3.1-template.yaml` is the source of truth and is linted in CI.
