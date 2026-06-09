---
name: github-actions-builder
description: Builds reliable, fast, and secure GitHub Actions CI/CD workflows with dependency caching, build matrices, scoped secrets, concurrency control, and reusable/composite workflows. Use this skill when the user asks to "create a GitHub Actions workflow", "set up CI", "add CI/CD", "fix a flaky/slow GitHub Actions pipeline", "add a build matrix", "cache dependencies in CI", "write a reusable workflow", "configure deployment with environments and secrets", or mentions files under .github/workflows.
license: MIT
---

# GitHub Actions Builder

## Overview

Author production-grade GitHub Actions workflows that are fast, deterministic, and secure by default.

Keywords: github actions, workflow, ci, cd, ci/cd, .github/workflows, jobs, steps, runs-on, matrix, build matrix, strategy, fail-fast, cache, actions/cache, setup-node, setup-python, setup-go, secrets, GITHUB_TOKEN, permissions, OIDC, environments, reusable workflow, workflow_call, composite action, concurrency, artifacts, upload-artifact, deploy, release, pinning SHA, dependabot.

This skill covers the full lifecycle: choosing triggers, structuring jobs, caching dependencies correctly, fanning out across a matrix, passing secrets safely, gating deployments with environments, and factoring shared logic into reusable or composite workflows. Always prefer the patterns and pinning rules in `references/best-practices.md` and validate output structure with `scripts/validate_workflow.py`.

## Workflow

1. **Clarify intent.** Identify: project language/runtime, the events that should trigger CI (push, pull_request, tag, schedule, manual), and whether deployment is in scope. If the user only says "add CI", default to lint + test on `push` to the default branch and on `pull_request`.

2. **Pick triggers (`on:`).** Use `pull_request` for validation and `push` (filtered to the default branch) to avoid double-runs on PR branches. Add `workflow_dispatch` for manual runs and `tags` filters for release pipelines. See the trigger matrix in `references/best-practices.md`.

3. **Set top-level defaults.** Always add `permissions:` (least privilege, default `contents: read`) and `concurrency:` to cancel superseded runs. Pin a sensible `timeout-minutes` on every job.

4. **Structure jobs.** Split lint, test, and build/deploy into separate jobs so failures are isolated and parallel. Use `needs:` to express ordering. Gate deploy jobs on `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`.

5. **Add a matrix when relevant.** Fan out across runtime versions and OSes with `strategy.matrix`. Set `fail-fast: false` for test matrices so one failure does not cancel the rest. Use `include`/`exclude` for targeted combinations. See `examples/node-matrix-ci.md`.

6. **Cache dependencies correctly.** Prefer the built-in cache of `setup-*` actions (`cache: 'npm'|'pip'|'gradle'`). When you need finer control, use `actions/cache` with a lockfile-hashed `key` and `restore-keys` fallback. Cache rules and key recipes live in `references/caching-guide.md`.

7. **Handle secrets and auth safely.** Reference secrets only via `${{ secrets.NAME }}`, never echo them, scope them with `environment:`, and prefer OIDC over long-lived cloud credentials. Follow `references/secrets-and-security.md`.

8. **Factor shared logic.** If two or more workflows repeat steps, extract a reusable workflow (`on: workflow_call`) or a composite action. Templates are in `templates/reusable-workflow.yml` and `templates/composite-action.yml`.

9. **Validate.** Run `python3 scripts/validate_workflow.py <file>` to catch missing `permissions`, unpinned third-party actions, plaintext secrets, missing `concurrency`, and absent `timeout-minutes` before committing.

## Decision Framework

| Need | Use |
|------|-----|
| Run checks on every PR | `on: pull_request` + separate lint/test jobs |
| Avoid duplicate runs on PR branch | `push` filtered to `branches: [main]` only |
| Test across versions/OS | `strategy.matrix` + `fail-fast: false` |
| Share steps across repos | Reusable workflow (`workflow_call`) |
| Share steps within one repo | Composite action under `.github/actions/` |
| Gate prod deploy | `environment:` with required reviewers |
| Talk to AWS/GCP/Azure | OIDC + `permissions: id-token: write` |
| Pass build output between jobs | `actions/upload-artifact` + `download-artifact` |
| Cancel stale runs | `concurrency:` with `cancel-in-progress: true` |

## Worked Example (minimal Node CI)

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

For richer scenarios see `examples/node-matrix-ci.md` (multi-version + OS matrix with caching) and the templates directory.

## Best Practices

- **Pin third-party actions to a full commit SHA** (e.g. `actions/checkout@<sha>`), not a moving tag. Official `actions/*` may use `@v4` if the org policy allows; everything else gets a SHA. Add a comment with the version for readability.
- **Least-privilege permissions.** Declare `permissions:` at the top, default to `contents: read`, and grant write scopes only on the specific job that needs them.
- **Always set `concurrency` and `timeout-minutes`.** Prevents pile-ups of stale runs and hung jobs burning minutes.
- **Use `npm ci` / `pip install -r ... --require-hashes` / lockfile installs**, never unpinned `npm install`, for reproducible builds.
- **`fail-fast: false` for test matrices**, `true` (default) for build/release matrices where one failure invalidates the set.
- **Cache by lockfile hash** and include `restore-keys` so a near-miss still warms the cache.
- **Group related steps into reusable workflows** once duplicated; keep individual workflow files focused on one purpose.
- **Use `environment:` for deploys** to get protection rules, required reviewers, and scoped secrets.
- **Prefer OIDC** (`id-token: write`) over storing cloud access keys as secrets.

## Common Pitfalls

- **Double runs:** triggering on both `push` and `pull_request` without filtering `push` to the default branch runs CI twice on PRs. Filter `push` branches.
- **Unbounded permissions:** the default `GITHUB_TOKEN` may be broad; not declaring `permissions:` is a supply-chain risk. Always set it.
- **Broken cache keys:** using a constant key never invalidates; hashing the wrong file (e.g. `package.json` instead of `package-lock.json`) misses changes. Hash the lockfile.
- **Leaking secrets:** `run: echo ${{ secrets.X }}` or passing secrets into untrusted PR contexts (`pull_request_target`) exposes them. Never echo; avoid `pull_request_target` with checkout of PR code.
- **Floating tags on third-party actions:** `@v1` or `@master` can be hijacked. Pin to SHA.
- **`fail-fast` cancelling a debug matrix:** leaving it `true` hides which versions actually fail. Set `false` for tests.
- **Missing `actions/checkout`:** many workflows fail because the repo was never checked out before build steps.
- **Secrets unavailable in reusable workflows:** caller must pass them via `secrets:` (or `secrets: inherit`); they are not auto-forwarded.

Validate every workflow you produce with `scripts/validate_workflow.py` and consult the references before finalizing.
