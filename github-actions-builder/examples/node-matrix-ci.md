# Worked Example: Node.js Matrix CI with Caching and a Gated Deploy

## Input (request)

> Set up CI for a Node app: lint and test on PRs and merges to main, test on Node 18/20/22 across Ubuntu and macOS, cache npm, and deploy to production (AWS via OIDC) only when main is pushed.

## Output (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ${{ matrix.os }}
    timeout-minutes: 20
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [18, 20, 22]
        exclude:
          - os: macos-latest
            node: 18          # skip the slow/old combo on macOS
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
      - run: npm ci
      - run: npm test

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7

  deploy:
    needs: [build]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    environment: production        # required reviewers + scoped secrets
    permissions:
      contents: read
      id-token: write              # OIDC
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gh-deploy
          aws-region: us-east-1
      - run: aws s3 sync dist/ s3://my-app-bucket --delete
```

## Why it is built this way

- **`push` filtered to `main` + bare `pull_request`** prevents double runs on PR branches while still gating merges.
- **`fail-fast: false`** on the test matrix surfaces every failing Node version at once. `exclude` trims a wasteful combo.
- **`cache: 'npm'`** with `npm ci` gives reproducible, fast installs keyed on `package-lock.json` automatically.
- **Artifact handoff** keeps `build` and `deploy` separate; deploy never rebuilds.
- **`deploy` is gated** by ref + event, uses an `environment` for approval and scoped secrets, and authenticates via **OIDC** (`id-token: write`) instead of stored AWS keys.
- **Least-privilege `permissions`** at the top (`contents: read`), with `id-token: write` granted only on the deploy job.

Run `python3 scripts/validate_workflow.py .github/workflows/ci.yml` to confirm it is clean.
