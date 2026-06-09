# Secrets, Auth, and Security Reference

## Referencing Secrets

```yaml
env:
  API_TOKEN: ${{ secrets.API_TOKEN }}
steps:
  - run: ./deploy.sh   # reads API_TOKEN from env
```

Rules:
- Reference only via `${{ secrets.NAME }}`. They are masked in logs automatically, but never `echo` or `cat` them deliberately.
- Prefer passing secrets as `env:` to a step over interpolating into a `run:` string (avoids shell-injection and accidental logging).
- Secrets are NOT passed to workflows triggered by `pull_request` from forks (by design). Do not work around this with `pull_request_target` + checkout of PR head.

## Secret Scopes

| Scope | Where defined | Use |
|-------|---------------|-----|
| Repository | repo settings | default per-repo secrets |
| Environment | repo > Environments | scoped to a deploy target, with protection rules |
| Organization | org settings | shared across repos, with repo allow-lists |

Use **environment secrets** for deploy credentials so they are only available to jobs that declare that environment, and can be gated by required reviewers.

```yaml
deploy:
  runs-on: ubuntu-latest
  environment: production      # required reviewers, env-scoped secrets
  steps:
    - run: ./deploy.sh
      env:
        TOKEN: ${{ secrets.PROD_DEPLOY_TOKEN }}
```

## OIDC — Prefer Over Stored Cloud Keys

Federate short-lived credentials instead of storing long-lived cloud access keys.

```yaml
permissions:
  id-token: write     # REQUIRED for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gh-deploy
          aws-region: us-east-1
      - run: aws s3 sync ./dist s3://my-bucket
```

Equivalents: `google-github-actions/auth` (GCP Workload Identity Federation), `azure/login` (Azure federated credentials). Configure the trust policy to restrict by repo, ref, and environment (the `sub` claim) so only intended workflows can assume the role.

## GITHUB_TOKEN Hardening

- Set `permissions:` explicitly; never rely on defaults.
- Grant write scopes only on the specific job that needs them.
- The token's permissions cannot exceed what you grant, and it cannot trigger new workflow runs by default (prevents recursion).

## Supply-Chain Hardening

- Pin third-party actions to a full commit SHA; enable Dependabot for `github-actions`.
- Review the source of any action before adding it; prefer verified creators.
- Avoid `curl | bash` of remote scripts in CI; vendor or checksum them.
- For untrusted PRs, run only read-only validation; require manual approval for first-time contributors (repo setting).
- Use `step-security/harden-runner` (pinned) for egress monitoring on sensitive pipelines.

## Anti-Patterns

- `run: echo "${{ secrets.TOKEN }}"` — logs/leaks the secret.
- `pull_request_target` + `actions/checkout` with `ref: ${{ github.event.pull_request.head.sha }}` — runs untrusted code with secrets.
- Storing AWS/GCP/Azure long-lived keys as secrets when OIDC is available.
- Granting `contents: write` or `packages: write` at the top level for all jobs.
- Interpolating untrusted input (`github.event.issue.title`, PR body) directly into `run:` — shell injection. Pass via `env:` and quote.
