# syntax=docker/dockerfile:1.7
# Node.js multi-stage build.
# - `deps` installs production deps with a cache mount and `npm ci` (lockfile-exact).
# - `build` compiles/transpiles (TypeScript, bundlers, etc.).
# - final stage is distroless nodejs (no shell, no package manager, non-root).
# Build: docker build -t mynode:1.0.0 .

############################
# Stage 1: production deps
############################
FROM node:22.11.0-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --no-audit --no-fund

############################
# Stage 2: build (needs dev deps)
############################
FROM node:22.11.0-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --no-audit --no-fund
COPY . .
RUN npm run build      # produces ./dist

############################
# Stage 3: runtime (distroless)
############################
FROM gcr.io/distroless/nodejs22-debian12:nonroot AS runtime
WORKDIR /app
ENV NODE_ENV=production

# Only the runtime artifacts: prod node_modules + built output + manifest.
COPY --from=deps  --chown=nonroot:nonroot /app/node_modules ./node_modules
COPY --from=build --chown=nonroot:nonroot /app/dist        ./dist
COPY --chown=nonroot:nonroot package.json ./

USER nonroot:nonroot
EXPOSE 3000

LABEL org.opencontainers.image.source="https://github.com/org/repo" \
      org.opencontainers.image.licenses="MIT"

# distroless nodejs image's entrypoint is already `node`, so CMD is just the script.
CMD ["dist/server.js"]
