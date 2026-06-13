# syntax=docker/dockerfile:1.7
# Minimal, secure, reproducible Go image.
# Final stage is `scratch`: just the static binary + CA certs + passwd entry.
# Build:  DOCKER_BUILDKIT=1 docker build -t myapp:1.0.0 .
# Result: typically a few MB, non-root, no shell, no package manager.

############################
# Stage 1: build
############################
FROM golang:1.23-bookworm AS builder

WORKDIR /src

# Dependency layer first so source edits don't bust the module cache.
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

# Now the source.
COPY . .

# Static, stripped, trimmed -> small + reproducible.
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux \
    go build -trimpath -ldflags="-s -w" -o /out/app ./cmd/server

# Create a minimal passwd entry for the non-root user used in `scratch`.
RUN echo 'app:x:10001:10001::/home/app:/sbin/nologin' > /out/passwd

############################
# Stage 2: runtime (scratch)
############################
FROM scratch

# TLS roots so the app can make HTTPS calls.
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /out/passwd /etc/passwd
COPY --from=builder --chown=10001:10001 /out/app /app

USER 10001:10001
WORKDIR /
EXPOSE 8080
ENV TZ=UTC

LABEL org.opencontainers.image.source="https://github.com/org/repo" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.description="Example Go service"

# Exec form so the binary is PID 1 and receives SIGTERM for graceful shutdown.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/app", "healthcheck"]
ENTRYPOINT ["/app"]
CMD ["serve"]
