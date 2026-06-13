# Worked Example: Email Validation, Naive vs. Safe

## Request
"Write a regex to validate an email address in a signup form. We use Python on the
backend. Show me it's not vulnerable to slow inputs."

## Step 1 - Clarify (answers assumed for this example)
- Flavor: Python `re`.
- Operation: validation (whole string) → use `re.fullmatch`, anchored.
- Valid: `ada@example.com`, `a.b+tag@sub.example.co.uk`.
- Invalid: `no-at-sign`, `a@b`, `a@@b.com`, `space @x.com`.
- Input is untrusted (public form) → must be ReDoS-safe.
- Note up front: regex cannot fully validate RFC 5322; for production, also send a
  confirmation email. This pragmatic pattern is fine for form-level checks.

## Step 2 - A tempting but DANGEROUS draft
```
^([a-zA-Z0-9]+)*@([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}$
```
The `([a-zA-Z0-9]+)*` is a **nested quantifier** (a `+` group wrapped in `*`).
Against `"a" * 30 + "!"` the engine explores exponentially many splits. This is a
classic ReDoS.

## Step 3 - Safe rewrite
```
^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$
```
- Single, flat quantifiers — no group is repeated.
- Negated/explicit classes only; no overlapping alternation.
- Anchored with `^`/`$` and used via `re.fullmatch` for whole-string semantics.

Token breakdown:
- `^` start of string.
- `[A-Za-z0-9._%+-]+` local part: one or more allowed chars.
- `@` literal at-sign.
- `[A-Za-z0-9.-]+` domain labels and dots.
- `\.` a literal dot before the TLD.
- `[A-Za-z]{2,}` TLD of at least two letters.
- `$` end of string.

## Step 4 - Test it
Functional cases:
```
python3 scripts/regex_test.py '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' \
  --match 'ada@example.com' \
  --match 'a.b+tag@sub.example.co.uk' \
  --no-match 'no-at-sign' \
  --no-match 'a@b' \
  --no-match 'a@@b.com' \
  --no-match 'space @x.com'
```
Expected output:
```
== Functional tests ==
  [PASS] should MATCH    : 'ada@example.com'
  [PASS] should MATCH    : 'a.b+tag@sub.example.co.uk'
  [PASS] should NOT match: 'no-at-sign'
  [PASS] should NOT match: 'a@b'
  [PASS] should NOT match: 'a@@b.com'
  [PASS] should NOT match: 'space @x.com'
  6 passed, 0 failed
```

ReDoS probe on the SAFE pattern (stays fast):
```
python3 scripts/regex_test.py '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' --redos
```
Expected: all timings a fraction of a millisecond, `RESULT: OK`.

ReDoS probe on the DANGEROUS draft (blows up):
```
python3 scripts/regex_test.py '^([a-zA-Z0-9]+)*@([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}$' --redos
```
Expected: timings climb sharply and the run stops early with
`RESULT: RISK - timing grows super-linearly. Rewrite the pattern.`

## Step 5 - Deliverable to the user
- Pattern: `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$`
- Usage: `re.fullmatch(pattern, candidate) is not None`.
- Caveats: pragmatic, not full RFC 5322; cap input length (e.g., 254 chars) and
  send a confirmation email for real verification.
- ReDoS: verified linear-time via the probe.

## Portability note
For JavaScript, the same pattern works as `/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/`
with `.test(candidate)` (anchors give whole-string semantics without the `m` flag).
For Go/Rust (RE2) it is also fine — it uses no lookarounds or backreferences.
