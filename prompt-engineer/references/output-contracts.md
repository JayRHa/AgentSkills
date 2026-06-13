# Output Contracts (Structured Output)

When code consumes the output, treat the format as a contract and enforce it.

## Rules for reliable structured output
1. **Define the exact schema.** List every field, its type, and whether nullable.
2. **Show a concrete filled example**, not just a description. Models copy shapes.
3. **Say "output only the JSON"** and forbid markdown fences/prose if your parser is strict.
4. **Keep reasoning out of the payload.** If the model must reason, give it a separate `scratchpad` field you discard, or a pre-output `<thinking>` block you strip — never interleave reasoning with the parsed object.
5. **Use native structured-output / JSON mode** when the API offers it (function/tool schemas, response_format=json_schema). This is more reliable than prompting alone.
6. **Specify enums explicitly** for categorical fields: `status: one of "open"|"closed"|"pending"`.
7. **Define nulls/empties.** "If unknown, use null" beats silent omission or invented values.

## Template
```
Return a JSON object matching exactly this schema (no extra keys, no markdown):
{
  "title": string,
  "tags": string[],          // 1-5 items, lowercase
  "priority": "low"|"med"|"high",
  "due": string|null          // ISO-8601 date or null
}

Example:
{"title":"Renew TLS cert","tags":["infra","security"],"priority":"high","due":"2026-07-01"}
```

## Common failures and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Output wrapped in ```json fences | Model defaults to markdown | "Do not use code fences. Output raw JSON." or strip fences in parser |
| Trailing prose after JSON | No clear stop | Add stop sequence, or "Output ONLY the JSON object." |
| Invalid JSON (trailing commas, quotes) | Free-form generation | Use JSON mode / json_schema; or post-validate and retry |
| Extra/hallucinated keys | Schema not constrained | "No keys other than those listed." + schema validation |
| Missing required fields | Field optional in model's mind | Mark required; provide null rule; validate |
| Reasoning leaked into fields | CoT mixed with output | Separate scratchpad field or strip a <thinking> block |

## Validate-and-retry loop
Always validate the parsed output against the schema in code. On failure:
1. Capture the validation error.
2. Re-prompt with the original request + the broken output + the specific error, asking for a corrected object only.
3. Cap retries (e.g., 2) and fall back to a safe default or surface the error.

This loop, plus JSON mode, gets structured output reliability near-100% in practice.
