---
name: unit-test-author
description: Writes thorough, maintainable unit tests with comprehensive edge cases, table-driven cases, proper mocking/stubbing, and meaningful coverage across languages and frameworks (pytest, Jest/Vitest, Go testing, JUnit, RSpec, xUnit, Rust). Use this skill when the user asks to "write tests", "add unit tests", "improve coverage", "test this function/class/module", "add edge cases", "mock this dependency", "make these tests table-driven", "test error handling", or wants a test plan before implementing. Covers test naming, AAA structure, fixtures, parametrization, mocking strategy, async tests, property-based testing, and avoiding brittle/flaky tests.
license: MIT
---

# Unit Test Author

## Overview

This skill produces unit tests that are **correct, behavior-focused, exhaustive on edge cases, and resistant to brittleness**. It applies across languages and frameworks and emphasizes testing observable behavior over implementation details.

Keywords: unit test, test coverage, edge cases, table-driven, parametrize, mock, stub, spy, fake, fixture, AAA arrange-act-assert, flaky test, property-based, snapshot, regression test, pytest, Jest, Vitest, Go test, JUnit, RSpec, xUnit, NUnit, Rust test.

Use this skill whenever the goal is to create or strengthen unit tests for a specific function, class, or module — not for end-to-end or load testing.

## Core Principles

1. **Test behavior, not implementation.** Assert on outputs, return values, raised errors, and observable side effects — never on private internals that can change without breaking the contract.
2. **One logical concept per test.** A test may have several assertions, but they should all verify a single behavior. If a test name needs "and", split it.
3. **Deterministic always.** No real clocks, randomness, network, filesystem, or ordering assumptions unless explicitly under test. Inject or freeze them.
4. **Arrange-Act-Assert (AAA).** Visually separate setup, the single action, and verification. Keep the "act" to one call.
5. **Fail for one reason.** When a test fails the message should point to the cause. Prefer precise assertions over `assertTrue(x == y)`.
6. **Cover the contract, then the edges.** Happy path first, then boundaries, then error/exception paths.

## Workflow

Follow these steps in order. Do not skip step 1 — understanding the unit under test prevents tautological tests.

1. **Identify the unit and its contract.** Read the function/class. List: inputs (types, ranges), outputs, raised errors, side effects, and dependencies (collaborators to mock).
2. **Detect the framework and conventions.** Inspect the repo: test directory layout, existing test files, the runner (`package.json` scripts, `pytest.ini`/`pyproject.toml`, `go.mod`, `pom.xml`, `Cargo.toml`), assertion library, and mocking library already in use. **Match existing conventions.** See `references/frameworks.md`.
3. **Enumerate test cases** using the edge-case checklist in `references/edge-cases.md`. Produce a short list before writing code (happy path, boundaries, empties, nulls, errors, concurrency if relevant).
4. **Choose a structure.** When many inputs map to one behavior, use table-driven / parametrized tests (see `references/table-driven.md`). Otherwise, individual named tests.
5. **Plan the test double strategy** for each dependency (mock vs stub vs fake vs spy) using the decision guide in `references/mocking.md`. Mock at architectural boundaries (network, DB, time, randomness), not internal pure functions.
6. **Write the tests** with descriptive names (`method_condition_expectedResult`), AAA layout, and precise assertions.
7. **Add error-path and edge tests** explicitly — these are most often missing.
8. **Run the tests** and ensure they pass. Then sanity-check quality with `scripts/check_tests.py` (heuristic linter for missing assertions, skipped tests, sleep-based timing, etc.).
9. **Verify they actually test something:** mentally (or literally) mutate the implementation and confirm a test would fail. Tests that pass against a broken implementation are worthless.

## Test Naming

Pick the convention that matches the codebase. Default patterns:

- `test_<unit>_<condition>_<expected>` (pytest/Go): `test_withdraw_insufficient_funds_raises`
- `should <do X> when <condition>` (Jest/RSpec describe/it): `it("returns 0 when the cart is empty")`
- `Method_State_Behavior` (xUnit/JUnit): `Withdraw_AmountExceedsBalance_ThrowsException`

The name must state the **condition** and the **expected outcome**, not just the method name.

## Coverage Targets

Coverage is a floor, not a goal. Aim for:
- **100% of branches in pure business logic** (the actual rules).
- Every `raise`/`throw`/error return has a dedicated test.
- Every boundary value (see edge-case checklist) is exercised.
- Do **not** chase coverage by testing trivial getters/setters, generated code, or framework glue.

Use coverage tooling to find untested branches, then write *meaningful* tests for them — never assertion-free tests that merely execute lines.

## Decision Frameworks

**When to use a table/parametrized test:** the same assertion logic runs over ≥3 input/output pairs. See `references/table-driven.md`.

**Mock vs Stub vs Fake vs Spy:** see the decision table in `references/mocking.md`. Quick rule: stub for inputs you read, mock/spy for interactions you must verify, fake for stateful collaborators (in-memory repo), and never mock the system under test.

**Property-based vs example-based:** use property-based testing when invariants hold over a large input space (round-trips, idempotence, commutativity, ordering). See `references/edge-cases.md` § Property-based.

## Best Practices

- Keep tests independent and order-agnostic; no shared mutable state between tests.
- Freeze time and seed randomness; inject clocks and RNGs.
- Prefer fakes/in-memory implementations over deep mock chains.
- Use builders/factories or fixtures for complex setup; keep each test's intent readable.
- Assert on specific error types and messages, not just "an error occurred".
- Name the variable under assertion clearly (`actual`, `result`) vs `expected`.
- Test one public behavior per test; let coverage of private code fall out naturally.
- Make failure messages diagnostic (most modern frameworks do this automatically with rich equality).

## Common Pitfalls

- **Asserting on implementation details** (call order of internal helpers, private fields) → brittle tests that break on refactors.
- **Over-mocking** so the test only verifies the mocks, not real behavior (tautological tests).
- **No edge cases** — only the happy path. The checklist exists to prevent this.
- **Non-deterministic tests** using `sleep`, real time, network, or unseeded random → flaky.
- **Hidden coupling** between tests via global/module state.
- **Tests that can't fail** — no assertions, or asserting `true == true`.
- **Snapshot abuse** — giant snapshots that everyone blindly updates.
- **Testing the framework or the language** instead of your logic.

## Bundled Resources

- `references/edge-cases.md` — exhaustive edge-case checklist by data type, plus property-based testing guidance.
- `references/mocking.md` — test double taxonomy and a mock/stub/fake/spy decision table with per-language tooling.
- `references/frameworks.md` — idioms, runners, and skeletons for pytest, Jest/Vitest, Go, JUnit, RSpec, xUnit, and Rust.
- `references/table-driven.md` — table-driven / parametrized patterns in each major language.
- `examples/worked-example.md` — a full worked example: source function → test plan → table-driven tests with edge cases and mocking.
- `templates/test-plan.md` — fill-in test plan to enumerate cases before coding.
- `scripts/check_tests.py` — heuristic linter that flags assertion-free tests, skipped tests, sleep-based timing, and focused/`.only` tests left in.
