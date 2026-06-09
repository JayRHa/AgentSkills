# Clear Validation Error Messages

A schema that rejects bad input is only half the job. Operators and API clients need to know **what** is wrong and **how** to fix it. This guide covers producing actionable errors.

## Principle: identify, explain, suggest
Good error = location + what's wrong + what's expected (+ example when cheap).

- Bad: `data.timeout should be number`
- Good: `config error at "timeout": expected an integer between 1 and 600 (seconds), got "30s". Example: 30`

## Two strategies

### 1. Curated messages embedded in the schema
Many ecosystems let you attach messages to keywords.

**ajv (`ajv-errors` plugin):**
```json
{
  "type": "object",
  "properties": {
    "port": {
      "type": "integer", "minimum": 1, "maximum": 65535,
      "errorMessage": {
        "type": "port must be a whole number",
        "minimum": "port must be >= 1",
        "maximum": "port must be <= 65535"
      }
    }
  },
  "required": ["port"],
  "errorMessage": { "required": { "port": "port is required" } }
}
```

Use `title`/`description` as a portable fallback that most tools surface:
```json
{ "type": "string", "format": "email",
  "title": "Recipient email",
  "description": "A valid email address, e.g. ops@example.com" }
```

### 2. Post-process raw validator output
When you can't embed messages, map validator output to friendly text. Both ajv and Python `jsonschema` expose: the failing **path**, the **keyword**, and the **expected** value.

Python `jsonschema` example:
```python
from jsonschema import Draft202012Validator

FRIENDLY = {
    "required": lambda e: f"missing required field: {e.message.split(\"'\")[1]}",
    "type":     lambda e: f"{path(e)}: expected {e.validator_value}, got {type(e.instance).__name__}",
    "enum":     lambda e: f"{path(e)}: must be one of {e.validator_value}",
    "minimum":  lambda e: f"{path(e)}: must be >= {e.validator_value}",
    "maximum":  lambda e: f"{path(e)}: must be <= {e.validator_value}",
    "pattern":  lambda e: f"{path(e)}: does not match required format",
}

def path(e):
    return "/".join(str(p) for p in e.absolute_path) or "<root>"

def explain(instance, schema):
    v = Draft202012Validator(schema)
    out = []
    for e in sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        fmt = FRIENDLY.get(e.validator)
        out.append(fmt(e) if fmt else f"{path(e)}: {e.message}")
    return out
```

## Reducing noise from `oneOf`/`anyOf`
These applicators produce one error per failing branch — verbose and confusing. Tactics:
- **Pin a discriminator** (`const`) so only the matching branch reports detailed errors; collapse the rest to a single "unknown kind" message.
- Surface only the error from the branch whose discriminator matched the input.
- For ajv, use `allErrors: false` (default) for fail-fast UX, or curate with `ajv-errors`.

## Message style checklist
- [ ] Includes the JSON path / property name.
- [ ] States the expected type/range/set, not just "invalid".
- [ ] Avoids leaking internal schema URIs and `$ref` paths to end users.
- [ ] Gives an example value for non-obvious formats.
- [ ] Uses the user's vocabulary ("timeout in seconds"), not the validator's ("maximum").
- [ ] Consistent casing and punctuation across messages.
- [ ] For APIs: machine-readable code + human message (e.g. `{ "field": "port", "code": "out_of_range", "message": "..." }`).

## API error envelope (recommended)
```json
{
  "error": "validation_failed",
  "details": [
    { "field": "port", "code": "maximum", "message": "port must be <= 65535" },
    { "field": "name", "code": "required", "message": "name is required" }
  ]
}
```
Keep `code` stable so clients can branch on it; `message` may be localized/changed freely.
