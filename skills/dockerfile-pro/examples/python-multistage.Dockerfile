# syntax=docker/dockerfile:1.7
# Python multi-stage build using a copied virtualenv.
# Slim base (glibc) avoids musl wheel-compatibility issues that plague Alpine.
# Build: docker build -t mypy:1.0.0 .

############################
# Stage 1: build the venv
############################
FROM python:3.12-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=0 \
    PYTHONDONTWRITEBYTECODE=1

# Build tools only live in this stage; cleaned via the cache mount + no-recommends.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends build-essential

# Isolated venv we can copy wholesale into the runtime image.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

############################
# Stage 2: runtime
############################
FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Non-root user with a fixed numeric UID/GID.
RUN groupadd --system --gid 10001 app \
    && useradd  --system --uid 10001 --gid app --home /home/app --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=builder --chown=10001:10001 /opt/venv /opt/venv
COPY --chown=10001:10001 . .

USER 10001:10001
EXPOSE 8000

LABEL org.opencontainers.image.source="https://github.com/org/repo" \
      org.opencontainers.image.licenses="MIT"

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz').status==200 else 1)"]

# Exec form; gunicorn is PID 1 and reaps workers + handles SIGTERM.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
