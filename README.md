# CRDC PreCheck Monorepo

Sprint 0 delivers the core scaffolding for the CRDC PreCheck platform. The repo now provides a single workspace for backend, worker, and web applications with shared packages, infrastructure-as-code, and developer tooling.

## Repository Layout

```
apps/             # Application surfaces (API, worker, web)
packages/         # Reusable domain packages (rules DSL, shared models)
infra/            # Docker Compose, database migrations, observability
tests/            # Cross-cutting integration and system tests
.devcontainer/    # VS Code devcontainer configuration
.github/workflows # CI/CD definitions
```

## Quick Start

Prerequisites: Docker, Docker Compose v2, Make, Node 20.x, Python 3.11, and pnpm.

```bash
make dev         # launch local stack (API, worker, web, Postgres, Redis, MinIO, Grafana)
make migrate     # run Alembic migrations (API service image)
make seed        # load synthetic demo data
make test        # run backend + frontend tests
make lint        # run linting for Python and web workspaces
```

The compose stack exposes standard ports:

- API: http://localhost:8000
- Web: http://localhost:3000
- Postgres: localhost:5432 (credentials in `.env.template`)
- Redis: localhost:6379
- MinIO: http://localhost:9000 (console on :9001)
- Grafana: http://localhost:3100

The demo admin token is `demo-admin-token`. Frontend requests rely on the `NEXT_PUBLIC_API_TOKEN` env var (already set in `.env.template`).

## Developer Tooling

- **VS Code**: tasks for dev, migrations, tests, and seeding (`.vscode/tasks.json`).
- **Devcontainer**: containerized workspace aligned with the Compose stack.
- **CI/CD**: GitHub Actions workflow runs linting and tests on push/PR.

## Next Steps

- Flesh out FastAPI services, Celery tasks, and shared domain models.
- Implement real ETL connectors, rules engine, and validation logic.
- Build the Next.js readiness dashboard and exception workflows.
- Expand integration and end-to-end test coverage.
