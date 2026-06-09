# Edge-Case Checklist

Use this to enumerate test cases before writing code. Not every item applies to every unit — pick the relevant rows for the input/output types involved.

## Universal

- Happy path (typical, valid input) → expected output.
- Minimum valid input.
- Maximum valid input.
- Just below minimum / just above maximum (off-by-one boundaries).
- Empty input (empty string, empty list, empty map, zero-length).
- Single-element input.
- Null / None / nil / undefined where the type allows it.
- Invalid type / malformed input → expected error or rejection.
- Duplicate elements.
- Already-processed / idempotency (calling twice yields same result).

## Numbers

- Zero.
- Negative numbers.
- The largest and smallest representable values (overflow/underflow).
- Floating-point precision (`0.1 + 0.2`), NaN, +Inf, -Inf, -0.0.
- Very large magnitudes; very small fractions.
- Division by zero.
- Rounding boundaries (banker's rounding vs half-up).

## Strings

- Empty string and whitespace-only string.
- Leading/trailing whitespace.
- Unicode: multibyte chars, emoji, combining characters, RTL text.
- Case sensitivity.
- Very long strings.
- Strings with delimiters/escape chars relevant to the parser (quotes, commas, newlines, backslashes).
- Injection-shaped input where relevant (SQL/HTML/shell) — confirm it is treated as data.
- Encoding edge cases (UTF-8 vs latin-1, BOM).

## Collections (list/array/set/map)

- Empty, one element, many elements.
- Ordering: sorted, reverse-sorted, random, all-equal.
- Duplicates and uniqueness handling.
- Nested/deeply nested structures.
- Mutation during iteration (should it be allowed?).
- Very large collections (performance/memory boundaries when relevant).
- Heterogeneous element types (in dynamic languages).

## Dates & Time

- Timezone boundaries (UTC vs local), DST transitions.
- Leap years (Feb 29), leap seconds, end-of-month/year.
- Epoch boundaries, far-future/far-past dates.
- Same instant in different timezones.
- ALWAYS inject or freeze the clock — never read the real system time in assertions.

## Errors & Exceptions

- Each distinct error/exception the unit can raise has its own test.
- Assert the specific exception type AND the message/code, not a generic catch.
- Error during cleanup / partial failure (resource left in valid state?).
- Wrapped/chained exceptions preserve the cause.
- Retryable vs non-retryable error classification.

## Concurrency (when relevant)

- Two callers racing on shared state.
- Re-entrancy.
- Cancellation / timeout mid-operation.
- Deterministic scheduling — avoid `sleep`; use synchronization primitives or fake schedulers.

## State & Side Effects

- Side effect happens exactly once (not zero, not twice).
- Side effect is NOT performed on the error path (or is rolled back).
- Output does not mutate the input arguments (unless documented).
- Resource is released (file/connection closed) even on failure.

## Property-based testing

When an invariant should hold across a large input space, prefer property-based tests over enumerating examples. Common properties:

- **Round-trip:** `decode(encode(x)) == x`.
- **Idempotence:** `f(f(x)) == f(x)` (e.g. normalization, sort, dedupe).
- **Commutativity / associativity** for combiners.
- **Invariance:** sorting preserves length and multiset of elements.
- **Oracle:** result matches a slow-but-obviously-correct reference implementation.
- **Metamorphic:** relationship between outputs of related inputs (e.g. `f(x) <= f(x+1)` for monotonic functions).

Tooling: Hypothesis (Python), fast-check (JS/TS), `testing/quick` or gopter (Go), jqwik (Java), proptest/quickcheck (Rust), PropCheck/PBT (Ruby). Always set a fixed seed in CI and print the minimal failing (shrunk) example.
