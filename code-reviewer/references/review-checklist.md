# Master Code Review Checklist

Use this as the primary pass over a diff. Work top to bottom per changed hunk. Not every item applies to every change; skip the irrelevant ones quickly.

## 1. Correctness

### Logic & control flow
- [ ] Conditionals cover all branches; no impossible/unreachable branch.
- [ ] Boolean logic is correct (no inverted condition, no `&&`/`||` mix-up, De Morgan errors).
- [ ] Loop bounds correct; no off-by-one (`<` vs `<=`, `len` vs `len-1`).
- [ ] Early returns don't skip required cleanup or leave state half-updated.
- [ ] `switch`/`match` has a default/else and handles new enum cases.
- [ ] Recursion has a base case and bounded depth.

### Null / empty / boundary
- [ ] Null/None/undefined handled before dereference or method call.
- [ ] Empty collection, single element, and max-size cases behave correctly.
- [ ] Integer overflow/underflow and float precision considered where it matters.
- [ ] String edge cases: empty, unicode, very long, leading/trailing whitespace.
- [ ] Division/modulo guarded against zero.
- [ ] Array/slice indexing guarded against out-of-bounds.

### Error handling
- [ ] Errors are caught at the right level, not swallowed silently.
- [ ] `catch`/`except` doesn't hide the original cause; errors are wrapped/logged.
- [ ] Resources (files, sockets, locks, DB connections) released on every path, including error paths (use RAII / `with` / `defer` / `try-finally`).
- [ ] Retries are bounded and idempotent; no infinite retry.
- [ ] Partial failures leave the system in a consistent state.
- [ ] Return values / error codes are actually checked by callers.

### Concurrency
- [ ] Shared mutable state is protected (lock, atomic, immutable, single-owner).
- [ ] No data races on read-modify-write (counters, caches, maps).
- [ ] No deadlock: consistent lock ordering; no lock held across blocking/IO calls.
- [ ] `async`/`await` / promises: no missing `await`, no unhandled rejection, no fire-and-forget that must complete.
- [ ] Thread-unsafe types not shared across threads.

### Contracts & regressions
- [ ] Public function signature/behavior changes are backward compatible or all callers updated.
- [ ] Return type/shape unchanged unless intended; serialized formats stable.
- [ ] Pre/postconditions and invariants preserved.
- [ ] No accidental behavior change to unrelated code paths.
- [ ] Feature flags / config defaults are safe.

### Data & state
- [ ] DB migrations are reversible or have a rollback plan; no destructive change without backup.
- [ ] Migrations handle existing rows (defaults, NULLs, large-table locking).
- [ ] Time handling uses correct timezone/UTC; no naive local-time bugs.
- [ ] Money/quantity uses fixed-point/decimal, not float.
- [ ] Caching: keys are correct and unique; invalidation happens on write.

## 2. Quality & Maintainability

### Readability
- [ ] Names reveal intent; no misleading or abbreviated names.
- [ ] Functions do one thing; long functions are split where it aids clarity.
- [ ] Nesting is shallow; complex conditions extracted to named variables/functions.
- [ ] Magic numbers/strings replaced with named constants.
- [ ] Comments explain *why*, not *what*; no stale/contradictory comments.

### Design
- [ ] No duplicated logic that should be shared (DRY) — but not over-abstracted.
- [ ] Abstractions don't leak implementation details.
- [ ] Dependencies point the right direction; no new circular dependency.
- [ ] Public API surface is minimal; internals not exported unnecessarily.
- [ ] No dead code, commented-out code, or unused imports/vars introduced.

### Tests
- [ ] New logic has tests covering the main branch and key edge cases.
- [ ] Tests assert behavior, not implementation; no tautological asserts.
- [ ] Tests are deterministic (no reliance on time, ordering, network, randomness).
- [ ] Bug fixes include a regression test that fails without the fix.
- [ ] Test names describe the scenario.

### Performance (only when it matters)
- [ ] No N+1 queries; batch where possible.
- [ ] No accidental O(n^2) over large inputs; appropriate data structures.
- [ ] No unbounded memory growth (unbounded cache, leak, large in-memory list).
- [ ] Expensive work not done in a hot loop or per-request when it could be cached.
- [ ] Pagination/streaming for large result sets.

### Observability & ops
- [ ] Adequate logging at decision points and error paths (no secrets in logs).
- [ ] Metrics/tracing for new critical paths where the team uses them.
- [ ] Error messages are actionable.

## 3. Language-Specific Smells

### Python
- Mutable default arguments (`def f(x=[])`).
- Bare `except:` catching everything including `KeyboardInterrupt`.
- Comparing with `==` to `None`/`True`/`False` instead of `is`.
- f-strings or `%` for SQL (injection) instead of parameterized queries.
- Iterating and mutating the same collection.

### JavaScript / TypeScript
- `==` vs `===`; truthiness bugs with `0`, `""`, `null`.
- Missing `await`; floating promises.
- `any` defeating the type system; unsafe casts.
- Array mutation where immutability expected (React state).
- `for...in` over arrays.

### Go
- Ignored errors (`_ =` or unassigned).
- Loop variable capture in goroutines/closures (pre-1.22).
- `defer` in a loop accumulating until function return.
- Nil map writes; nil pointer deref on interface.

### Java / Kotlin / C#
- Resource not in try-with-resources / `using`.
- `equals`/`hashCode` mismatch.
- Catching and ignoring `Exception`.
- Mutable shared static state.

### SQL
- Missing index for new query predicate.
- `SELECT *` in production code paths.
- Unparameterized dynamic SQL.
- Missing `WHERE` on `UPDATE`/`DELETE`.

## 4. Quick Triage Order

When time-boxed, review in this order for max value:
1. Error/exception paths and cleanup.
2. Trust boundaries (input handling, auth).
3. Concurrency / shared state.
4. Data migrations and persisted formats.
5. The happy path.
6. Style and naming.
