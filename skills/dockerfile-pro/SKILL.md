---
name: dockerfile-pro
description: Authors small, secure, reproducible multi-stage Dockerfiles with build-cache optimization, pinned base images, non-root runtime users, and minimal attack surface. Use this skill when writing, reviewing, hardening, or shrinking a Dockerfile or container image — e.g. "write a Dockerfile", "containerize this app", "my image is too big", "make this container secure / non-root", "optimize Docker build cache", "multi-stage build", "reduce image layers", "fix Docker best practices", or "review my Dockerfile".
license: MIT
---

# dockerfile-pro

## Overview

Produce production-grade Dockerfiles that are **small** (minimal final image), **secure** (non-root, pinned, no secrets, minimal surface), and **reproducible** (deterministic builds with effective layer caching). Applies to any language runtime (Go, Rust, Node, Python, Java, .NET, etc.) and any registry.

Keywords: Dockerfile, container, multi-stage build, build cache, BuildKit, non-root user, distroless, alpine, slim, image size, layer caching, `.dockerignore`, HEALTHCHECK, OCI image, supply chain, reproducible build, hadolint, Trivy.

The three goals (small / secure / reproducible) often align, but when they conflict, prioritize **security > reproducibility > size**.

## Workflow

Follow these steps in order when authoring or reviewing a Dockerfile.

1. **Identify the app shape.** Compiled binary (Go/Rust/C++) → use a `FROM scratch` or `distroless` final stage. Interpreted/runtime (Node/Python/Java/.NET) → use the matching `-slim`/`distroless` runtime image. JVM/CLR may need a JRE-only final image.
2. **Always use multi-stage.** A `builder` stage installs toolchains and compiles/installs dependencies; the final stage copies only the runtime artifacts. Never ship compilers, package caches, or dev headers.
3. **Pin everything.** Pin the base image by tag **and** digest (`image:tag@sha256:...`). Pin OS and language package versions. This is what makes builds reproducible.
4. **Order layers from least- to most-frequently-changing.** Copy dependency manifests (`package.json`, `go.mod`, `requirements.txt`, `*.csproj`) and install deps *before* copying application source. Source changes then don't bust the dependency layer.
5. **Use BuildKit cache mounts** (`RUN --mount=type=cache,...`) for package-manager caches so repeated builds are fast without bloating the image.
6. **Drop to a non-root user** in the final stage with an explicit numeric UID/GID. Make the filesystem read-only-friendly.
7. **Minimize layers and surface.** Combine related `RUN` steps, clean package caches in the same layer, and copy with `--chown` instead of a separate `chown` layer.
8. **Add operational metadata.** `WORKDIR`, `EXPOSE`, `ENV`, OCI `LABEL`s, `HEALTHCHECK`, and an exec-form `ENTRYPOINT`/`CMD`.
9. **Add a `.dockerignore`.** Exclude `.git`, `node_modules`, build output, secrets, and CI files so the build context stays small and secrets never enter an image.
10. **Lint and scan.** Run `hadolint Dockerfile` and a vulnerability scan (e.g. `trivy image`). See `scripts/check_dockerfile.py` for a fast static audit you can run with zero dependencies.

## Decision frameworks

### Which final base image?

| App type | Recommended final base | Notes |
|---|---|---|
| Static Go / Rust binary | `gcr.io/distroless/static` or `scratch` | Add CA certs + `/etc/passwd` if using `scratch`. |
| Dynamically-linked binary | `gcr.io/distroless/base` or `*-slim` | Needs libc. |
| Node.js | `gcr.io/distroless/nodejs22-debian12` or `node:22-slim` | Distroless has no shell — great for prod, harder to debug. |
| Python | `python:3.12-slim` or `gcr.io/distroless/python3` | Prefer slim + venv copy. |
| Java | `eclipse-temurin:21-jre` or `gcr.io/distroless/java21` | JRE only, never the JDK, in the final stage. |
| .NET | `mcr.microsoft.com/dotnet/aspnet:8.0` (or `-chiseled`) | `chiseled` images are distroless-style and non-root by default. |
| Needs a shell/debug | `*-slim` or `*-alpine` | Alpine uses musl — watch for glibc-specific bugs. |

Rule of thumb: **distroless or scratch for compiled apps; `-slim` for interpreted apps.** Avoid full `:latest` / fat base images.

### Alpine vs slim?

- Alpine: smallest, but `musl` libc can break native deps (Python wheels, glibc binaries) and complicate DNS/locale handling.
- Debian `-slim`: slightly larger but maximally compatible. **Default to `-slim` unless you have measured a real size win and tested compatibility.**

## Best Practices

- **Pin base by digest:** `FROM node:22.11.0-slim@sha256:<digest>`. Tags are mutable; digests are not.
- **One concern per stage**, named with `AS builder`, `AS deps`, `AS runtime`.
- **Exec form only:** `CMD ["node","server.js"]` — never the shell form `CMD node server.js` (it breaks signal handling and PID 1 semantics).
- **Non-root with numeric UID:** `USER 10001:10001`. A numeric UID lets Kubernetes enforce `runAsNonRoot` even without `/etc/passwd`.
- **`COPY --chown=10001:10001`** to set ownership without an extra layer; never `chmod -R 777`.
- **Clean in the same layer:** `apt-get update && apt-get install -y --no-install-recommends X && rm -rf /var/lib/apt/lists/*`.
- **`--no-install-recommends`** (apt) / `--no-cache` (apk) / `--frozen-lockfile` (npm ci) for determinism.
- **Pass secrets via `RUN --mount=type=secret`,** never `ARG`/`ENV` (they persist in image history and `docker history` leaks them).
- **Add `HEALTHCHECK`** for long-running services so orchestrators can detect liveness.
- **Set `WORKDIR`** explicitly; never rely on `/`.
- **Use `tini` or `--init`** (or a runtime that reaps zombies) when your process spawns children.
- See `references/best-practices.md` for the full annotated checklist and rationale.

## Common Pitfalls

- ❌ Running as root in the final image (the default). Always add `USER`.
- ❌ `ADD` for local files — use `COPY`. Reserve `ADD` for remote URLs/tar auto-extraction (and prefer not to).
- ❌ Secrets in `ARG`/`ENV` or copied `.env` files — they leak via `docker history` and image layers.
- ❌ `apt-get upgrade` / unpinned `latest` — destroys reproducibility.
- ❌ Separate `RUN chmod`/`chown` after `COPY` — doubles the data on disk across layers. Use `COPY --chown`.
- ❌ Copying the whole context first (`COPY . .`) before installing deps — busts the cache on every source edit.
- ❌ Shell-form `CMD`/`ENTRYPOINT` — your process won't receive `SIGTERM`, so graceful shutdown breaks.
- ❌ No `.dockerignore` — bloats context, slows builds, risks leaking `.git`/credentials.
- ❌ Shipping the build toolchain in the final image — keep it in the builder stage only.

## Supporting files

- `references/best-practices.md` — exhaustive, annotated best-practice checklist with rationale, BuildKit cache-mount and secret-mount recipes, and a security/supply-chain section.
- `examples/go-multistage.Dockerfile` — minimal scratch-based Go image (non-root, pinned, static).
- `examples/node-multistage.Dockerfile` — Node.js multi-stage with `npm ci`, cache mounts, distroless final.
- `examples/python-multistage.Dockerfile` — Python slim with venv copy and non-root user.
- `templates/Dockerfile.template` — language-agnostic fill-in-the-blanks multi-stage template.
- `templates/dockerignore.template` — sensible default `.dockerignore`.
- `scripts/check_dockerfile.py` — zero-dependency static auditor that flags root users, unpinned bases, secrets in ARG, shell-form CMD, missing `.dockerignore`, and more.

Use the examples/templates as the starting skeleton, then apply the workflow and run `scripts/check_dockerfile.py` plus `hadolint` before finishing.
