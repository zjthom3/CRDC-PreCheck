# syntax=docker/dockerfile:1.4

FROM python:3.11-slim AS base

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/app ./apps/api/app
COPY apps/api/pyproject.toml apps/api/README.md ./apps/api/
COPY packages/shared ./packages/shared
COPY packages/rules ./packages/rules

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ./packages/shared \
    && pip install --no-cache-dir -e ./packages/rules \
    && pip install --no-cache-dir -e ./apps/api

ENV PYTHONPATH=/workspace

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
