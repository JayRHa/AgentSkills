# REST API Design Review Checklist

Use this when designing or reviewing a REST API. Each item is a yes/no gate.

## Resource Modeling
- [ ] Resources are nouns; URLs contain no verbs.
- [ ] Collections are plural (`/orders`), members are `/orders/{id}`.
- [ ] Identifiers are opaque strings (UUID/ULID/slug), not leaked DB auto-increment IDs.
- [ ] Nesting is at most one level deep; deeper relations use filters/links.
- [ ] Non-CRUD actions modeled as state changes (`PATCH`) or explicit sub-resources (`POST /orders/{id}/cancel`).
- [ ] Field naming casing is consistent across the whole API (all camelCase OR all snake_case).

## HTTP Semantics
- [ ] `GET` is safe and has no side effects.
- [ ] `PUT` replaces, `PATCH` partially updates, both idempotent.
- [ ] `POST` used for non-idempotent creation/actions.
- [ ] `DELETE` is idempotent (second delete returns `204` or `404`, documented).
- [ ] `201 Created` responses include a `Location` header.
- [ ] Correct status codes for auth (`401` vs `403`) and validation (`400` vs `422`).
- [ ] No `200 OK` with an error payload anywhere.

## Representations
- [ ] Request and response schemas are documented per endpoint.
- [ ] Read-only fields (e.g., `id`, `createdAt`) cannot be set on write and are ignored or rejected.
- [ ] Timestamps are UTC ISO-8601 with offset.
- [ ] Money uses explicit currency code + integer minor units (or documented decimal string).
- [ ] Enums are documented and stable; unknown enum values handled gracefully by clients.
- [ ] Null vs absent semantics are defined for PATCH.

## Lists
- [ ] Every collection endpoint is paginated with an enforced max limit.
- [ ] Pagination style chosen deliberately (cursor preferred) and documented.
- [ ] Default and allowed `sort` fields documented; sort is deterministic.
- [ ] Filtering params are explicit and validated; unknown params rejected or ignored consistently.
- [ ] Consistent response envelope (`data` + `page`/`meta`).

## Errors
- [ ] Single error shape across all endpoints (RFC 9457 Problem Details recommended).
- [ ] Stable machine-readable error `type`/`code` in addition to human `detail`.
- [ ] Field-level validation errors include pointers to offending fields.
- [ ] No stack traces, SQL, or internal hostnames leaked.

## Reliability
- [ ] Retry-safe POSTs accept `Idempotency-Key`.
- [ ] Optimistic concurrency via `ETag` + `If-Match` where lost updates matter.
- [ ] Long operations return `202 Accepted` with a status resource to poll, or a webhook.

## Cross-Cutting
- [ ] AuthN scheme defined (OAuth2/OIDC bearer, API key) and documented.
- [ ] AuthZ rules defined per endpoint; least privilege.
- [ ] Rate limits enforced; `RateLimit`/`X-RateLimit-*` + `Retry-After` returned.
- [ ] Versioning strategy chosen; breaking-change + deprecation policy written.
- [ ] CORS policy explicit for browser clients.
- [ ] Pagination, filtering, and errors are consistent with the rest of the org's APIs.

## Contract & Tooling
- [ ] OpenAPI 3.1 spec exists and is the source of truth.
- [ ] Examples included for each request/response and error.
- [ ] Spec passes lint (`scripts/lint_openapi.py`) and CI contract tests.
