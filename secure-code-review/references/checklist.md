# Secure Code Review Checklist & Severity Rubric

## Per-file pass
- [ ] All external input identified and traced to sinks
- [ ] Queries parameterized (no string-built SQL/NoSQL)
- [ ] OS/shell calls avoid `shell=True` / string concatenation
- [ ] Output encoded for its context (HTML/JS/URL)
- [ ] Object-level authorization on every record access (no IDOR)
- [ ] AuthN: strong password hashing, constant-time token compare, rate limiting
- [ ] Sessions: rotation on login, `HttpOnly`/`Secure`/`SameSite`, expiry
- [ ] Crypto via standard libs; CSPRNG for tokens; no static IV/key
- [ ] No hardcoded secrets (incl. tests/comments)
- [ ] No unsafe deserialization / `eval` on untrusted data
- [ ] Outbound URL fetches allow-listed (SSRF)
- [ ] File paths confined to an allowed base (traversal)
- [ ] Errors don't leak stack traces/secrets; logs scrubbed
- [ ] Security headers present (HSTS, CSP, etc.)

## Severity rubric

| Severity | Definition | Examples |
| --- | --- | --- |
| **Critical** | Remote exploit, no/low auth, high impact | SQLi, RCE via deserialization, auth bypass, hardcoded prod secret |
| **High** | Exploitable under realistic conditions | Stored XSS, IDOR on sensitive data, weak password hashing |
| **Medium** | Needs preconditions or limited impact | Reflected XSS behind auth, SSRF to limited targets, missing rate limit |
| **Low** | Hardening / defense-in-depth | Missing security header, verbose errors, weak `SameSite` |

severity ≈ **exploitability × impact**. When unsure it's reachable, label "Possible:" and state what confirms it.
