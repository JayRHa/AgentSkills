# Versioning & Evolution

## Strategies
| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URI path (recommended for public) | `/v1/orders` | Visible, cache-friendly, trivial routing | Couples version to URL; coarse (whole API) |
| Custom header | `API-Version: 2026-06-01` | Clean URLs, fine-grained | Invisible, easy to forget, harder to cache |
| Media type | `Accept: application/vnd.acme.v2+json` | RESTful, per-resource | Tooling friction, less discoverable |
| Query param | `?version=2` | Easy to try | Pollutes caching, easy to omit |

Default recommendation: **major version in the URL path** (`/v1`), plus a date-based `API-Version` header for fine-grained behavior flags if you need them (the "date-versioned" model). Keep a single major version live as long as possible by making changes additively.

## Breaking vs Non-Breaking
### Non-breaking (no version bump needed)
- Adding a new endpoint.
- Adding a new **optional** request field.
- Adding a new field to a response (clients must ignore unknown fields).
- Adding a new optional query parameter.
- Adding a new value to an enum **only if** clients are documented to tolerate unknown values.
- Loosening a validation constraint.

### Breaking (requires a new major version)
- Removing or renaming a field/endpoint/parameter.
- Changing a field's type, format, or units.
- Making an optional request field required, or tightening validation.
- Changing default behavior, sort order, or pagination semantics.
- Changing error codes/status for an existing condition.
- Changing authentication/authorization requirements.

## Deprecation Policy (publish it)
1. Announce in changelog + docs with a migration guide.
2. Emit `Deprecation: true` (or a date) and `Sunset: <http-date>` response headers (RFC 8594).
3. Optionally add a `Link: <...>; rel="deprecation"` to docs.
4. Provide a generous window (e.g., 6–12 months for public APIs).
5. After sunset, return `410 Gone` (not `404`) so callers know it existed and is intentionally removed.
6. Track usage by client before removal; proactively contact heavy users.

## Consumer-Driven Compatibility
- Treat the OpenAPI/SDL as a contract; run contract tests in CI.
- Use schema diff tooling to flag breaking changes automatically on every PR.
- Clients should be tolerant readers: ignore unknown fields, don't assume field order, handle new enum values defensively.
