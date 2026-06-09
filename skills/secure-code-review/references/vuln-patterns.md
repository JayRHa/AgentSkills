# Vulnerability Patterns Reference

For each class: what it is, the smell, and the fix.

## 1. Injection (SQL, NoSQL, OS command, LDAP)
- **Smell:** untrusted input concatenated into a query/command string (`f"... {x}"`, `+ x`, `os.system(... + x)`).
- **Fix:** parameterized queries / prepared statements; pass args as a list to subprocess (no `shell=True`); use ORMs safely.

## 2. Cross-Site Scripting (XSS)
- **Smell:** user input rendered into HTML/JS without context-aware encoding; `innerHTML`, `dangerouslySetInnerHTML`, unescaped template output.
- **Fix:** encode for the output context; use framework auto-escaping; sanitize HTML with a vetted library; set a Content-Security-Policy.

## 3. Broken Access Control / IDOR
- **Smell:** object fetched by an ID from the request with no ownership check (`Order.get(request.id)`); role checks missing on an endpoint.
- **Fix:** enforce object-level authorization (`where owner_id = current_user`); deny by default; centralize policy checks.

## 4. Authentication & Session
- **Smell:** passwords hashed with MD5/SHA1/no salt; tokens compared with `==`; no rate limiting; session IDs in URLs; no expiry.
- **Fix:** use bcrypt/argon2/scrypt; `hmac.compare_digest`; rate-limit + lockout; rotate session on login; set `HttpOnly`, `Secure`, `SameSite`.

## 5. Cryptographic Failures
- **Smell:** ECB mode, hardcoded/static IV or key, `Math.random()` for tokens, custom crypto, deprecated TLS.
- **Fix:** AES-GCM (or libsodium); random IV per message; CSPRNG (`secrets`/`os.urandom`); TLS 1.2+; rely on standard libraries.

## 6. Hardcoded Secrets
- **Smell:** API keys, passwords, private keys literal in source, configs, or tests.
- **Fix:** load from env/secret manager; rotate leaked secrets; add secret scanning to CI; purge from git history.

## 7. Insecure Deserialization
- **Smell:** `pickle.loads`, `yaml.load` (unsafe), Java/PHP native deserialization, `eval`/`exec` on untrusted data.
- **Fix:** use safe formats (JSON); `yaml.safe_load`; never deserialize untrusted bytes into objects; sign/validate payloads.

## 8. SSRF (Server-Side Request Forgery)
- **Smell:** server fetches a URL supplied by the user (`requests.get(user_url)`).
- **Fix:** allow-list hosts/schemes; block private/link-local ranges (169.254.169.254, 10/8, 127/8); disable redirects to internal hosts.

## 9. Path Traversal
- **Smell:** file path built from user input (`open(base + filename)`), `../` not handled.
- **Fix:** resolve and confirm the canonical path stays within an allowed base dir; allow-list filenames; reject `..`.

## 10. CSRF
- **Smell:** state-changing GET/POST without anti-CSRF token; cookies without `SameSite`.
- **Fix:** anti-CSRF tokens; `SameSite=Lax/Strict`; require re-auth for sensitive actions.

## 11. Security Misconfiguration & Data Exposure
- **Smell:** debug mode on in prod, verbose stack traces, directory listing, secrets in logs, missing security headers.
- **Fix:** harden defaults; generic error pages; scrub PII/secrets from logs; set security headers (HSTS, CSP, X-Content-Type-Options).
