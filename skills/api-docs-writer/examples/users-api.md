# Worked Example: Documenting a Users API

This shows the full path from source code to delivered docs.

## Input: source routes (FastAPI)

```python
@router.get("/users")
def list_users(limit: int = 20, cursor: str | None = None, user=Depends(auth)):
    ...  # returns {"data": [...], "hasMore": bool, "nextCursor": str | None}

@router.post("/users", status_code=201)
def create_user(body: CreateUser, user=Depends(auth)):
    # raises HTTPException(409, "email_taken") if email exists
    ...  # returns the created User

class CreateUser(BaseModel):
    email: EmailStr
    role: Literal["admin", "member", "viewer"] = "member"
```

## Step 1 — Inventory (from the extraction checklist)

| Endpoint | Auth | Params | Body | Success | Errors |
|----------|------|--------|------|---------|--------|
| `GET /users` | Bearer | `limit` (1–100, def 20), `cursor` | — | `200` UserList | `401` |
| `POST /users` | Bearer | — | `email`*, `role` | `201` User | `400`, `401`, `409` |

## Step 2 — Reference page output

### `POST /users`

> Create a user.  
> **Requires:** Bearer token.

Creates a new user account. The email must be unique across the workspace; a
duplicate returns `409 email_taken`. This operation has a side effect: a welcome
email is queued on success.

#### Request body — `application/json`

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `email` | string | Yes | — | valid email | The user's email address. |
| `role` | string | No | `member` | enum: `admin`,`member`,`viewer` | Access level. |

```json
{ "email": "ada@example.com", "role": "member" }
```

#### Responses

`201 Created`

```json
{
  "id": "usr_8f2c1a",
  "email": "ada@example.com",
  "role": "member",
  "createdAt": "2026-02-14T09:30:00Z"
}
```

#### Errors

| Status | Code | When it happens | Resolution |
|--------|------|-----------------|------------|
| `400` | `validation_error` | `email` missing or malformed. | Send a valid email. |
| `401` | `unauthenticated` | Missing/invalid token. | Provide a valid Bearer token. |
| `409` | `email_taken` | Email already registered. | Use a different email. |

#### Example

```bash
curl -X POST https://api.acme.com/v1/users \
  -H "Authorization: Bearer $ACME_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","role":"member"}'
```

## Step 3 — Pagination section (shared, written once)

List endpoints use opaque cursor pagination. Pass `limit` (1–100, default 20) and
`cursor`. The response includes `hasMore` and `nextCursor`. Fetch page 2:

```bash
curl "https://api.acme.com/v1/users?limit=20&cursor=eyJpZCI6InVzcl84ZjJjMWEifQ" \
  -H "Authorization: Bearer $ACME_API_KEY"
```

When `hasMore` is `false`, `nextCursor` is `null` and you have reached the end.

## Step 4 — OpenAPI excerpt

See `templates/openapi-skeleton.yaml` for the full spec; the `POST /users`
operation and `CreateUser`/`User`/`Error` schemas there match this example.

## Step 5 — Validate

```bash
python3 scripts/validate_openapi.py templates/openapi-skeleton.yaml
# == templates/openapi-skeleton.yaml ==
#   OK (0 warning(s)).
```
