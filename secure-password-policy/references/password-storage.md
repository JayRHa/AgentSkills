# Password Storage — KDF Selection and Parameters

Never store passwords in plaintext, reversibly encrypted, or under a fast general-purpose
hash (MD5, SHA-1, SHA-256/512 on their own). Use a deliberately slow, salted, memory-hard
key derivation function (KDF). Each stored credential gets a unique random salt (handled by
the KDF). Optionally add an application-wide secret "pepper" kept outside the database.

## Recommended order of preference

1. **Argon2id** — first choice. Memory-hard, resists GPU/ASIC cracking, side-channel aware.
2. **scrypt** — strong memory-hard alternative where Argon2 is unavailable.
3. **bcrypt** — well-vetted; note its 72-byte input limit (pre-hash with SHA-256 if you
   must accept longer inputs, then base64-encode before bcrypt to avoid NUL issues).
4. **PBKDF2** — acceptable for FIPS-constrained environments; use HMAC-SHA-256 and high
   iteration counts. Least resistant to hardware acceleration.

## Suggested baseline parameters (tune to ~250-500 ms per hash on prod hardware)

| KDF | Parameters (starting point) |
|-----|-----------------------------|
| Argon2id | memory = 19 MiB (19456 KiB) or higher, iterations (t) = 2-3, parallelism (p) = 1; scale memory up to 64+ MiB on capable servers |
| scrypt | N = 2^17 (131072), r = 8, p = 1 (raise N as hardware allows) |
| bcrypt | cost (work factor) = 12 or higher |
| PBKDF2-HMAC-SHA256 | iterations >= 600000 |

These are conservative 2024+ baselines aligned with OWASP guidance. Benchmark on your own
hardware and increase until a single verification takes a few hundred milliseconds; record
the parameters alongside the hash so they can be upgraded over time.

## Salt and pepper

- **Salt:** unique, random, >=16 bytes, stored with the hash. Modern KDF encodings embed it.
- **Pepper:** a single secret value applied to all passwords (e.g. HMAC the password with a
  key, or pass it as Argon2 "secret"), stored in a KMS/HSM/secret manager — never in the DB.
  A leaked database alone is then insufficient to mount offline attacks.

## Upgrading hashes over time

Store the algorithm and parameters in the hash string (PHC string format does this:
`$argon2id$v=19$m=19456,t=2,p=1$<salt>$<hash>`). On successful login, if the stored
parameters are weaker than the current target, transparently re-hash the supplied password
with the new parameters and update the record.

## Anti-patterns

- Single global salt, or salt derived from username — defeats per-credential uniqueness.
- Fast hashes (raw SHA family, MD5) — crackable at billions/sec on commodity GPUs.
- Reversible encryption — a key compromise exposes every password.
- Double-hashing fast functions to "slow it down" — not memory-hard; still GPU-friendly.
- Truncating input before hashing — silently weakens long passwords.

## Example: Argon2id in Python (argon2-cffi)

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(memory_cost=19456, time_cost=2, parallelism=1)
stored = ph.hash("correct horse battery staple")  # PHC string, salt embedded

try:
    ph.verify(stored, candidate)
    if ph.check_needs_rehash(stored):
        stored = ph.hash(candidate)  # upgrade params transparently
except VerifyMismatchError:
    ...  # reject
```
