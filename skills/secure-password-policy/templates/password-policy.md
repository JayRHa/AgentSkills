# Password & Authentication Policy — <ORGANIZATION / SYSTEM NAME>

- Owner: <name / role>
- Effective date: <YYYY-MM-DD>
- Review cadence: <annually>
- Aligned to: NIST SP 800-63B
- Target Authenticator Assurance Level (AAL): <AAL1 | AAL2 | AAL3>

## 1. Scope

This policy applies to <all user accounts | employees | customers | service accounts>
for <system / application>. Service and machine accounts are governed by <section / link>.

## 2. Password requirements

- Minimum length: <8 (recommend 12)> characters.
- Maximum length: at least 64 characters accepted; no silent truncation.
- Permitted characters: all printable ASCII, the space character, and Unicode.
- Composition rules: NONE imposed (no required mix of character types).
- Periodic rotation: NOT required. Passwords are changed only on evidence of compromise
  or at the user's discretion.
- Screening: every new or changed password is rejected if it appears in the breach
  corpus, the common-password blocklist, contains context-specific terms
  (<site name>, username, email local-part), or consists of repetitive/sequential runs.
- Usability: paste is allowed in password fields; a show-password toggle is provided.

## 3. Storage

- Algorithm: <Argon2id | scrypt | bcrypt | PBKDF2-HMAC-SHA256>.
- Parameters: <e.g. Argon2id m=19456 KiB, t=2, p=1> (tuned to ~<300> ms/verify).
- Salt: unique per credential, >= 16 bytes (embedded in PHC string).
- Pepper: <yes/no — stored in <KMS / secret manager>>.
- Plaintext or reversible storage of passwords is prohibited.
- Parameters are reviewed <annually> and credentials are transparently re-hashed on login
  when below current targets.

## 4. Multi-factor authentication

- MFA is <required | required for AAL2+ flows | optional>.
- Accepted factors, in preference order: <WebAuthn/passkeys, TOTP, push w/ number
  matching, SMS (last resort)>.
- SMS is <prohibited | discouraged> for privileged and high-value accounts.
- Biometrics may be used only as part of multi-factor authentication.

## 5. Rate limiting & account protection

- Failed attempts are throttled per IP and per account with exponential backoff.
- <CAPTCHA | step-up> is required after <N> consecutive failures.
- No more than <100> failed attempts per account per <30 days>.
- Permanent lockout is NOT used; soft lock of <duration> applies instead.
- Error messages are generic and do not reveal account existence or which field was wrong.

## 6. Account recovery & reset

- Reset tokens are single-use, high-entropy, and expire after <15-60 minutes>.
- Tokens are delivered out-of-band via <email / verified channel>.
- Security questions are NOT used.
- All active sessions are invalidated on password change or reset.
- Reset requests are rate-limited; account existence is not disclosed.

## 7. Logging, monitoring & notifications

- Authentication events (success, failure, MFA, reset) are logged WITHOUT secrets.
- Users are emailed on password/MFA change and on new-device sign-in.
- Anomalies (credential stuffing, spikes in failures) trigger <alert / response>.

## 8. Exceptions

Exceptions require documented approval from <role> and a compensating control and
expiry date. Track exceptions in <register / link>.
