---
name: json-schema-author
description: Authors and validates JSON Schema (Draft 2020-12 and Draft-07) for configuration files and HTTP/REST APIs, applying types, constraints, composition keywords, and human-readable error messaging. Use this skill when the user wants to write, fix, refactor, or validate a JSON Schema, define a config-file contract, document request/response payloads, add validation rules to an OpenAPI spec, generate schemas from sample JSON, or produce clear validation error messages.
license: MIT
---

# JSON Schema Author

## Overview
Keywords: JSON Schema, Draft 2020-12, Draft-07, $schema, $ref, $defs, validation, config schema, API schema, OpenAPI, additionalProperties, oneOf, anyOf, allOf, if/then/else, format, pattern, const, enum, error messages, ajv, jsonschema.

This skill helps you design correct, strict, and maintainable JSON Schemas for two dominant use cases: **configuration files** (validate user/operator input, fail fast with helpful messages) and **APIs** (contract for request/response bodies, often embedded in OpenAPI). It covers the type system, every important constraint keyword, schema composition, reuse via `$ref`/`$defs`, conditional validation, and turning raw validator output into actionable error messages.

Use the bundled material:
- `references/keywords.md` — complete keyword reference (types, constraints, composition, applicators, annotations, draft differences) with copy-paste snippets.
- `references/error-messages.md` — patterns for clear, user-facing validation errors and how to map validator output to them.
- `templates/config-schema.json` — a strict, annotated starting point for a config-file schema.
- `templates/api-schema.json` — request/response schema pattern suitable for OpenAPI `components.schemas`.
- `scripts/validate.py` — stdlib-only structural linter that flags the most common schema authoring mistakes; falls back to `jsonschema` if installed for real validation.
- `examples/config-walkthrough.md` — sample config JSON turned into a finished schema with passing and failing instances.

## Workflow

1. **Pick the draft.** Default to **Draft 2020-12** for new schemas (`$schema: "https://json-schema.org/draft/2020-12/schema"`). Use **Draft-07** when targeting tooling that lags (older `ajv` configs, many OpenAPI 3.0 toolchains). OpenAPI 3.1 aligns with 2020-12. Note the differences: 2020-12 uses `$defs` and `prefixItems`/`items`; Draft-07 uses `definitions` and `items` (array)/`additionalItems`. See `references/keywords.md`.

2. **Identify the root type and intent.** Is this a config object, an API request, an API response, or a reusable component? Decide whether unknown keys are errors (config → almost always `"additionalProperties": false`) or tolerated (forward-compatible APIs may allow them).

3. **Model the shape.** Define `type`, then `properties`, then `required`. List every known property. Add a one-line `description` and a realistic `examples`/`default` where it aids users and generated docs.

4. **Add constraints, narrowest first.** Apply `enum`/`const`, numeric bounds (`minimum`, `maximum`, `exclusiveMinimum`, `multipleOf`), string rules (`minLength`, `maxLength`, `pattern`, `format`), and array/object cardinality (`minItems`, `uniqueItems`, `minProperties`). Prefer `enum` over free-form strings when the value set is closed.

5. **Compose and reuse.** Extract repeated shapes into `$defs` and reference with `$ref`. Use `allOf` to combine/extend, `oneOf` for mutually-exclusive variants (tagged unions), `anyOf` for "at least one", and `if/then/else` for conditional requirements. Avoid `oneOf` when only one branch can plausibly match — prefer a discriminator pattern (see `references/keywords.md`).

6. **Lock it down.** Set `additionalProperties: false` for configs and internal APIs. For arrays, decide `additionalItems`/`items: false` if a tuple. Mark deprecated fields with `deprecated: true`.

7. **Write good error messaging.** Decide between validator-native errors and curated messages. Add `title`/`description` and, where supported, `errorMessage` (ajv-errors) or a post-processing map. Follow `references/error-messages.md`.

8. **Validate against real instances.** Run `scripts/validate.py` to lint the schema structure, then validate at least one passing and several failing instances (one per constraint). Never ship a schema without a failing-case test.

## Decision framework: choosing composition keywords

| Need | Keyword | Notes |
|------|---------|-------|
| Exactly one of several variants | `oneOf` | Validation fails if zero or 2+ match. Add a discriminating `const` per branch. |
| At least one variant (overlap OK) | `anyOf` | Cheaper, clearer than `oneOf` when overlap is allowed. |
| Combine constraints (extend a base) | `allOf` | All subschemas must pass. Beware `additionalProperties` interactions. |
| Required field depends on another field's value | `if`/`then`/`else` | e.g. if `type=="ssl"` then `cert` is required. |
| Field A requires field B present | `dependentRequired` | Simple co-presence rules. |
| Closed value set | `enum` / `const` | `const` for single value; `enum` for a list. |

Critical gotcha: `additionalProperties: false` only sees properties declared in the **same** schema object, not those introduced by `allOf`/`$ref` siblings. To extend strictly, either declare all properties locally or use `unevaluatedProperties: false` (Draft 2019-09+/2020-12). See `references/keywords.md`.

## Worked example (tagged union)

A notification config where the payload depends on `channel`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["channel"],
  "properties": { "channel": { "enum": ["email", "sms"] } },
  "oneOf": [
    {
      "properties": {
        "channel": { "const": "email" },
        "to": { "type": "string", "format": "email" }
      },
      "required": ["to"]
    },
    {
      "properties": {
        "channel": { "const": "sms" },
        "to": { "type": "string", "pattern": "^\\+[1-9]\\d{6,14}$" }
      },
      "required": ["to"]
    }
  ],
  "unevaluatedProperties": false
}
```

Each branch pins `channel` with `const`, so exactly one branch can match — clean error attribution. See `examples/config-walkthrough.md` for a full multi-property example.

## Best Practices
- **Always declare `$schema`.** It tells validators and humans the dialect.
- **Be strict by default.** `additionalProperties: false` for configs; require what's mandatory. Loosen deliberately, not accidentally.
- **One source of truth per shape.** Factor repeated structures into `$defs` and `$ref` them.
- **Constrain values, not just types.** A `"type": "string"` port number is a bug; use `"type": "integer", "minimum": 1, "maximum": 65535`.
- **Prefer `enum` to `pattern`** when the set is finite — it yields better errors and docs.
- **Annotate for humans and generators.** `title`, `description`, `examples`, `default`, `deprecated` feed docs, IDE autocomplete, and form generators.
- **Use `format` judiciously.** Many validators treat `format` as annotation-only unless explicitly enabled (e.g. ajv `formats`, `format: "full"`). Back security-critical formats with a `pattern`.
- **Pin tag fields with `const`** inside `oneOf` branches so exactly one branch matches and errors point to the right place.
- **Test failing instances.** Each constraint deserves a test that proves it rejects bad input.

## Common Pitfalls
- **`additionalProperties: false` + `allOf`/`$ref`** silently rejects inherited properties. Use `unevaluatedProperties: false` instead when extending.
- **Mixing draft idioms.** Don't use `definitions` (Draft-07) and `$defs` (2020-12) inconsistently, or `items: [..]` tuple syntax under 2020-12 (use `prefixItems`).
- **`required` does not imply existence checks for nested objects** unless you also constrain the nested schema — list `required` at each level.
- **`oneOf` with non-exclusive branches** fails when input matches two branches. Add discriminators.
- **Forgetting `type`** lets unexpected JSON types pass (a number where you meant a string).
- **`format` assumed enforced.** It's often advisory; verify your validator enforces it or add a `pattern`.
- **Numbers vs integers.** `"type": "number"` accepts `1.5`; use `"integer"` for counts/ports/IDs.
- **Unescaped regex in `pattern`.** JSON requires `\\` for a single backslash; `\d` must be written `\\d`.
- **Open `enum` drift.** When the value set grows, update the schema — stale enums reject valid new values.
