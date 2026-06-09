# Dockerfile Best Practices — Annotated Reference

Load this when you need the *why* behind a rule, the exact BuildKit syntax, or the full security checklist.

## 1. Multi-stage builds

The single highest-impact technique. Build artifacts in one stage; copy only what runs into a tiny final stage.

```dockerfile
# syntax=docker/dockerfile:1.7
FROM golang:1.23-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /app ./cmd/server

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

- Name stages with `AS <name>` and reference them with `--from=<name>`.
- `--trimpath` and `-ldflags="-s -w"` strip paths and debug symbols → smaller, more reproducible binaries.
- You can target an intermediate stage for debugging: `docker build --target builder .`.

## 2. Pinning for reproducibility

| What | How | Why |
|---|---|---|
| Base image | `FROM img:1.2.3@sha256:...` | Tags are mutable; digests are immutable. |
| `# syntax` | `# syntax=docker/dockerfile:1.7` | Pins the frontend so BuildKit features are stable. |
| OS packages | `apt-get install -y pkg=1.2.3-1` | Avoids surprise upgrades. |
| Language deps | lockfiles: `package-lock.json`, `go.sum`, `poetry.lock` | Deterministic dependency tree. |
| Install flags | `npm ci`, `pip install --require-hashes`, `--frozen-lockfile` | Fail if the lockfile drifts. |

Get a digest: `docker pull node:22-slim && docker inspect --format='{{index .RepoDigests 0}}' node:22-slim`.

Never use `:latest` in production Dockerfiles. Never run `apt-get upgrade`/`apk upgrade` — rebuild on a newer pinned base instead.

## 3. Layer ordering & caching

Docker caches each instruction by its inputs. A layer rebuilds only when it or an earlier layer changes. Order from least- to most-volatile:

```dockerfile
COPY package.json package-lock.json ./   # changes rarely
RUN npm ci                               # cached unless manifests change
COPY . .                                 # changes constantly
RUN npm run build                        # only this re-runs on source edits
```

### BuildKit cache mounts

Keep package-manager caches *out* of the image while reusing them across builds:

```dockerfile
# npm
RUN --mount=type=cache,target=/root/.npm npm ci
# pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
# apt (disable the auto-clean so the cache survives)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends ca-certificates
# go
RUN --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build go build ./...
# cargo
RUN --mount=type=cache,target=/usr/local/cargo/registry --mount=type=cache,target=/app/target cargo build --release
```

Cache mounts require BuildKit (default in modern Docker; otherwise `DOCKER_BUILDKIT=1`).

## 4. Minimizing image size

- Use distroless/scratch/slim final bases (see SKILL.md table).
- Combine `RUN` steps and clean caches **in the same layer**:
  ```dockerfile
  RUN apt-get update \
      && apt-get install -y --no-install-recommends curl ca-certificates \
      && rm -rf /var/lib/apt/lists/*
  ```
- `--no-install-recommends` (apt) and `--no-cache` (apk) skip optional bloat.
- Copy only what you need; rely on `.dockerignore` to keep the context lean.
- Strip binaries (`-ldflags="-s -w"` for Go, `strip` for C/Rust, `RUSTFLAGS` / `cargo build --release`).
- For Python, build a virtualenv in the builder and `COPY --from=builder /opt/venv /opt/venv`.
- Inspect what's taking space: `docker history --no-trunc <image>` and `dive <image>`.

## 5. Security hardening

### Run as non-root

```dockerfile
# Debian/Ubuntu-based
RUN groupadd --system --gid 10001 app \
    && useradd  --system --uid 10001 --gid app --home /home/app --shell /usr/sbin/nologin app
USER 10001:10001
```

- Prefer a **numeric** UID/GID so Kubernetes `runAsNonRoot` can verify it without `/etc/passwd`.
- distroless `:nonroot` variants already define UID 65532.
- For `FROM scratch`, bake a passwd entry in the builder:
  ```dockerfile
  RUN echo 'app:x:10001:10001::/home/app:/sbin/nologin' > /etc/passwd_min
  COPY --from=builder /etc/passwd_min /etc/passwd
  ```

### Read-only friendly

Design the image to run with `--read-only`; write only to mounted `tmpfs`/volumes. Use `COPY --chown` so files are owned correctly and you never need a writable root FS.

### Secrets — never in the image

```dockerfile
# Build-time secret, never persisted in any layer:
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
# build with:  docker build --secret id=npmrc,src=$HOME/.npmrc .
```

- ❌ `ARG TOKEN` / `ENV TOKEN` — visible in `docker history` and image config.
- ❌ `COPY .env .` — copies credentials into a layer forever.
- ✅ `RUN --mount=type=secret,...` or SSH agent forwarding `--mount=type=ssh`.

### Supply chain

- Pin base images by digest (immutability + auditability).
- Scan: `trivy image <image>` / `grype <image>` in CI; fail on HIGH/CRITICAL.
- Sign & attest: `cosign sign` + SBOM (`docker buildx build --sbom=true --provenance=true`).
- Drop Linux capabilities at runtime (`--cap-drop=ALL`) and add only what's needed.
- Set `SOURCE_DATE_EPOCH` and `--output type=image,rewrite-timestamp=true` for bit-reproducible builds.

## 6. Operational metadata

```dockerfile
WORKDIR /app
EXPOSE 8080
ENV NODE_ENV=production
LABEL org.opencontainers.image.source="https://github.com/org/repo" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.description="My service"
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["/app", "healthcheck"]
ENTRYPOINT ["/app"]
CMD ["serve"]
```

- Use **exec form** (`["..."]`) for `ENTRYPOINT`/`CMD`/`HEALTHCHECK` so PID 1 receives signals.
- Prefer a built-in healthcheck subcommand over installing `curl` just to probe.
- `ENTRYPOINT` = the binary; `CMD` = default args (overridable).

## 7. PID 1 / signal handling

If your process spawns children or you see hung shutdowns, add an init:

```dockerfile
# Option A: tiny init binary
ADD --chmod=755 https://github.com/krallin/tini/releases/download/v0.19.0/tini-static-amd64 /tini
ENTRYPOINT ["/tini", "--", "/app"]
# Option B (at runtime): docker run --init ...
```

## 8. Linting & validation

- `hadolint Dockerfile` — catches DL3xxx best-practice violations.
- `docker buildx build --check .` — BuildKit build-time linter.
- `scripts/check_dockerfile.py Dockerfile` — this skill's dependency-free auditor.
- `trivy config Dockerfile` — misconfiguration scan.

## Quick reference: instruction do/don't

| Do | Don't |
|---|---|
| `COPY` local files | `ADD` local files |
| `CMD ["a","b"]` (exec) | `CMD a b` (shell) |
| `USER 10001` | run as root |
| `img:1.2@sha256:...` | `img:latest` |
| `--mount=type=secret` | `ARG SECRET` |
| `COPY --chown=u:g` | `RUN chown -R` |
| `rm -rf /var/lib/apt/lists/*` same layer | clean in a later layer |
