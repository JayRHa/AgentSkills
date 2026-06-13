# Dependency Caching Guide

Fast, correct caching is the single biggest CI speedup. The golden rule: **key the cache on the lockfile hash so it invalidates exactly when dependencies change, and provide `restore-keys` so a near-miss still warms the cache.**

## Tier 1 — Use the built-in cache of `setup-*` actions

Simplest and recommended for most projects. These handle key construction and path discovery for you.

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'          # also: 'yarn', 'pnpm'
    cache-dependency-path: package-lock.json
```

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'          # also: 'pipenv', 'poetry'
```

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: '1.22'
    cache: true           # on by default; keyed on go.sum
```

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: '21'
    cache: 'gradle'       # also: 'maven', 'sbt'
```

## Tier 2 — Manual `actions/cache`

Use when you need to cache build outputs, tool installs, or paths the setup actions do not cover.

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .venv
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

Key anatomy:
- Prefix with `runner.os` (and runtime version if relevant) so caches do not collide across platforms.
- `hashFiles(...)` over the **lockfile**, not the manifest. Use `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `requirements.txt`/`poetry.lock`, `go.sum`, `Gemfile.lock`, `Cargo.lock`.
- `restore-keys` are tried as prefixes on a miss — order most-specific first.

## Common Cache Recipes

| Ecosystem | path | key hashes |
|-----------|------|-----------|
| npm | `~/.npm` | `package-lock.json` |
| yarn | `~/.cache/yarn` | `yarn.lock` |
| pnpm | `~/.local/share/pnpm/store` | `pnpm-lock.yaml` |
| pip | `~/.cache/pip` | `requirements*.txt` |
| poetry | `~/.cache/pypoetry` | `poetry.lock` |
| Go modules | `~/go/pkg/mod` | `go.sum` |
| Gradle | `~/.gradle/caches` | `**/*.gradle*`, `gradle-wrapper.properties` |
| Maven | `~/.m2/repository` | `**/pom.xml` |
| Cargo | `~/.cargo/registry`, `target` | `Cargo.lock` |
| Docker layers | use `docker/build-push-action` with `cache-from`/`cache-to: type=gha` |

## Docker Layer Caching

```yaml
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v6
  with:
    context: .
    push: false
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Pitfalls

- **Constant key** (`key: my-cache`) never invalidates and serves stale deps forever. Always hash the lockfile.
- **Hashing the manifest** (`package.json`) instead of the lockfile misses transitive dependency changes.
- **No `restore-keys`** means every lockfile change is a full cold cache. Add a prefix fallback.
- **Caching `node_modules` directly** is fragile across OS/arch; prefer caching the package manager's download cache and running `npm ci`.
- **Cache size limits:** repos have a total cache budget (~10 GB); least-recently-used entries are evicted. Keep keys tight.
- **Branch scoping:** caches created on a branch are readable by child branches and the default branch, but not arbitrary sibling branches. Warm shared caches on `main`.
