# `<METHOD> /<resource>/{id}`

> `<one-line imperative summary>`  
> **Requires:** `<auth scheme, e.g. Bearer token with `users:write` scope>`

<Description: what it does, side effects, when to use it, notable constraints.>

## Path parameters

| Name | In | Type | Required | Default | Constraints | Description |
|------|----|------|----------|---------|-------------|-------------|
| `id` | path | string | Yes | — | `usr_` prefix | Identifier of the resource. |

## Query parameters

| Name | In | Type | Required | Default | Constraints | Description |
|------|----|------|----------|---------|-------------|-------------|
| `expand` | query | string | No | — | enum: `account` | Inline related objects. |

## Request headers

| Header | Required | Description |
|--------|----------|-------------|
| `Idempotency-Key` | No | Unique key to safely retry the request. |

## Request body

Content-Type: `application/json`

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `email` | string | Yes | — | valid email | The user's email. |
| `role` | string | No | `member` | enum: `admin`,`member`,`viewer` | Access level. |

```json
{
  "email": "ada@example.com",
  "role": "member"
}
```

## Responses

### `201 Created`

```json
{
  "id": "usr_8f2c1a",
  "email": "ada@example.com",
  "role": "member",
  "createdAt": "2026-02-14T09:30:00Z"
}
```

## Errors

| Status | Code | When it happens | Resolution |
|--------|------|-----------------|------------|
| `400` | `validation_error` | A field is missing or malformed. | Fix the field named in `error.details`. |
| `401` | `unauthenticated` | Missing or invalid token. | Send a valid `Authorization` header. |
| `409` | `email_taken` | Email already in use. | Use a different email. |

## Example

```bash
curl -X POST https://api.acme.com/v1/users \
  -H "Authorization: Bearer $ACME_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","role":"member"}'
```
