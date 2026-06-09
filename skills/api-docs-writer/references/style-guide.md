# API Docs Style Guide

Conventions for human-readable API reference docs. Load when writing Markdown reference pages or example payloads.

## Voice and tense
- Second person, present tense: "Returns the user." / "Send the token in the Authorization header."
- Imperative for summaries: "Create a user", "List invoices", "Delete a webhook".
- Describe what the API *does*, not what the client "should" feel.

## Summaries vs descriptions
- **Summary**: one line, imperative, < 60 chars. Used in nav and tables.
- **Description**: behavior, side effects, constraints, when to use, edge cases.

## Naming
- Endpoint titles: `METHOD /resource/{id}` in code font.
- Field names, headers, status codes, and values in `code font`.
- Use the API's actual casing for fields (`createdAt` vs `created_at`) — match the wire format exactly.

## Examples
- Always realistic. Use plausible names, ids, emails, timestamps.
  - Good: `"id": "usr_8f2c1a"`, `"email": "ada@example.com"`, `"createdAt": "2026-02-14T09:30:00Z"`.
  - Bad: `"id": "string"`, `"email": "foo@bar"`, `"x": 123`.
- Prefix ids with a type tag when the API does (`usr_`, `inv_`, `evt_`).
- Timestamps: ISO-8601 UTC with `Z`. State the timezone if not UTC.
- Money: integer minor units (cents) unless the API uses decimals; always state the unit and currency.
- Mask secrets: `Authorization: Bearer sk_test_4eC39H...` — show the prefix, truncate the rest.

## curl examples
Use a consistent shape:

```bash
curl https://api.acme.com/v1/users/usr_8f2c1a \
  -H "Authorization: Bearer $ACME_API_KEY" \
  -H "Content-Type: application/json"
```

- Reference an env var for the token, never a literal secret.
- Show `-X POST` and `-d` for write operations; long single-quoted JSON for `-d`.
- Put the base URL first so the example is copy-pasteable.

## Multi-language samples
When including SDK samples, keep them parallel (same operation, same values) across languages. Order: curl, then JS/TS, then Python, then others.

## Tables
- Parameter columns, always in this order: Name, In, Type, Required, Default, Constraints, Description.
- Error columns: Status, Code, When it happens, Resolution.
- Keep cells terse; move long prose to the description body.

## Units and constraints — always state
- Pagination limits (min/max/default).
- Rate limits (requests per window) and the reset header.
- String length and pattern constraints.
- Enum allowed values (list them all).
- Nullability and default values.

## Deprecation
Mark with a clear note: what is deprecated, since which version, the replacement, and the removal date if known.

```
> Deprecated since v1.3. Use `displayName` instead. Removed in v2.0.
```

## Cross-cutting sections (write once, link everywhere)
- Authentication
- Pagination
- Rate limiting
- Versioning
- Errors
- Idempotency
