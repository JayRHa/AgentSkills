# GitHub Actions Best Practices Reference

## Trigger (`on:`) Matrix

| Goal | Configuration |
|------|---------------|
| Validate PRs | `pull_request:` (optionally `types: [opened, synchronize, reopened]`) |
| Run on merge to main | `push:` `branches: [main]` |
| Avoid duplicate PR runs | Only filter `push` to default branch; let `pull_request` cover branches |
| Manual run | `workflow_dispatch:` (add `inputs:` for parameters) |
| Scheduled | `schedule: - cron: '0 6 * * 1'` (UTC; quote the cron) |
| Release on tag | `push:` `tags: ['v*.*.*']` |
| Called by another workflow | `workflow_call:` |
| Path-scoped | add `paths:` / `paths-ignore:` under the event |

Note: `pull_request` from forks runs with a read-only `GITHUB_TOKEN` and no secrets by default — this is intentional. Do NOT switch to `pull_request_target` to work around it unless you fully understand the risk; that runs in the context of the base repo with secrets and can execute attacker-controlled code if you checkout PR head.

## Permissions Cheat Sheet

Default to the most restrictive and widen per-job.

```yaml
permissions:
  contents: read        # checkout, read repo
```

Common additional scopes (grant only on the job that needs them):

| Scope | When |
|-------|------|
| `contents: write` | Create releases, push tags/commits, GitHub Pages source |
| `packages: write` | Publish to GitHub Packages / GHCR |
| `id-token: write` | OIDC federation to cloud providers |
| `pull-requests: write` | Comment on / label PRs |
| `issues: write` | Create or update issues |
| `pages: write` | Deploy to GitHub Pages |
| `checks: write` | Publish check runs / annotations |

## Action Pinning Policy

- Third-party actions: pin to a full 40-char commit SHA.
  ```yaml
  - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
  ```
- First-party `actions/*` and `github/*`: `@v4` style major tags are acceptable if org policy permits; SHA is still safest.
- Enable Dependabot to bump pinned actions:
  ```yaml
  # .github/dependabot.yml
  version: 2
  updates:
    - package-ecosystem: "github-actions"
      directory: "/"
      schedule: { interval: "weekly" }
  ```

## Concurrency Patterns

Cancel superseded runs on the same ref:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
For deploys, serialize without cancelling in-flight deploys:
```yaml
concurrency:
  group: production-deploy
  cancel-in-progress: false
```

## Job Structure

- One job per concern: `lint`, `test`, `build`, `deploy`.
- Express order with `needs:`; jobs without `needs` run in parallel.
- Gate environment-specific jobs:
  ```yaml
  deploy:
    needs: [test, build]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  ```
- Always set `timeout-minutes` (e.g. 10-30) to cap runaway jobs.

## Passing Data Between Jobs

- Build artifacts: `actions/upload-artifact` then `actions/download-artifact`.
- Small values: job `outputs:` via `$GITHUB_OUTPUT`.
  ```yaml
  - id: vers
    run: echo "version=$(cat VERSION)" >> "$GITHUB_OUTPUT"
  # consumer: ${{ needs.build.outputs.version }}
  ```

## Reusable Workflows vs Composite Actions

| | Reusable workflow | Composite action |
|--|------------------|------------------|
| File | `.github/workflows/x.yml` with `on: workflow_call` | `.github/actions/x/action.yml` |
| Granularity | Whole jobs | A sequence of steps |
| Inputs | `inputs:`, `secrets:` | `inputs:` (no native secrets block) |
| Called via | `uses: ./.github/workflows/x.yml` (job-level) | `uses: ./.github/actions/x` (step-level) |
| Cross-repo | Yes (`owner/repo/.github/workflows/x.yml@ref`) | Yes |

Secrets are NOT inherited automatically by reusable workflows — pass `secrets: inherit` or list them explicitly.

## Self-Documenting Checklist

- [ ] `permissions:` declared, least privilege
- [ ] `concurrency:` set
- [ ] every job has `timeout-minutes`
- [ ] `actions/checkout` present before build steps
- [ ] dependencies installed from lockfile (`npm ci`, etc.)
- [ ] cache key hashes the lockfile, with `restore-keys`
- [ ] third-party actions pinned to SHA
- [ ] no secrets echoed; deploys use `environment:`
- [ ] matrix tests use `fail-fast: false`
