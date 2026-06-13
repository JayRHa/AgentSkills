# OWASP Top 10 (2021) — Audit Reference

For each category: what it is, where to look, vulnerable patterns by language, and the correct fix. CWE ids included for tracking.

---

## A01:2021 — Broken Access Control (CWE-284, CWE-639, CWE-22)

**The #1 risk.** A user performs actions or accesses data outside their permissions.

### Sub-types
- **IDOR / BOLA** — endpoint trusts an id from the request without checking the caller owns the object: `GET /api/invoices/{id}` returns any invoice.
- **Missing function-level authz** — admin endpoint reachable by normal user (only the UI hides it).
- **Path traversal** — `../../etc/passwd` reaches the filesystem (CWE-22).
- **Forced browsing / verb tampering** — `POST` blocked but `PUT` allowed.
- **JWT/cookie tampering** — role claim trusted without verification.

### Where to look
- Every route handler: is there an authz check *after* authn?
- Queries filtered only by the requested id, not by `current_user.id`.
- File reads built from user input.

### Vulnerable
```python
@app.get('/invoice/<int:id>')
@login_required
def invoice(id):
    return db.invoices.find_one({'_id': id})   # any logged-in user reads any invoice
```
```python
open(os.path.join(UPLOAD_DIR, request.args['name']))  # name='../../../../etc/passwd'
```

### Fix
```python
inv = db.invoices.find_one({'_id': id, 'owner': current_user.id})
if inv is None:
    abort(404)
```
```python
base = os.path.realpath(UPLOAD_DIR)
full = os.path.realpath(os.path.join(base, request.args['name']))
if not full.startswith(base + os.sep):
    abort(403)
```
Deny by default. Enforce ownership server-side. Centralize authz in middleware/decorators.

---

## A02:2021 — Cryptographic Failures (CWE-327, CWE-916, CWE-798)

Sensitive data exposed due to missing or weak cryptography.

### Vulnerable patterns
- Passwords with `md5` / `sha1` / unsalted hashes.
- Hardcoded keys/secrets in source (CWE-798).
- `ssl.verify = False`, `verify=False`, `rejectUnauthorized: false` (disabled TLS verification).
- ECB mode, static IV, `Math.random()` / `random.random()` for tokens.
- Sensitive data (PII, tokens) stored in plaintext.

### Detect
```
md5(  sha1(  DES  ECB  verify=False  rejectUnauthorized: false
AKIA[0-9A-Z]{16}   (AWS key)   -----BEGIN .* PRIVATE KEY-----
```

### Fix
- Passwords: `bcrypt`, `argon2`, or `scrypt` with per-user salt (use the framework's password hasher).
- Tokens/keys: CSPRNG — `secrets.token_urlsafe()` (Python), `crypto.randomBytes()` (Node).
- Encryption: AES-GCM (authenticated) with a random nonce; never ECB.
- Secrets: load from env/secret manager, never commit. Rotate any exposed key.
- TLS: never disable verification in production.

---

## A03:2021 — Injection (CWE-89, CWE-78, CWE-79, CWE-90, CWE-943)

Untrusted input is interpreted as code/command/query.

### SQL Injection (CWE-89)
```python
cursor.execute("SELECT * FROM users WHERE name='" + name + "'")  # VULN
cursor.execute(f"... WHERE id = {uid}")                          # VULN (f-string)
```
Fix — parameterize:
```python
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```
ORMs: never pass user input into `.raw()` / `text()` / `extra()` via string concat.

### OS Command Injection (CWE-78)
```python
os.system("ping " + host)                       # VULN
subprocess.run(f"convert {f} out.png", shell=True)  # VULN
```
Fix — arg list, no shell:
```python
subprocess.run(["ping", "-c", "1", host], shell=False)
```

### Cross-Site Scripting / XSS (CWE-79)
- **Reflected/Stored:** user input rendered into HTML without encoding.
- React: `dangerouslySetInnerHTML={{__html: userInput}}`.
- Templates: `{{ x | safe }}` (Jinja), `{!! $x !!}` (Blade), disabling auto-escape.
Fix: rely on auto-escaping; for rich HTML use a sanitizer (DOMPurify, bleach). Encode per context (HTML body vs attribute vs JS vs URL).

### NoSQL Injection (CWE-943)
```js
db.users.find({ user: req.body.user, pass: req.body.pass })
// attacker sends pass: {"$ne": null}
```
Fix: cast to string, validate types, use schema validation.

### Others
LDAP (CWE-90), XPath, template injection (SSTI), header/CRLF injection. Same rule: parameterize or strictly validate against an allowlist.

---

## A04:2021 — Insecure Design (CWE-209, CWE-256, CWE-799)

Flaws in the design, not the implementation. Code can be "correct" yet insecure.

- No rate limiting / lockout on login, OTP, password reset (credential stuffing, brute force).
- Trusting client-supplied price/role/quantity.
- Recoverable password storage (security questions, plaintext reset).
- Missing MFA on sensitive operations.
- Business-logic bypass (negative quantity, replay).

Fix: threat-model the feature, add rate limits, server-side authorization of all state changes, defense in depth.

---

## A05:2021 — Security Misconfiguration (CWE-16, CWE-732, CWE-942)

- Debug mode in production (`DEBUG=True`, stack traces to client).
- Default credentials, sample apps, admin consoles exposed.
- Overly permissive CORS: `Access-Control-Allow-Origin: *` with credentials.
- Missing security headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options).
- Verbose error messages leaking stack traces, SQL, versions.
- Cloud storage buckets world-readable; directory listing on.

Fix: harden defaults, disable debug, restrict CORS to known origins, add security headers, return generic errors to clients while logging detail server-side.

---

## A06:2021 — Vulnerable & Outdated Components (CWE-1104, CWE-937)

- Dependencies with known CVEs; unmaintained libraries; pinned old versions.

Detect: `npm audit`, `pip-audit`, `osv-scanner`, `govulncheck`, GitHub Dependabot. Check lockfiles.

Report with reachability: rate higher if the vulnerable function is actually called. Fix: upgrade to a patched version; if none, mitigate or replace.

---

## A07:2021 — Identification & Authentication Failures (CWE-287, CWE-384, CWE-307)

- Weak/absent password policy; no breach-password check.
- No brute-force protection (overlaps A04).
- Session fixation: session id not rotated on login (CWE-384).
- Predictable/long-lived session tokens; missing `HttpOnly`, `Secure`, `SameSite`.
- **JWT flaws:** `alg: none` accepted, signature not verified, `HS256`/`RS256` confusion, no expiry.
- Credentials/secrets in URLs (logged).

Fix: framework session management, rotate session on privilege change, secure cookie flags, verify JWT signature + `exp` + `aud`/`iss`, never accept `alg: none`.

---

## A08:2021 — Software & Data Integrity Failures (CWE-502, CWE-345)

- **Insecure deserialization (CWE-502):** `pickle.loads`, `yaml.load` (unsafe), Java `ObjectInputStream`, PHP `unserialize` on untrusted data → RCE.
- Unsigned auto-updates; CI/CD pulling unpinned/unverified artifacts.
- Untrusted data used in `eval` / dynamic require.

### Vulnerable
```python
import pickle
obj = pickle.loads(request.data)        # RCE
yaml.load(stream)                       # use safe_load
```
Fix: use safe formats (JSON), `yaml.safe_load`, signed/verified payloads, integrity checks (subresource integrity, signed packages), never deserialize attacker data into objects.

---

## A09:2021 — Security Logging & Monitoring Failures (CWE-778, CWE-532)

- No audit log for login success/failure, access-control failures, high-value actions.
- Logs that **contain** secrets/PII/tokens/passwords (CWE-532) — itself a vulnerability.
- Logs not protected/centralized; no alerting.

Fix: log security events with enough context (who/what/when/where) but redact secrets. Ensure tamper-resistant, monitored storage. Never log raw passwords, full card numbers, or tokens.

---

## A10:2021 — Server-Side Request Forgery / SSRF (CWE-918)

Server makes a request to a URL it gets from the user.

### Vulnerable
```python
url = request.args['url']
resp = requests.get(url)   # attacker: http://169.254.169.254/latest/meta-data/ (cloud creds)
```

### Impact
Read cloud metadata (IAM creds), reach internal services, port-scan the internal network, bypass firewalls.

### Fix
- Allowlist destination hosts/schemes; reject by default.
- Resolve DNS and **block private/link-local/loopback ranges** (10/8, 172.16/12, 192.168/16, 127/8, 169.254/16, ::1, fc00::/7).
- Disable redirects or re-validate each hop.
- Use a dedicated egress proxy with no internal access.
- Beware DNS-rebinding: validate the IP actually connected to.

---

## Cross-cutting: CSRF (CWE-352)
State-changing requests without anti-CSRF tokens and using cookie auth. Fix: per-session CSRF tokens or `SameSite=Lax/Strict` cookies + verify Origin/Referer.
