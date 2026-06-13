---
name: code-reviewer
description: Reviews a code diff or pull request for correctness bugs, security vulnerabilities, and quality/maintainability problems, producing severity-ranked findings with file/line references and concrete fix suggestions. Use this skill when the user asks to "review this PR", "review my diff", "code review", "look over these changes", "check this code before merge", "find bugs in this change", or pastes a diff/patch and wants feedback. Applies to git diffs, GitHub/GitLab PRs, staged changes, or a set of changed files in any language.
license: MIT
---

# Code Reviewer

## Overview

This skill performs a thorough, structured code review of a change set (a diff, a pull request, staged changes, or a list of modified files). It surfaces **correctness bugs**, **security vulnerabilities**, and **quality/maintainability** issues, ranks every finding by severity, and gives an actionable fix for each one.

Keywords: code review, PR review, diff review, bug hunting, security review, pull request, merge readiness, static review, defect detection.

The review is **diff-scoped by default**: focus on what changed and what the change touches. Do not rewrite the whole codebase. The deliverable is a review report, not a refactor.

## When To Use

- User says "review this PR / diff / branch / changes".
- User pastes a patch, unified diff, or set of files and asks for feedback.
- Before a merge, when the user wants a gate check.
- After implementing a feature, to self-review prior to opening a PR.

## Workflow

Follow these steps in order.

### 1. Gather the change set
Determine exactly what to review. Prefer the narrowest accurate scope.

- GitHub PR: `gh pr diff <number>` (or `gh pr view <number> --json files,title,body`).
- Local branch vs base: `git diff <base>...HEAD` (three-dot = changes on the branch since it forked).
- Staged: `git diff --staged`. Unstaged: `git diff`.
- A given commit: `git show <sha>`.
- If only file paths are given, read those files and, where needed, the symbols they call.

Capture: changed files, hunks, the PR title/description (intent), and the target branch.

### 2. Understand intent before judging
Read the PR description / commit messages to learn what the change is *supposed* to do. A bug is a divergence between intent and behavior — you cannot find bugs without knowing intent. If intent is unclear, note it as a finding ("unclear intent / missing description") and review against the most reasonable interpretation.

### 3. Build minimal context
For each changed function, pull in just enough surrounding code to judge correctness:
- The function signature and its callers (does the change break callers?).
- Types/interfaces touched.
- Tests covering the changed code.
- Config/migration files referenced by the diff.

Do not read the entire repo. Use `grep`/search to find callers and definitions on demand.

### 4. Pass over the diff with three lenses
Review each hunk through three lenses, in this priority order. Use `references/review-checklist.md` as the master checklist and `references/security-checklist.md` for the security lens.

1. **Correctness** — does it do the right thing for all inputs? (off-by-one, null/None, error handling, concurrency, edge cases, regressions, broken contracts).
2. **Security** — can it be abused? (injection, authz/authn, secrets, unsafe deserialization, SSRF, path traversal, crypto misuse).
3. **Quality / maintainability** — is it readable, tested, consistent, and not needlessly complex? (naming, duplication, dead code, missing tests, magic numbers, leaky abstractions).

### 5. Rank every finding by severity
Assign exactly one severity per finding using the rubric in "Severity Rubric" below. Sort the final report Critical → High → Medium → Low → Nit.

### 6. Write the report
Use `templates/review-report.md`. Each finding must include: severity, category, `file:line`, a one-line summary, why it matters, and a concrete suggested fix (ideally a diff snippet). End with a verdict: **Approve**, **Approve with nits**, **Request changes**, or **Block**.

### 7. Optional: post or self-check
- To estimate effort and sanity-check coverage, run `scripts/diff_stats.py` against the diff.
- If asked, post inline comments via `gh pr review` / `gh pr comment`.

## Severity Rubric

| Severity | Meaning | Examples |
|----------|---------|----------|
| **Critical** | Will cause data loss, security breach, or outage in production. Must fix before merge. | SQL injection, auth bypass, hardcoded secret, unhandled exception on the happy path, data-corrupting migration. |
| **High** | Correctness bug or vuln that triggers under realistic conditions. Fix before merge. | Off-by-one on a boundary, null deref on common input, race on shared state, missing input validation, broken error handling. |
| **Medium** | Bug under uncommon conditions, or a real maintainability problem. Fix soon. | Edge case only on empty input, N+1 query, missing test for new branch, leaky resource on error path. |
| **Low** | Minor issue, low blast radius. Nice to fix. | Inconsistent naming, redundant code, slightly unclear logic, missing doc. |
| **Nit** | Style/preference, non-blocking. | Formatting, wording, import order. |

When unsure between two levels, pick the higher one and say why. Do not inflate nits to high; that erodes trust in the review.

## Decision Heuristics

- **Only flag what you can justify.** Every finding needs a concrete failure scenario or rule. No vague "this could be better."
- **Scope discipline.** Pre-existing issues outside the diff are out of scope unless the diff makes them materially worse — if so, flag as Low/Medium with "pre-existing, surfaced by this change."
- **Prefer the smallest fix.** Suggest the minimal change that resolves the issue, not a rewrite.
- **Tests are part of correctness.** New logic without a test covering its main branch is at least Medium.
- **Read the error paths.** Most real bugs hide in `catch`/`except`, retries, cleanup, and early returns — not the happy path.
- **Assume hostile input** for anything crossing a trust boundary (HTTP params, files, env, deserialization, DB rows from other tenants).
- **Confidence labeling.** If you are not certain, prefix with "Possible:" and state what would confirm it. Never fabricate line numbers.

## Output Format

Produce the report from `templates/review-report.md`. Keep findings dense:

```
[High] Correctness — src/auth/session.py:42
Session token compared with `==`, enabling a timing attack and (on None) a TypeError.
Fix: use `hmac.compare_digest(a, b)` and guard for None before comparing.
```

Group by severity, highest first. Give a Summary line with counts (e.g., "1 Critical, 2 High, 3 Medium") and a final Verdict.

## Best Practices

- Lead with the verdict and the count summary so the reader knows the stakes immediately.
- Cite exact `file:line` from the diff for every finding.
- Give a fix, not just a complaint — a diff snippet beats prose.
- Separate blocking issues (Critical/High) from polish (Low/Nit) visually.
- Acknowledge what is good briefly; reviews that are 100% negative get ignored.
- Be specific and kind. Critique the code, not the author.

## Common Pitfalls

- **Reviewing the whole file instead of the diff** — wastes effort and produces out-of-scope noise.
- **Nit-flooding** — burying one Critical under 30 style nits. Keep nits at the bottom and brief.
- **Vague findings** — "consider refactoring" with no rule or scenario.
- **Missing the security lens** on data that crosses trust boundaries.
- **Hallucinated line numbers / APIs** — always anchor to the actual diff; mark uncertainty as "Possible:".
- **Ignoring tests** — a feature change with no test is an incomplete change.
- **Approving on style alone** while a logic bug sits unreviewed in the error path.

## Bundled Files

- `references/review-checklist.md` — full multi-language correctness & quality checklist (the master pass).
- `references/security-checklist.md` — OWASP-aligned security review checklist with concrete patterns.
- `templates/review-report.md` — the output template for the review.
- `examples/sample-review.md` — a worked example: input diff → produced review.
- `scripts/diff_stats.py` — stdlib script that summarizes a unified diff (files, churn, risk hints) to size the review.
