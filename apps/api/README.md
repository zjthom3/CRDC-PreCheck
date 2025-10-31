# CRDC PreCheck API

FastAPI application exposing tenant-scoped endpoints for CRDC data ingestion, validation, and reporting.

## Local Development

```bash
pnpm install --dir ../web          # install front-end deps once
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Environment variables are loaded from `.env` (see `.env.template` at the repo root). Database connectivity defaults to the Postgres service defined in `infra/docker/compose.yml`.
