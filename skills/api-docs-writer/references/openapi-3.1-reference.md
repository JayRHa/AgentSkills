# OpenAPI 3.1 Reference

A condensed, practical reference for authoring OpenAPI 3.1 specs. Load this when producing or editing a spec.

> OpenAPI 3.1 is fully compatible with JSON Schema 2020-12. Prefer 3.1 over 3.0 for new specs.

## Top-level structure

```yaml
openapi: 3.1.0
info:
  title: Acme API
  version: "1.4.0"
  description: Public REST API for Acme resources.
  contact:
    name: API Support
    email: api@acme.com
  license:
    name: MIT
servers:
  - url: https://api.acme.com/v1
    description: Production
  - url: https://sandbox.acme.com/v1
    description: Sandbox
tags:
  - name: Users
    description: User accounts.
paths: {}
components: {}
security: []
```

- `openapi`: must be a 3.1.x string.
- `info.version`: API version (not the OpenAPI version). Use semver.
- `servers`: list real base URLs. The path in `paths` is appended to `server.url`.
- `tags`: group operations for nicer rendering.
- top-level `security`: default applied to every operation unless overridden.

## Paths and operations

```yaml
paths:
  /users/{userId}:
    parameters:
      - $ref: '#/components/parameters/UserId'   # shared by all methods on this path
    get:
      operationId: getUser
      summary: Retrieve a user
      description: Returns a single user by id.
      tags: [Users]
      responses:
        '200':
          description: The user.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'
```

- `operationId` must be unique across the whole spec; SDK generators use it for method names.
- Status codes are quoted strings (`'200'`).
- Use `default` response only for catch-all error shapes.

## Parameters

Each parameter object:

```yaml
- name: limit
  in: query           # query | path | header | cookie
  required: false      # MUST be true when in: path
  description: Max items per page.
  schema:
    type: integer
    minimum: 1
    maximum: 100
    default: 20
  example: 50
```

Rules:
- `in: path` parameters are always `required: true`.
- Put constraints (`minimum`, `maxLength`, `enum`, `pattern`) inside `schema`.
- For arrays in query strings, set `style` and `explode` (default `form`/`true`).

## Request bodies

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CreateUser'
      examples:
        minimal:
          summary: Minimal payload
          value:
            email: ada@example.com
```

- `requestBody.required` defaults to `false` — set `true` for create/update.
- Use `multipart/form-data` with `format: binary` for file uploads.
- `examples` (plural, keyed map) is preferred over single `example`.

## Responses

```yaml
responses:
  '201':
    description: User created.
    headers:
      Location:
        schema: { type: string }
        description: URL of the created user.
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
```

- Every response needs a `description`.
- Document custom response headers (rate-limit, pagination, `Location`).

## Schemas (JSON Schema 2020-12)

```yaml
components:
  schemas:
    User:
      type: object
      required: [id, email, createdAt]
      properties:
        id:
          type: string
          examples: ['usr_8f2c1a']
        email:
          type: string
          format: email
        role:
          type: string
          enum: [admin, member, viewer]
          default: member
        createdAt:
          type: string
          format: date-time
      additionalProperties: false
```

Useful keywords:
- Strings: `format` (`email`, `uuid`, `date-time`, `uri`), `minLength`, `maxLength`, `pattern`, `enum`.
- Numbers: `minimum`, `maximum`, `exclusiveMinimum`, `multipleOf`.
- Objects: `required` (array of property names), `additionalProperties`.
- Arrays: `items`, `minItems`, `maxItems`, `uniqueItems`.
- Nullable in 3.1: use a type array, e.g. `type: [string, 'null']` (the 3.0 `nullable: true` is gone).
- Composition: `allOf`, `oneOf`, `anyOf`; use `discriminator` for polymorphic types.

## Reusable components

```yaml
components:
  parameters:
    UserId:
      name: userId
      in: path
      required: true
      schema: { type: string }
  responses:
    NotFound:
      description: Resource not found.
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    apiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

Apply security per operation or globally:

```yaml
security:
  - bearerAuth: []
```

An empty `security: []` on an operation makes it public.

## Security scheme types

| type | scheme/flow | Use for |
|------|-------------|---------|
| `http` | `bearer` | JWT / opaque bearer tokens |
| `http` | `basic` | username:password |
| `apiKey` | `in: header/query/cookie` | API keys |
| `oauth2` | flows: authorizationCode, clientCredentials | OAuth 2 |
| `openIdConnect` | `openIdConnectUrl` | OIDC discovery |

## Common validation errors to avoid
- `in: path` parameter not marked `required: true`.
- `$ref` pointing to a component that does not exist.
- Response missing `description`.
- Duplicate `operationId`.
- Using 3.0 `nullable: true` instead of 3.1 type arrays.
- `requestBody` without a `content` map.
