# Endpoint Extraction Checklist

Use this when reading source code/routes to document an API, and again as a final review gate. Every endpoint must satisfy every applicable item.

## Per endpoint
- [ ] HTTP method and full path captured (with `{path_params}`).
- [ ] One-line imperative summary written.
- [ ] Description covers behavior, side effects, and constraints.
- [ ] Auth requirement stated (which scheme, which scopes/roles, or public).
- [ ] Path parameters: every one documented with type + constraints.
- [ ] Query parameters: name, type, required, default, constraints, description.
- [ ] Required request headers documented (skip standard ones).
- [ ] Request body: content type, schema, required vs optional fields, example.
- [ ] Success responses: one per status code (200 vs 201 vs 204) with schema + example.
- [ ] Response headers documented if non-standard (Location, X-RateLimit-*, pagination).
- [ ] Error responses: status, machine code, cause, resolution.
- [ ] At least one runnable example (curl) with realistic values.
- [ ] Idempotency / side effects noted for non-GET.
- [ ] Pagination behavior documented for list endpoints.

## Where to find each detail (by framework)

| Detail | FastAPI | Flask | Express | Spring |
|--------|---------|-------|---------|--------|
| Path + method | `@app.get("/x")` | `@app.route("/x", methods=[...])` | `app.get('/x', ...)` | `@GetMapping("/x")` |
| Path params | function args / `Path()` | `<int:id>` in route | `req.params` | `@PathVariable` |
| Query params | `Query()` defaults | `request.args.get` | `req.query` | `@RequestParam` |
| Body schema | Pydantic model | manual `request.json` | body parser / zod | `@RequestBody` DTO |
| Auth | `Depends(get_user)` | decorators / before_request | middleware | `@PreAuthorize` |
| Status codes | `status_code=` / raises | `return ..., 201` | `res.status(201)` | `ResponseEntity` |
| Errors | `HTTPException` | `abort()` | thrown errors / next(err) | `@ExceptionHandler` |

## Cross-cutting (document once for the whole API)
- [ ] Base URL(s) / servers (prod + sandbox).
- [ ] Authentication scheme(s) and how to obtain credentials.
- [ ] Token/header format and where it goes.
- [ ] Pagination model (cursor vs offset) with a worked example.
- [ ] Rate limits and the headers that report them.
- [ ] Versioning strategy (URL path, header, or query).
- [ ] Standard error envelope shape.
- [ ] Global error code table.
- [ ] Content types accepted and returned.
- [ ] Idempotency-Key support for retries.

## Final quality gate
- [ ] No placeholder values (`foo`, `string`, `123`) in examples.
- [ ] Every `$ref` resolves (run scripts/validate_openapi.py).
- [ ] Defaults and units stated everywhere.
- [ ] Happy path AND error path both documented.
- [ ] Summaries imperative and short.
