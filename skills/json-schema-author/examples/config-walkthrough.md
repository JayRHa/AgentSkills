# Worked Example: From Sample Config to Schema

Goal: take a real config file and produce a strict, well-errored JSON Schema, then prove it accepts good input and rejects bad input.

## 1. Starting sample (what users actually write)

```json
{
  "service": "billing-api",
  "environment": "prod",
  "server": { "host": "0.0.0.0", "port": 8443, "tls": { "enabled": true, "certFile": "/etc/tls/cert.pem", "keyFile": "/etc/tls/key.pem" } },
  "logging": { "level": "info", "format": "json" },
  "timeoutSeconds": 30,
  "allowedOrigins": ["https://app.example.com"]
}
```

## 2. Decisions
- Config → strict: `additionalProperties: false` everywhere.
- `environment` is a closed set → `enum`.
- `port` is a port → `integer`, 1..65535 (not a string!).
- TLS is conditional: if `enabled`, then `certFile` and `keyFile` are required → `if`/`then`.
- `allowedOrigins` are URIs and must be unique.

The resulting schema is `templates/config-schema.json` (reuse it directly).

## 3. Validate the good instance

```
$ python3 scripts/validate.py templates/config-schema.json --data good.json
meta-schema: OK (Draft202012Validator)
instance good.json: VALID
OK: 0 warning(s)
```

## 4. Failing instances (one per constraint)

### a) Port out of range
```json
{ "service": "billing-api", "server": { "port": 99999 } }
```
```
server/port: 99999 is greater than the maximum of 65535
```

### b) Wrong type (port as string)
```json
{ "service": "billing-api", "server": { "port": "8443" } }
```
```
server/port: '8443' is not of type 'integer'
```

### c) Unknown key (typo)
```json
{ "service": "billing-api", "server": { "port": 8443 }, "loging": {} }
```
```
<root>: Additional properties are not allowed ('loging' was unexpected)
```

### d) Bad enum value
```json
{ "service": "billing-api", "environment": "production", "server": { "port": 8443 } }
```
```
environment: 'production' is not one of ['dev', 'staging', 'prod']
```

### e) Conditional requirement: TLS enabled but no cert
```json
{ "service": "billing-api", "server": { "port": 8443, "tls": { "enabled": true } } }
```
```
server/tls: 'certFile' is a required property
server/tls: 'keyFile' is a required property
```

### f) Pattern violation (uppercase service name)
```json
{ "service": "Billing_API", "server": { "port": 8443 } }
```
```
service: 'Billing_API' does not match '^[a-z][a-z0-9-]{2,31}$'
```

## 5. Turn errors into friendly messages
Feed the raw output through the mapping in `references/error-messages.md` to get, for example:

```
config error at "server/port": must be <= 65535 (got 99999)
config error at "environment": must be one of dev, staging, prod (got "production")
config error: unknown setting "loging" - did you mean "logging"?
```

## 6. Lint the schema itself
```
$ python3 scripts/validate.py templates/config-schema.json
meta-schema: OK (Draft202012Validator)
OK: 0 warning(s)
```
The linter (stdlib-only path) also flags missing `$schema`, `additionalProperties` gaps, `oneOf` branches without discriminators, and dangling `$ref`s even when the `jsonschema` package is not installed.
