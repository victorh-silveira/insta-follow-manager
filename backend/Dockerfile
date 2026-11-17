# syntax=docker/dockerfile:1.7

ARG PYTHON_IMAGE=python:3.13.9-slim-bookworm

# --- Stage 1: Dependency Builder ---
FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Stage 2: Minimal Non-Root Runtime ---
FROM ${PYTHON_IMAGE} AS runtime

ARG APP_UID=10001
ARG APP_GID=10001

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install tini for proper PID 1 signal forwarding & zombie reaping
RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged user and group without login shell
RUN groupadd --gid "${APP_GID}" appgroup \
    && useradd --uid "${APP_UID}" --gid "${APP_GID}" --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup src ./src

# Persistent directory for SQLite / session volume
RUN mkdir -p /app/data && chown -R appuser:appgroup /app/data

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"]

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
