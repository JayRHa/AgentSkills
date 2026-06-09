---
name: refactoring-guide
description: Applies safe, incremental, behavior-preserving refactorings (extract function/variable, rename, inline, decompose conditionals, remove duplication, replace conditional with polymorphism, introduce parameter object) using a test-protected, small-step workflow. Use this skill when the user asks to "refactor", "clean up", "simplify", "extract a method/function", "rename", "remove duplication", "reduce nesting", "break up a god class/long function", "improve readability", "untangle" code, "make this testable", "reduce complexity", or "tidy up" without changing what the code does. Covers code smell detection, choosing the right refactoring, and verifying behavior is unchanged.
license: MIT
---

# Refactoring Guide

## Overview

Refactoring is changing the internal structure of code **without changing its observable behavior**. The goal is readability, maintainability, and testability — never new features and never bug fixes in the same step.

Keywords: refactor, clean up, simplify, extract function, extract method, extract variable, inline, rename, remove duplication, reduce nesting, decompose conditional, guard clause, god class, long function, code smell, DRY, separation of concerns, make testable, reduce cyclomatic complexity.

The two non-negotiable rules:

1. **Behavior must not change.** No new functionality, no bug fixes, no API changes in a refactoring commit. If you spot a bug, note it and fix it in a **separate** commit.
2. **Tests stay green at every step.** Refactor in small steps; run tests after each. If there are no tests, write characterization tests first (see `references/characterization-tests.md`).

When the task mixes refactoring with feature work, separate them: "make the change easy (this may be hard), then make the easy change." Refactor first, commit, then build the feature.

## Workflow

Follow this loop. Do **not** batch many changes before testing.

1. **Establish a safety net.**
   - Find and run the existing test suite. Confirm it passes *before* you touch anything.
   - If coverage of the target code is weak or absent, write characterization tests that pin current behavior (including current quirks). See `references/characterization-tests.md`.
   - Identify how to run the tests fast (single file / single test) so the inner loop is quick.

2. **Identify the smell and pick ONE refactoring.**
   - Scan the target code against the smell catalog in `references/code-smells.md`.
   - Map the smell to a refactoring using the table in `references/refactoring-catalog.md`.
   - Choose the smallest refactoring that improves the worst problem first. Resist doing everything at once.

3. **Apply the smallest mechanical step.**
   - Prefer automated/IDE refactorings (rename, extract) — they are safer than hand edits.
   - Follow the mechanics in `references/refactoring-catalog.md` step by step.
   - Keep each edit tiny: one extraction, one rename, one guard clause.

4. **Run the tests.**
   - Green → commit (or stage) immediately with a clear message like `refactor: extract calculateTax from invoiceTotal`.
   - Red → revert this step (don't debug a half-refactor). Take a smaller step.

5. **Repeat** until the smell is gone and the code reads clearly.

6. **Final verification.**
   - Run the full test suite, linters, and type checker.
   - Run `scripts/refactor_check.sh <paths>` to confirm public API surface and signatures are unchanged.
   - Diff-review: every change should be structure-only. Anything that alters output is a red flag.

## Decision Framework: which refactoring?

| If you see... | Apply | Mechanics |
|---|---|---|
| A long function doing several things | Extract Function | catalog §1 |
| A cryptic expression | Extract Variable (explaining variable) | catalog §2 |
| Deep `if/else` nesting | Replace Nested Conditional with Guard Clauses | catalog §4 |
| Same code in 2+ places | Extract Function + call it (DRY) | catalog §1, §7 |
| A trivial wrapper that hides nothing | Inline Function/Variable | catalog §3 |
| Unclear name | Rename | catalog §5 |
| Long parameter list / repeated arg groups | Introduce Parameter Object | catalog §6 |
| `switch`/`if` on a type code, repeated | Replace Conditional with Polymorphism | catalog §8 |
| A class that knows/does too much | Extract Class / Move Method | catalog §9 |
| Comments explaining *what* code does | Extract Function with an intention-revealing name | catalog §1 |

When unsure, default to **Extract Function** + **Rename** — together they resolve most readability smells with the lowest risk.

## Best Practices

- **Tiny steps, frequent tests.** A refactoring session is dozens of safe micro-commits, not one giant rewrite.
- **One refactoring per commit.** Keeps diffs reviewable and reverts surgical.
- **Separate refactoring commits from behavior changes.** Never mix. Reviewers should be able to trust a `refactor:` commit changes nothing observable.
- **Name things for intent**, not implementation (`isEligibleForDiscount`, not `checkFlag2`).
- **Prefer pure functions** when extracting — pass inputs in, return outputs, avoid reaching into shared state.
- **Let tests drive trust.** If you can't test it, characterize it first; if you can't characterize it, you can't safely refactor it.
- **Leave the campsite cleaner.** Opportunistic, bounded cleanup around code you're already touching beats a doomed "big refactor" project.

## Common Pitfalls

- **Refactoring without tests.** The #1 way to silently break behavior. Write characterization tests first.
- **Mixing in a bug fix or feature.** Now the diff can't be trusted as behavior-preserving. Split it out.
- **Big-bang rewrite.** High risk, hard to review, easy to abandon. Decompose into incremental steps.
- **Changing public API while "just refactoring".** Renaming/removing exported symbols is a breaking change, not a refactor. Use deprecation shims if needed.
- **Over-extraction.** Splitting into so many one-line functions that flow is lost. Extract for clarity, not dogma.
- **Premature abstraction.** Don't DRY up two things that merely *look* similar; wait for the third real duplication and confirm they change together.
- **Not running tests between steps.** When something breaks you won't know which step did it.

## Bundled resources

- `references/code-smells.md` — catalog of smells with detection signals and the refactoring each implies.
- `references/refactoring-catalog.md` — numbered, step-by-step mechanics for each core refactoring, with before/after examples.
- `references/characterization-tests.md` — how to pin legacy behavior before refactoring untested code.
- `scripts/refactor_check.sh` — verification helper: runs tests + lint/type-check and snapshots exported symbols to detect accidental API changes.
- `examples/extract-function-walkthrough.md` — a full worked example from smelly code to clean, step by step.
