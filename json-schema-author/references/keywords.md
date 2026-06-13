# JSON Schema Keyword Reference

Default dialect for new work: **Draft 2020-12** (`$schema: "https://json-schema.org/draft/2020-12/schema"`). Notes call out Draft-07 differences for legacy tooling.

## Core / metadata

| Keyword | Purpose |
|---------|---------|
| `$schema` | Declares the dialect. Always include it. |
| `$id` | Base URI for the schema; anchors relative `$ref`s. |
| `$ref` | Reference another schema (e.g. `"#/$defs/Port"`). |
| `$defs` | Reusable subschemas (Draft-07: `definitions`). |
| `$anchor` | Named anchor for `$ref` (2019-09+). |
| `title` | Short human label (docs, form fields). |
| `description` | Longer human explanation. |
| `default` | Suggested value; advisory only (validators don't inject it). |
| `examples` | Array of sample valid values. |
| `deprecated` | `true` marks a field as deprecated (2019-09+). |
| `readOnly` / `writeOnly` | API hints: response-only / request-only. |

## Types

`"type"` accepts: `"object"`, `"array"`, `"string"`, `"number"`, `"integer"`, `"boolean"`, `"null"`, or an array of these (e.g. `["string", "null"]` for nullable).

```json
{ "type": ["string", "null"] }   // nullable string
{ "type": "integer" }            // whole numbers only
{ "type": "number" }             // integers OR floats
```

## Number / integer constraints

| Keyword | Meaning |
|---------|---------|
| `minimum` / `maximum` | Inclusive bounds. |
| `exclusiveMinimum` / `exclusiveMaximum` | Exclusive bounds (a number, not boolean, in Draft-07+). |
| `multipleOf` | Value must be a multiple (e.g. `0.01` for currency). |

```json
{ "type": "integer", "minimum": 1, "maximum": 65535 }   // TCP port
{ "type": "number", "exclusiveMinimum": 0, "multipleOf": 0.01 }  // positive money
```

## String constraints

| Keyword | Meaning |
|---------|---------|
| `minLength` / `maxLength` | Character bounds. |
| `pattern` | ECMA-262 regex (anchored implicitly? NO — anchor with `^...$`). |
| `format` | Semantic hint: `email`, `uri`, `uuid`, `date-time`, `date`, `time`, `ipv4`, `ipv6`, `hostname`, `duration`, `regex`. Often advisory — verify enforcement. |
| `contentEncoding` / `contentMediaType` | For embedded binary/base64. |

```json
{ "type": "string", "format": "email", "maxLength": 254 }
{ "type": "string", "pattern": "^[a-z][a-z0-9-]{2,31}$" }   // slug; note escaped JSON
```
Regex reminder: in JSON a backslash must be doubled. `\\d`, `\\.`, `\\+`.

## Array constraints

| Keyword | Meaning |
|---------|---------|
| `items` | Schema for each element (2020-12). |
| `prefixItems` | Tuple positions (2020-12). Draft-07 uses `items` as array. |
| `additionalItems` | (Draft-07) schema/`false` for items beyond the tuple. 2020-12: use `items` after `prefixItems`. |
| `minItems` / `maxItems` | Length bounds. |
| `uniqueItems` | `true` forbids duplicates. |
| `contains` / `minContains` / `maxContains` | At least/at most N elements match a subschema. |

```json
// 2020-12 list of unique slugs
{ "type": "array", "items": { "type": "string" }, "uniqueItems": true, "minItems": 1 }

// 2020-12 tuple [lat, lng] with no extra items
{ "type": "array", "prefixItems": [ {"type":"number"}, {"type":"number"} ], "items": false }
```

## Object constraints

| Keyword | Meaning |
|---------|---------|
| `properties` | Map of property name → schema. |
| `required` | Array of mandatory property names. |
| `additionalProperties` | Schema/`false` for undeclared keys. `false` = strict. |
| `patternProperties` | Schema for keys matching a regex. |
| `propertyNames` | Constrain key strings themselves. |
| `minProperties` / `maxProperties` | Count bounds. |
| `dependentRequired` | If key X present, these keys also required. |
| `dependentSchemas` | If key X present, apply this subschema. |
| `unevaluatedProperties` | (2019-09+) `false` rejects keys not evaluated by this schema OR its `allOf`/`$ref`/conditionals. The correct strict-extension tool. |

```json
{
  "type": "object",
  "properties": { "name": {"type":"string"}, "ttl": {"type":"integer"} },
  "required": ["name"],
  "additionalProperties": false
}
```

### `additionalProperties` vs `unevaluatedProperties`
`additionalProperties: false` only knows about `properties`/`patternProperties` in the **same** object. With `allOf`/`$ref` it rejects inherited keys. Use `unevaluatedProperties: false` at the outer schema to extend strictly:
```json
{
  "allOf": [ { "$ref": "#/$defs/Base" } ],
  "properties": { "extra": { "type": "string" } },
  "unevaluatedProperties": false
}
```

## Composition / applicators

| Keyword | Semantics |
|---------|-----------|
| `allOf` | All subschemas must pass (intersection / extension). |
| `anyOf` | At least one passes. |
| `oneOf` | Exactly one passes (else fail). |
| `not` | Subschema must NOT pass. |
| `if` / `then` / `else` | Conditional: if `if` matches, apply `then`, else `else`. |

### Tagged-union (discriminator) pattern
Pin the tag with `const` in each `oneOf` branch so exactly one matches:
```json
"oneOf": [
  { "properties": { "kind": {"const":"a"}, "x": {"type":"string"} }, "required":["x"] },
  { "properties": { "kind": {"const":"b"}, "y": {"type":"integer"} }, "required":["y"] }
]
```
OpenAPI 3.x also supports a `discriminator` object for tooling, but the schema-level `const` is what enforces correctness.

### Conditional required field
```json
{
  "properties": { "auth": {"enum":["none","token"]}, "token": {"type":"string"} },
  "if":   { "properties": { "auth": {"const":"token"} } },
  "then": { "required": ["token"] }
}
```

## Enum / const
```json
{ "enum": ["debug", "info", "warn", "error"] }
{ "const": "v1" }
```
Prefer `enum` over `pattern` for closed sets — clearer errors and generated docs.

## Draft 2020-12 vs Draft-07 cheat sheet

| Concept | Draft 2020-12 | Draft-07 |
|---------|---------------|----------|
| Reusable defs | `$defs` | `definitions` |
| Tuple items | `prefixItems` + `items` | `items` (array) + `additionalItems` |
| Strict extension | `unevaluatedProperties` | not available (declare all locally) |
| `$schema` URI | `.../draft/2020-12/schema` | `.../draft-07/schema#` |
| OpenAPI alignment | OpenAPI 3.1 | OpenAPI 3.0 (subset, no `$schema`) |
