# Worked Example: Reviewing & Fixing a Bad Dockerfile

This shows the skill's workflow applied to a real, flawed Dockerfile.

## Input (the "before")

```dockerfile
FROM node:latest
WORKDIR /app
COPY . .
RUN npm install
ENV API_TOKEN=sk-live-abcdef123456
ADD config.json /app/config.json
EXPOSE 3000
CMD npm start
```

## Audit

Running `python3 scripts/check_dockerfile.py Dockerfile` reports:

```
Dockerfile: 4 error(s), 4 warning(s)
  [ERROR] DFP003 (L1): Base 'node:latest' uses 'latest'/no tag -> non-reproducible.
  [ERROR] DFP010 (L1): No USER set in the final stage: container runs as root.
  [ERROR] DFP020 (L5): Possible secret in ARG/ENV (persists in image history)...
  [ERROR] DFP031 (L8): CMD uses shell form; use exec form ["..."] so PID 1 receives signals.
  [WARN]  DFP001 (L1): Single-stage build: consider multi-stage...
  [WARN]  DFP002 (L1): Base 'node:latest' is not pinned by @sha256 digest...
  [WARN]  DFP030 (L6): Use COPY for local files; reserve ADD for remote URLs/tar.
  [WARN]  DFP060: No .dockerignore next to the Dockerfile...
```

## Diagnosis (mapped to the workflow)

| Issue | Rule violated | Fix |
|---|---|---|
| `node:latest` | Step 3 (pin) | Pin `node:22.11.0-slim@sha256:...` |
| `COPY . .` before install | Step 4 (layer order) | Copy `package*.json` first, then `npm ci` |
| `npm install` | reproducibility | Use `npm ci` (lockfile-exact) |
| `ENV API_TOKEN=...` | Step 6 / secrets | Remove; inject at runtime or `--mount=type=secret` |
| `ADD config.json` | instruction misuse | Use `COPY` |
| runs as root | Step 6 (non-root) | Distroless `:nonroot` or `USER 10001` |
| shell-form `CMD` | best practice | Exec form `["node","dist/server.js"]` |
| no `.dockerignore` | Step 9 | Add one from the template |
| single stage | Step 2 | Split build vs runtime |

## Output (the "after")

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:22.11.0-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev --no-audit --no-fund

FROM node:22.11.0-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs22-debian12:nonroot AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps  --chown=nonroot:nonroot /app/node_modules ./node_modules
COPY --from=build --chown=nonroot:nonroot /app/dist        ./dist
COPY --chown=nonroot:nonroot package.json config.json ./
USER nonroot:nonroot
EXPOSE 3000
CMD ["dist/server.js"]
```

The secret is gone (inject `API_TOKEN` at `docker run -e` / orchestrator secret),
the build is reproducible, the final image is distroless + non-root, and the
cache layers mean source edits no longer reinstall dependencies.

Finish by running `hadolint Dockerfile` and `trivy image <tag>` in CI.
