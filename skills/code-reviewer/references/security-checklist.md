# Security Review Checklist (OWASP-aligned)

Apply this lens to any code that crosses a trust boundary: HTTP handlers, file/IO, deserialization, subprocess, DB access, auth, crypto. Assume all external input is hostile.

## A01 — Broken Access Control
- [ ] Every protected endpoint checks authorization, not just authentication.
- [ ] Object-level authz: user can only access *their* resources (no IDOR — `/orders/{id}` must verify ownership).
- [ ] No reliance on client-side checks or hidden fields for access control.
- [ ] Default-deny: new routes/actions require explicit permission.
- [ ] Privilege escalation paths checked (role changes, admin flags from request body).

## A02 — Cryptographic Failures
- [ ] Secrets/PII encrypted at rest and in transit (TLS enforced).
- [ ] Passwords hashed with bcrypt/scrypt/argon2 (never MD5/SHA1, never plaintext).
- [ ] Strong randomness for tokens/keys (`secrets`, `crypto.randomBytes`, `SecureRandom`) — not `random`/`Math.random`.
- [ ] Constant-time comparison for secrets/tokens/HMAC (`hmac.compare_digest`, `crypto.timingSafeEqual`).
- [ ] No custom crypto; use vetted libraries; no ECB mode; IV/nonce never reused.
- [ ] Correct key length and algorithm; no hardcoded keys.

## A03 — Injection
- [ ] SQL: parameterized queries / prepared statements / ORM bindings — never string concatenation/interpolation.
- [ ] NoSQL: query operators not taken from user input (Mongo `$where`, object injection).
- [ ] OS command: avoid shell; use arg arrays; never interpolate input into `system`/`exec`/`shell=True`.
- [ ] LDAP / XPath / template injection (SSTI) — escape or use safe APIs.
- [ ] Output encoding for HTML/JS/URL contexts to prevent XSS; framework auto-escaping not bypassed (`dangerouslySetInnerHTML`, `|safe`, `v-html`).
- [ ] Log injection / CRLF in headers prevented.

## A04 — Insecure Design
- [ ] Rate limiting / throttling on auth, OTP, and expensive endpoints.
- [ ] Business-logic abuse considered (negative amounts, replay, race-to-double-spend).
- [ ] Fail closed, not open.

## A05 — Security Misconfiguration
- [ ] No debug mode / verbose errors / stack traces returned to clients in prod.
- [ ] Secure defaults; unnecessary features/endpoints disabled.
- [ ] Security headers present where relevant (CSP, HSTS, X-Content-Type-Options).
- [ ] CORS not set to `*` with credentials; allowlist origins.
- [ ] Permissions on created files/dirs are least-privilege.

## A06 — Vulnerable & Outdated Components
- [ ] New/updated dependencies are from trusted sources and reasonably current.
- [ ] No known-vulnerable versions pinned; lockfile updated.
- [ ] No dependency confusion (internal package names not claimable publicly).

## A07 — Identification & Authentication Failures
- [ ] Session tokens are random, rotated on privilege change, invalidated on logout.
- [ ] No session fixation; secure + httpOnly + sameSite cookies.
- [ ] Brute-force protection; account lockout/backoff.
- [ ] MFA flows don't leak whether an account exists.

## A08 — Software & Data Integrity Failures
- [ ] Untrusted deserialization avoided (`pickle`, `yaml.load`, Java native serialization, PHP `unserialize`).
- [ ] Signed/verified updates and artifacts.
- [ ] CI/CD: untrusted PRs can't access secrets; no `pull_request_target` misuse.

## A09 — Logging & Monitoring Failures
- [ ] Security events logged (auth failures, access-control denials).
- [ ] Secrets/PII/tokens NOT written to logs.
- [ ] Logs can't be forged by user input (sanitized).

## A10 — Server-Side Request Forgery (SSRF)
- [ ] User-supplied URLs validated against an allowlist; no fetch to internal/metadata IPs (169.254.169.254, localhost, RFC1918).
- [ ] Redirects followed safely; DNS-rebinding considered.

## Other High-Value Checks
- [ ] **Secrets in code**: no API keys, passwords, tokens, private keys committed. (`git diff` for `KEY=`, `SECRET`, `PRIVATE KEY`, long base64.)
- [ ] **Path traversal**: user input in file paths is sanitized/normalized; reject `..`; confine to base dir.
- [ ] **Mass assignment**: request bodies can't set protected fields (`is_admin`, `role`, `balance`).
- [ ] **Open redirect**: redirect targets validated against allowlist.
- [ ] **Regex DoS (ReDoS)**: no catastrophic backtracking on user input.
- [ ] **XXE**: XML parsers have external entity resolution disabled.
- [ ] **Insecure temp files / TOCTOU**: atomic creation, predictable names avoided.

## Quick Grep Patterns

Run these against the diff to catch low-hanging fruit:

```bash
# Secrets
git diff | grep -iE '(api[_-]?key|secret|password|token|private key)\s*[:=]'
# Dangerous calls
git diff | grep -nE 'eval\(|exec\(|pickle\.load|yaml\.load\(|shell=True|os\.system|subprocess.*shell=True|innerHTML|dangerouslySetInnerHTML'
# SQL string building
git diff | grep -nE 'SELECT .*\+|f"SELECT|execute\(.*%|\.format\(.*SELECT'
# Weak crypto / randomness
git diff | grep -niE 'md5|sha1|Math\.random|random\.random|DES|ECB'
```
