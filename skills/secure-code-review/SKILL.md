---
name: secure-code-review
description: Performs a security-focused review of code or a diff, hunting for injection, broken authentication/authorization, insecure crypto, hardcoded secrets, unsafe deserialization, SSRF, path traversal, and missing input validation, with exploit scenarios and concrete fixes ranked by severity. Use this skill when the user asks to "do a security review", "audit this code for vulnerabilities", "is this code secure", "check for security issues before deploy", "review this auth/crypto code", or wants a security pass on a PR. Complements general code review with a threat-focused lens.
license: MIT
---

# Secure Code Review

## Overview

Review code through the eyes of an attacker. For each finding, name the **vulnerability class**, show **how it's exploited**, rate **severity**, and give a **concrete fix**. Scope to the diff/files provided; pull in just enough surrounding code (callers, trust boundaries) to judge exploitability.

Keywords: security review, secure code review, vulnerability, OWASP, injection, SQLi, XSS, command injection, authentication, authorization, IDOR, broken access control, crypto, secrets, hardcoded credentials, deserialization, SSRF, path traversal, input validation, CSRF.

## Workflow

1. **Map trust boundaries.** Identify where untrusted data enters: HTTP params/body/headers, file uploads, env, message queues, DB rows from other tenants, third-party APIs. Untrusted input is where most bugs live.
2. **Trace tainted data to sinks.** Follow each untrusted input to dangerous sinks (SQL, shell, file paths, HTML output, deserializers, redirects, template engines). A flow from source → sink without sanitization is a finding.
3. **Review each vulnerability class** using `references/vuln-patterns.md`: injection, broken access control/authz, auth & session, crypto, secrets, deserialization, SSRF, path traversal, CSRF, security misconfig, sensitive-data exposure.
4. **Check authorization on every sensitive operation.** Authentication ≠ authorization. Confirm object-level checks (does this user own this record?) to catch IDOR / broken access control.
5. **Scan for low-hanging fruit** with `scripts/secret_scan.py` (hardcoded secrets, dangerous function calls). Triage hits — it's a starting point, not proof.
6. **Rate severity** (Critical/High/Medium/Low) by exploitability × impact, using `references/checklist.md`.
7. **Write findings** with: class, `file:line`, exploit scenario, severity, and a concrete fix (prefer a diff). End with a verdict and a prioritized fix list.

## Decision Heuristics

- **Assume all external input is hostile** until validated/escaped at the sink.
- **Escape at the sink, validate at the boundary** — parameterized queries beat input filtering.
- **Deny by default** for access control; explicit allow per resource and action.
- **Never trust client-side checks** — they're UX, not security.
- **Secrets in code = Critical**, even in tests or comments, because of git history.
- If uncertain it's exploitable, mark **"Possible:"** and state what would confirm it.

## Worked Example

```python
# src/api/users.py:88  — VULNERABLE
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)
```
**Finding — [Critical] SQL Injection — src/api/users.py:88**
An attacker submitting `email=' OR '1'='1` reads all rows; `'; DROP TABLE users;--` can destroy data.
**Fix:** use a parameterized query:
```python
db.execute("SELECT * FROM users WHERE email = %s", (email,))
```

## Best Practices

- Prefer **parameterized queries / prepared statements** over string building everywhere.
- **Context-aware output encoding** for XSS (HTML, attribute, JS, URL contexts differ).
- Use **vetted libraries** for crypto and auth — never hand-roll. Use `hmac.compare_digest` for secret comparison.
- **Allow-list** inputs (paths, redirect targets, file types) rather than block-listing.
- Keep **secrets in a vault/KMS or env**, never in source; rotate anything that leaked.
- Add a **regression test** for each fixed vuln.

## Common Pitfalls

- Treating **authentication as authorization** — logged-in users still need per-object checks (IDOR).
- **Block-list validation** that attackers trivially bypass; prefer allow-lists and escaping at the sink.
- **Custom crypto** (homemade tokens, ECB mode, static IVs, MD5/SHA1 for passwords).
- **`eval`/`pickle`/`yaml.load`/native deserialization** on untrusted data → RCE.
- **Verbose error messages / stack traces** leaking internals to users.
- **Reflected user input** into HTML, headers, or redirects without encoding/allow-listing.
- Reviewing only the happy path — vulns hide in error handlers and edge cases.
