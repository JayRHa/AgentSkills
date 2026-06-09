# STRIDE Catalog

Reference for threat enumeration. STRIDE is a mnemonic for six threat categories, each the negation of a desirable security property.

| Letter | Threat | Violated property | Core question |
|---|---|---|---|
| **S** | Spoofing | Authentication | Can someone pretend to be another principal? |
| **T** | Tampering | Integrity | Can data or code be modified without authorization? |
| **R** | Repudiation | Non-repudiation | Can someone deny an action with no proof? |
| **I** | Information disclosure | Confidentiality | Can data leak to unauthorized parties? |
| **D** | Denial of service | Availability | Can the system be made unavailable? |
| **E** | Elevation of privilege | Authorization | Can someone gain capabilities they should not have? |

## STRIDE-per-element applicability matrix

Apply only the cells marked applicable; this prevents both gaps and noise.

| Element type | S | T | R | I | D | E |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| External entity (user, third party) | yes | - | yes | - | - | - |
| Process (service, function, worker) | yes | yes | yes | yes | yes | yes |
| Data store (db, cache, bucket, file) | - | yes | yes* | yes | yes | - |
| Data flow (request, query, message) | - | yes | - | yes | yes | - |

\* Repudiation applies to a data store when it is itself the audit/log store (e.g., logs can be deleted or forged).

## Attacker archetypes

Consider each threat from multiple attacker viewpoints:

- **Unauthenticated remote attacker** — anyone on the Internet hitting public endpoints.
- **Authenticated low-privilege user** — a legitimate account abusing the system or other tenants.
- **Malicious insider** — employee/operator with elevated access.
- **Compromised dependency** — a third-party library, SaaS, or supply-chain element turned hostile.
- **Network adversary** — on-path attacker observing or modifying traffic (MITM).
- **Stolen-credential attacker** — possessing a leaked token, key, or password.

## Threat patterns and standard mitigations

### Spoofing (authentication)
Threat patterns:
- Forged identity on an unauthenticated endpoint or webhook.
- Credential stuffing / brute force against login.
- Session hijacking or token theft/replay.
- Service impersonation (rogue server, DNS/ARP spoofing).
- Phishing leading to account takeover.

Mitigations:
- Strong authentication: MFA, WebAuthn/passkeys, OIDC/OAuth2.
- Service-to-service identity: mutual TLS, signed JWT with audience checks, SPIFFE.
- Webhook authenticity: HMAC signature + timestamp/nonce anti-replay.
- Short-lived tokens, secure cookie flags (HttpOnly, Secure, SameSite), rotation.
- Rate limiting + lockout + breached-password checks on auth.

### Tampering (integrity)
Threat patterns:
- Injection (SQL, NoSQL, OS command, LDAP, template).
- Modification of data in transit (no/weak TLS).
- Modification of data at rest (writable store, IDOR write).
- Parameter/mass-assignment tampering, insecure deserialization.
- Supply-chain tampering (dependency, build pipeline, container image).

Mitigations:
- Parameterized queries / prepared statements / ORM; strict input validation and output encoding.
- TLS 1.2+ everywhere; HSTS; certificate pinning where appropriate.
- Integrity checks: HMAC/signatures, checksums, append-only/audit storage.
- Least-privilege store credentials; row/object-level access control.
- Signed artifacts, SBOM, pinned dependencies, reproducible builds.

### Repudiation (non-repudiation)
Threat patterns:
- User denies performing a sensitive action; no log exists.
- Logs are missing, mutable, or attacker-deletable.
- Insufficient detail to attribute actions to a principal.

Mitigations:
- Comprehensive, structured audit logging of security-relevant events (who, what, when, from where).
- Tamper-evident/append-only logs; ship to a separate, access-controlled store (WORM/SIEM).
- Synchronized, trusted timestamps; correlation IDs.
- Digital signatures / receipts for high-value transactions.

### Information disclosure (confidentiality)
Threat patterns:
- Sensitive data in transit without encryption; leaked via logs, error messages, or stack traces.
- Over-broad API responses (excessive data exposure); IDOR read.
- Secrets in source, config, or environment dumps; misconfigured buckets.
- Side channels: timing, verbose errors, directory listing, metadata.

Mitigations:
- Encrypt in transit (TLS) and at rest (KMS-managed keys, field-level encryption for PII).
- Data minimization; field-level authorization; redact logs and errors.
- Secrets management (Vault/KMS/secret manager); no secrets in repo or images.
- Proper bucket/ACL config; remove verbose errors and directory listing in prod.

### Denial of service (availability)
Threat patterns:
- Volumetric flood; application-layer abuse of expensive endpoints.
- Resource exhaustion (connections, memory, file descriptors, disk).
- Algorithmic complexity (ReDoS, zip bombs, large payloads/pagination).
- Dependency outage cascading into the system.

Mitigations:
- Rate limiting, quotas, throttling, and request size limits.
- Autoscaling, load balancing, CDN/WAF, connection pool caps and timeouts.
- Input bounds, safe regex, async/queue offloading of heavy work.
- Circuit breakers, bulkheads, graceful degradation, backpressure.

### Elevation of privilege (authorization)
Threat patterns:
- Missing or broken access control (function/object level — BOLA/BFLA).
- Vertical escalation (user → admin) via flawed role checks.
- Horizontal escalation (tenant A reads tenant B) via IDOR.
- Sandbox/container escape; SSRF reaching internal services; deserialization to RCE.

Mitigations:
- Centralized, deny-by-default authorization; enforce on every request server-side.
- RBAC/ABAC with least privilege; verify object ownership/tenant on each access.
- Harden runtime: drop capabilities, seccomp, non-root, network egress controls (SSRF).
- Avoid unsafe deserialization; validate redirects; sandbox untrusted code.

## OWASP cross-reference

Map threats to OWASP Top 10 (2021) for shared vocabulary: A01 Broken Access Control (E, I), A02 Cryptographic Failures (I), A03 Injection (T), A04 Insecure Design (all), A05 Security Misconfiguration (I, E), A07 Identification & Authentication Failures (S), A08 Software & Data Integrity Failures (T), A09 Logging & Monitoring Failures (R), A10 SSRF (E, I). Use OWASP ASVS as the verification checklist for chosen mitigations.
