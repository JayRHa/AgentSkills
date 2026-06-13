# Worked Example — Auditing a Legacy Password Policy Against NIST 800-63B

## Input: an existing (legacy) policy

> 1. Passwords must be 8-16 characters.
> 2. Must contain at least one uppercase, one lowercase, one number, and one symbol.
> 3. Cannot contain spaces.
> 4. Must be changed every 90 days; cannot reuse the last 5 passwords.
> 5. Account locks permanently after 3 failed attempts; call the help desk to unlock.
> 6. To reset, answer two security questions.
> 7. Passwords stored hashed with SHA-256.
> 8. SMS one-time code required as second factor.

## Audit findings (mapped to NIST 800-63B)

| # | Clause | Verdict | Why | Fix |
|---|--------|---------|-----|-----|
| 1 | 8-16 length cap | Change | Max 16 blocks passphrases & truncates manager output | Min 8 (recommend 12), accept >=64, never truncate |
| 2 | Composition rules | Remove | NIST prohibits imposed composition; pushes predictable patterns | Drop entirely; rely on length + breach screening |
| 3 | No spaces | Remove | All printable + space + Unicode must be allowed | Allow spaces and Unicode |
| 4 | 90-day rotation + history | Change | Forced rotation yields weak incremental passwords | Rotate only on compromise; offer voluntary change |
| 5 | Permanent lockout after 3 | Fix | Enables denial-of-service; threshold too low | Soft lock + backoff + CAPTCHA; up to ~100 failures/30d |
| 6 | Security questions | Remove | Prohibited as authenticators (OSINT-guessable) | Single-use, time-boxed out-of-band reset tokens |
| 7 | SHA-256 storage | Critical | Fast hash, GPU-crackable, salt unspecified | Argon2id (or bcrypt/scrypt/PBKDF2) salted, tuned cost |
| 8 | SMS 2FA | Improve | SMS is "restricted"; SIM-swap risk | Offer passkeys/TOTP first; SMS last resort, never for admin |

## Output: revised policy clauses

> 1. Passwords must be at least 12 characters; up to 64+ characters are accepted and
>    never truncated. All printable characters, spaces, and Unicode are allowed.
> 2. No character-composition rules are imposed.
> 3. Every new or changed password is screened against breach corpora (HIBP),
>    a common-password blocklist, context terms (service name, username, email), and
>    repetitive/sequential patterns; matches are rejected with a reason.
> 4. Passwords are not rotated on a schedule; users may change them anytime and are
>    required to change only on evidence of compromise.
> 5. Sign-in is rate-limited per IP and account with exponential backoff; CAPTCHA or
>    step-up triggers after repeated failures; a time-boxed soft lock replaces the
>    permanent lock. Error messages are generic.
> 6. Recovery uses single-use, 30-minute, high-entropy reset links sent out-of-band;
>    security questions are removed; all sessions are invalidated on reset.
> 7. Passwords are stored using Argon2id (m=19456 KiB, t=2, p=1, per-user salt, app
>    pepper in the secret manager), re-hashed transparently when below current targets.
> 8. MFA is required: passkeys/WebAuthn preferred, then TOTP; SMS is a last resort and
>    is not permitted for administrative or high-value accounts.

## Verifying a candidate password with the bundled script

```
$ echo -n 'Spring2026!' | python3 scripts/check_password.py --stdin --min-length 12 --context acme
REJECTED:
  - too short: 11 chars (minimum 12).
  - found in N known breaches (HIBP). Choose another.

$ echo -n 'glacier-tractor-meadow-quartz' | python3 scripts/check_password.py --stdin --min-length 12
note: not found in HIBP breach corpus.
note: length >= 15 — strong; passphrases of this length are encouraged.
ACCEPTED: password meets NIST 800-63B screening.
```
