---
name: secure-password-policy
description: Defines modern authentication and password policies aligned with NIST SP 800-63B, covering minimum length, blocklist/breach screening, rate limiting, MFA, password storage hashing, and account recovery. Use this skill when asked to "write a password policy", "review our authentication requirements", "implement NIST 800-63B", "decide password complexity rules", "configure password hashing", "set up MFA requirements", or audit an existing login/signup flow for security.
license: MIT
---

# Secure Password Policy (NIST SP 800-63B)

## Overview

This skill produces and reviews authentication and password policies that follow current
NIST Digital Identity Guidelines (SP 800-63B) rather than legacy "complexity rule" folklore.
The modern consensus inverts much of the 2003-era advice: favor LONG passphrases, screen
against breach/blocklists, drop forced periodic rotation, drop composition rules, and lean on
phishing-resistant MFA plus strong server-side hashing.

Keywords: password policy, NIST 800-63B, authentication, AAL, memorized secret, passphrase,
password length, breach screening, Have I Been Pwned, password complexity, password rotation,
MFA, 2FA, TOTP, WebAuthn, passkeys, rate limiting, account lockout, Argon2, bcrypt, scrypt,
PBKDF2, password storage, salt, pepper, credential stuffing, account recovery, password reset.

Use this skill to: author a policy document, translate it into concrete engineering
requirements, choose a password hashing configuration, or audit a sign-in flow.

## Core Principles (the NIST inversion)

| Topic | Legacy advice (avoid) | NIST 800-63B (adopt) |
|-------|----------------------|----------------------|
| Length | 8 chars | Min 8, recommend 12-15+; allow at least 64 |
| Composition | Require upper/lower/digit/symbol | Do NOT impose composition rules |
| Allowed chars | Restrict symbols | Allow all printable ASCII + Unicode + spaces |
| Rotation | Force change every 60-90 days | Do NOT force periodic change; rotate only on evidence of compromise |
| Hints / security questions | Allowed | Prohibited as authenticators |
| Breach check | None | Screen against known-compromised/blocklist values |
| Truncation | Common | Never silently truncate; accept full input |
| Paste in password fields | Blocked | Always allow paste (supports password managers) |
| Show password | Hidden always | Offer "show password" toggle |

The single highest-leverage controls are: (1) breach/blocklist screening at set-time,
(2) a strong, salted, memory-hard hash for storage, (3) rate limiting + MFA against
online guessing. Composition rules and forced rotation actively hurt usability with little
security gain.

## Workflow

1. **Determine the assurance level (AAL).** Decide whether the system needs AAL1
   (single factor acceptable), AAL2 (MFA required), or AAL3 (hardware-based,
   phishing-resistant). See `references/nist-800-63b.md` for the decision criteria.
   Higher-risk data (PII, financial, admin) => AAL2 minimum.

2. **Set memorized-secret (password) rules.** Apply the table above. Fix minimum length
   (>=8 hard floor, 12+ recommended), allow >=64 max, allow all Unicode, no composition
   rules, no truncation, allow paste and show-password.

3. **Add breach + blocklist screening.** At account creation and password change, reject
   values that appear in: known-breach corpora (e.g. Have I Been Pwned k-anonymity API),
   dictionary words, context-specific terms (site name, username, email local-part), and
   repetitive/sequential strings. Use `scripts/check_password.py` to prototype this.

4. **Choose password storage.** Select a memory-hard KDF and parameters. Argon2id is the
   first choice; bcrypt/scrypt/PBKDF2 acceptable with correct cost. Add a unique per-user
   salt (the KDF handles this) and consider an application-wide pepper in a secret store.
   See the parameters table in `references/password-storage.md`.

5. **Define rate limiting & account protection.** Throttle by IP and by account, add
   exponential backoff, CAPTCHA after N failures, and prefer soft lockouts over permanent
   ones (to avoid DoS). Limit failed attempts to 100 per account per 30 days (NIST guidance).

6. **Require MFA appropriately.** Map AAL2+ flows to MFA. Prefer phishing-resistant
   factors (WebAuthn/passkeys, FIDO2) > authenticator apps (TOTP) > push > SMS (last resort).
   Never use SMS for high-value or admin accounts.

7. **Secure recovery & reset.** No security questions. Use time-boxed, single-use,
   high-entropy reset tokens delivered out-of-band; re-verify identity; invalidate sessions
   on password change; rate-limit reset requests.

8. **Document and codify.** Fill in `templates/password-policy.md` for the human-readable
   policy, then translate each clause into testable engineering acceptance criteria.

## Decision Framework: how strict?

- **Public consumer app, low-risk data:** AAL1, 8+ char min (12 recommended), breach screen,
  Argon2id, rate limiting, optional MFA, allow passkeys.
- **App with PII / payments / accounts:** AAL2, 12+ recommended, breach screen, MFA required,
  phishing-resistant MFA encouraged, session timeouts.
- **Admin / privileged / regulated:** AAL3, hardware MFA (FIDO2) required, short reauth
  windows, no SMS, full audit logging.

## Length vs. complexity (worked reasoning)

A 16-character random passphrase of common words ("correct-horse-battery-staple") has more
guessing entropy than "P@ssw0rd1!" while being far more memorable. Composition rules push
users toward predictable substitutions (a=@, o=0) that attackers' rules already model.
Length + breach screening defeats both dictionary and credential-stuffing attacks more
effectively than composition. See `examples/policy-review.md` for a before/after audit.

## Best Practices

- Screen EVERY new and changed password against a breach list; do it with k-anonymity so the
  full password never leaves the client/server boundary in plaintext.
- Store only the output of a slow, salted, memory-hard KDF — never plaintext, never fast
  hashes (MD5/SHA-1/SHA-256 alone), never reversible encryption.
- Tune KDF cost so a single hash takes ~250-500 ms on your production hardware; re-tune yearly.
- Support and encourage password managers: allow paste, long values, all characters.
- Offer and promote passkeys (WebAuthn) — they eliminate the password entirely for many flows.
- Rotate passwords only on evidence of compromise, plus offer voluntary change anytime.
- Invalidate all active sessions when a password is changed or reset.
- Log authentication events (success/failure, MFA, resets) for detection — never log secrets.
- Send a notification email on password/MFA change and on new-device sign-in.

## Common Pitfalls

- Forcing periodic rotation: leads to weak, incremental passwords (Spring2026! -> Summer2026!).
- Composition rules: reduce entropy and frustrate users without stopping modern attacks.
- Silent truncation: user types 30 chars, system stores 16 — login later fails or weakens hash.
- Blocking paste / capping length too low: breaks password managers, pushes weaker passwords.
- Using fast hashes or unsalted hashes: rainbow-table and GPU-cracking exposure.
- SMS as the only MFA: vulnerable to SIM-swap and interception; never for admin.
- Security questions: answers are guessable or publicly discoverable (OSINT); prohibited.
- Permanent account lockout on failures: enables trivial denial-of-service against users.
- Revealing whether the username or the password was wrong: aids account enumeration.
- Storing a single global salt or no salt: defeats the purpose of per-credential hashing.

## Bundled files

- `references/nist-800-63b.md` — AAL definitions, requirement checklist, control mapping.
- `references/password-storage.md` — KDF comparison and recommended parameters.
- `scripts/check_password.py` — runnable stdlib policy + HIBP k-anonymity checker.
- `templates/password-policy.md` — fill-in human-readable policy template.
- `examples/policy-review.md` — worked audit of a legacy policy mapped to NIST.
