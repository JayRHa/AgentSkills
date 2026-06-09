---
name: api-docs-writer
description: Writes precise, complete reference documentation for HTTP/REST APIs and authors valid OpenAPI 3.1 specifications, including endpoint pages, request/response schemas, parameter tables, authentication, pagination, code samples, and error tables. Use this skill when the user asks to "document an API", "write API reference docs", "create an OpenAPI/Swagger spec", "document these endpoints", "write a REST API reference", "add request/response examples", "document error codes", "describe API parameters", or convert code/routes into API documentation.
license: MIT
---

# API Docs Writer

## Overview
This skill produces production-quality API reference documentation and OpenAPI 3.1 specifications. It covers endpoint reference pages, parameter/field tables, authentication, pagination, rate limits, request/response examples in multiple languages, and complete error tables.

Keywords: API documentation, REST reference, OpenAPI, Swagger, endpoint docs, request schema, response schema, error codes, curl example, parameter table, authentication docs.

Use it for two distinct deliverables:
1. **Human-readable reference docs** (Markdown) — one page per resource or endpoint.
2. **Machine-readable OpenAPI 3.1 spec** (YAML/JSON) — the single source of truth for tooling, SDK generation, and doc portals.

Prefer generating the OpenAPI spec first, then deriving Markdown from it, when both are requested.

## Process
Follow these steps in order.

1. **Gather the source of truth.** Identify where the API behavior is defined: route handlers, controllers, framework decorators (Flask/FastAPI/Express/Spring), existing partial specs, Postman collections, or live responses. Never invent fields — read the code or ask. If a detail is unknown, mark it clearly rather than guessing.

2. **Inventory the surface.** For each endpoint capture: HTTP method, path (with `{path_params}`), summary, auth requirement, query/path/header params, request body schema, success responses (per status code), error responses, and idempotency. Use `references/extraction-checklist.md` to avoid omissions.

3. **Choose the deliverable.** If the user wants a spec, scaffold OpenAPI 3.1 (see `references/openapi-3.1-reference.md` and `templates/openapi-skeleton.yaml`). If they want a reference page, use `templates/endpoint-reference.md`.

4. **Document each endpoint.** Write the summary (imperative, one line), description (behavior, side effects, constraints), parameter tables, request body, and responses. Every parameter row must state: name, in (path/query/header/cookie), type, required, default, constraints, description.

5. **Add examples.** Provide at least a `curl` example and one realistic JSON request/response pair per endpoint. Use real-looking values, never `foo`/`bar`. Show the exact status code. See `references/style-guide.md` for example conventions.

6. **Document errors.** Build a per-endpoint error table AND a global error reference. Each row: HTTP status, machine-readable `code`, when it occurs, and how to fix. Reuse a consistent error envelope.

7. **Document cross-cutting concerns.** Authentication, pagination, rate limiting, versioning, idempotency keys, and content types. Document these once in shared sections and link to them.

8. **Validate.** If you produced an OpenAPI file, run `scripts/validate_openapi.py path/to/spec.yaml` to catch structural errors before delivering. Fix every reported issue.

9. **Self-review** against `references/extraction-checklist.md` and the Common Pitfalls list below.

## Endpoint documentation structure
Each endpoint page should contain, in order:
- Title: `METHOD /path`
- One-line summary + auth badge (e.g. `Requires: Bearer token`)
- Description (behavior, side effects, when to use)
- Path parameters table
- Query parameters table
- Request headers table (only non-standard ones)
- Request body: schema table + example
- Responses: one block per status code with schema + example
- Errors: table specific to this endpoint
- Code samples (curl + at least one SDK/language)

## Parameter table format
Always use this column order:

| Name | In | Type | Required | Default | Constraints | Description |
|------|----|----- |----------|---------|-------------|-------------|
| `limit` | query | integer | No | 20 | 1–100 | Max items per page. |

## Error envelope (recommended default)
Use a single consistent shape unless the API dictates otherwise:

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "No user exists with id 'usr_123'.",
    "details": [],
    "request_id": "req_8f2c1a"
  }
}
```

Document the envelope once, then reference it from each error table.

## Best Practices
- Document the actual behavior, not the intended behavior — verify against code or live calls.
- Use stable, machine-readable error `code` strings; HTTP status alone is not enough.
- Make every example copy-paste runnable. Include the base URL and a placeholder token format like `Bearer sk_test_...`.
- Reuse schemas via `$ref` / `components.schemas` in OpenAPI; never copy a schema twice.
- Show pagination with a concrete example of fetching page 2.
- State default values, units (ms, bytes, ISO-8601), and timezones explicitly.
- Mark deprecated fields/endpoints with the reason and the replacement.
- Keep summaries imperative and under ~60 chars; put detail in the description.
- Document idempotency and side effects for every non-GET endpoint.

## Common Pitfalls
- Inventing fields or status codes that the code does not produce.
- Missing the error responses (only documenting the happy path).
- Forgetting `required` vs optional, or omitting defaults.
- Using `foo`/`bar`/`string` placeholders instead of realistic values.
- Mixing `200` and `201` without saying which operation returns which.
- OpenAPI: putting examples in the wrong place, missing `requestBody.required`, or referencing undefined `$ref`s.
- Not specifying the content type (`application/json` vs `multipart/form-data`).
- Documenting auth in each endpoint instead of one shared section + per-endpoint badge.

## Supporting files
- `references/openapi-3.1-reference.md` — OpenAPI 3.1 structure, field semantics, schema patterns, security schemes, and reusable components.
- `references/style-guide.md` — voice, examples, naming, and formatting conventions.
- `references/extraction-checklist.md` — what to capture per endpoint; use as a final review gate.
- `templates/endpoint-reference.md` — fill-in Markdown template for one endpoint.
- `templates/openapi-skeleton.yaml` — minimal valid OpenAPI 3.1 starting point.
- `scripts/validate_openapi.py` — stdlib validator for common OpenAPI mistakes.
- `examples/users-api.md` — a complete worked example (input routes -> reference page + spec excerpt).
