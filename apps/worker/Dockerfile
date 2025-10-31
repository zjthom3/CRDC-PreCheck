# syntax=docker/dockerfile:1.4

FROM python:3.11-slim AS base

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY apps/worker/worker ./apps/worker/worker
COPY apps/worker/pyproject.toml apps/worker/README.md ./apps/worker/
COPY packages/shared ./packages/shared
COPY packages/rules ./packages/rules

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ./packages/shared \
    && pip install --no-cache-dir -e ./packages/rules \
    && pip install --no-cache-dir -e ./apps/worker

ENV PYTHONPATH=/workspace

CMD ["celery", "-A", "apps.worker.worker.app", "worker", "--loglevel=info"]
