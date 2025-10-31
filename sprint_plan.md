Sprint Plan — CRDC PreCheck (VS Code + OpenAI Agent)

Timeline: 3 Sprints × 2 weeks (plus Sprint 0 setup)
Team: 1 PM, 1 BE, 1 FE, 1 Data/ETL, 1 QA (can compress to 2–3 people by sequencing)
Stack:

Backend: Python 3.11, FastAPI, SQLAlchemy, Pydantic, Celery/Redis

DB: Postgres 15 (RLS enabled), pg_partman (optional), pgcrypto

Storage: S3-compatible (MinIO for local)

Frontend: React + Next.js (App Router), TanStack Query, Tailwind

PDF/ZIP: WeasyPrint or ReportLab + zipfile

Auth/SSO: OIDC/SAML adapters; Clever/ClassLink SSO (MVP SSO toggle)

Infra/Dev: Docker Compose, devcontainers, Makefile, pre-commit, Ruff/Black, Vitest/Jest, PyTest

Observability: OpenTelemetry, Prometheus/Grafana (docker), Sentry (optional)

Sprint 0 (3–4 days) — Environment, Repo, Guardrails
Goals

One-command dev environment.

Monorepo scaffold with strict lint/tests.

OpenAI agent wired into VS Code workflows.

Deliverables

Monorepo:

crdc-precheck/
├─ apps/
│  ├─ api/            # FastAPI
│  ├─ worker/         # Celery tasks
│  └─ web/            # Next.js
├─ packages/
│  ├─ rules/          # rules DSL + validator
│  └─ shared/         # domain models/types
├─ infra/
│  ├─ docker/         # compose files
│  ├─ db/             # migrations, seed, RLS
│  └─ grafana/
├─ tests/
├─ .devcontainer/
├─ .github/workflows/
├─ Makefile
└─ README.md


VS Code config (.vscode/):

tasks.json: run dev servers, tests, migrations

launch.json: API debug, web debug, worker debug

Devcontainer: Postgres, Redis, MinIO, Prometheus, Grafana, Mailhog

Make targets:

make dev (compose up + hot reload)

make migrate (alembic upgrade head)

make seed (synthetic demo data)

make test (API + web + e2e)

make lint (ruff/black/eslint)

Security Guardrails:

.env.template with no real secrets; use docker secrets in local

PII masking helpers (log filters)

Pre-commit hooks (secret detection)

OpenAI Agent usage:

Prompt templates (/prompts/) for codegen, tests, SQL, and docs

“Generate-then-Review” workflow (agent proposes, human reviews)

Agent Prompt Template (snippet)
/prompts/module_scaffold.md

“You are a senior Python engineer. Generate a FastAPI router for rule_results with CRUD, pagination, RLS-safe SQLAlchemy queries. Include unit tests (pytest) and dependency-injected services. Do not hardcode secrets. Follow apps/api/style_guide.md.”

Sprint 1 (Weeks 1–2) — Data Foundations, Ingestion, Rules v1

Epics covered: E1, E2, E3, E4, E6 (baseline), E15 (indexes)

Objectives

Multi-tenant API with RLS.

Canonical schema & migrations.

CSV importer + mapping UI.

PowerSchool connector (read-only).

Rules engine core + 10 priority rules.

Minimal “Validate now” flow + basic result list.

Work Breakdown

1) Tenancy/Auth (E1)

RLS policies on all tenant tables.

Roles: admin, data_engineer, reviewer, readonly.

Session tokens (MVP) with role claims.

2) DB & Migrations (E4)

Create core tables from Data Model.

Constraints: single active enrollment/day; non-negative durations.

Indexes: hot paths (rule_result(district_id,severity,status)).

3) CSV Import & Mapping (E3)

Upload → schema check → save mapping profile.

Row-level reject report (download CSV).

Save ingest_batch lineage.

4) PowerSchool Connector (E2)

OAuth/Token, entities: Student, Enrollment, Section, Staff, Incidents.

Nightly scheduled sync + metrics (rows, duration).

5) Rules Engine v1 (E6)

YAML/JSON DSL parser, deterministic evaluator.

10 rules across Enrollment & Discipline (e.g., ENR-001, DIS-101).

Results writer with lineage references.

6) Minimal UI (E7/E8)

Run Validation: district scope.

Results Table: severity, rule code, entity link.

Filters: severity; CSV export.

7) Testing & Observability (E12/E15)

PyTest (≥80% touched modules), Jest/Vitest for importer UI.

OpenTelemetry traces for ingestion & rule runs.

Grafana dashboard: connector health, last run, validation duration.

Demos / Exit Criteria

Connect demo PowerSchool sandbox or synthetic CSV.

Run validation → see open results with lineage.

Export results CSV; show RLS isolation by user role.

Metrics visible in Grafana.

Sprint 2 (Weeks 3–4) — Exceptions, Evidence, Readiness, IC Connector

Epics covered: E7, E8, E9, E10, E2 (IC), E12

Objectives

Exceptions workflow (assign, due date, bulk actions).

AI-drafted Exception Memo (editable).

Evidence Packet generator (PDF/ZIP).

Readiness Score + Heatmap dashboard.

Infinite Campus connector parity with PowerSchool.

Work Breakdown

1) Exceptions & Workflow (E8)

Result list: filters (severity, school, rule, owner, status).

Assignments, due dates, status transitions.

Comments + activity log.

2) AI-Drafted Memos (E9)

Template injection: rule context, entity snippet, remediation.

Editable Markdown body; save versions.

Guardrails: no PII echo by default; reviewers can insert specific values.

3) Evidence Packets (E9)

Packet generator: cover sheet, CSV slice, ZIP bundle.

SHA-256 hash; stored in S3/MinIO.

Approval/sign-off (Reviewer/Legal) with signature block.

4) Readiness Dashboard (E10)

Scoring: weighted severity per category/school.

Heatmap + drill-down to results.

Trend deltas vs prior run.

5) Infinite Campus Connector (E2)

Same entities & nightly sync; shared ingestion pipeline.

6) Admin Health Console (E12)

Connector status, last sync, last validation, queue depth.

7) QA / E2E

Playwright/Cypress e2e: run → triage → memo → packet → approval.

Load samples (250k students synthetic batch) for perf smoke.

Demos / Exit Criteria

Full pre-check flow: results → assign → memo → packet → approve.

Readiness score/heatmap updates after resolution.

IC sync green; admin health shows green checks.

Sprint 3 (Weeks 5–6) — SSO/RBAC, Performance, Hardening, Pilot

Epics covered: E1 (SSO), E11, E12, E15, E14, E13 (exports)

Objectives

Clever/ClassLink SSO + RBAC enforcement (UI & API).

Performance tuning for large districts.

Security: encryption, audit logs, retention settings.

Exports (PDF/XLSX) and share links.

Onboarding wizard + docs; Pilot prep.

Work Breakdown

1) SSO & RBAC (E1/E11)

Clever/ClassLink SSO integration.

Role enforcement on routes & UI (feature flags).

IP allowlisting (optional).

2) Security & Compliance (E11)

TLS termination in local proxy; AES-256 at rest (S3 enc).

Audit logs for reads/writes/exports; access reports.

Data retention setting per tenant; purge job.

3) Performance & Scale (E15)

Partition hot tables (rule_result, incidents) by district.

Parallel validation sharding per school; worker autoscale (compose profiles).

Load tests; p95 budgets met (see NFRs).

4) Exports & API (E13)

PDF/XLSX exports (dashboard views, exception lists).

Read-only REST endpoints for downstream BI; signed URLs.

5) Onboarding (E14)

4-step wizard: SSO → Connector → CSV → Run validation.

In-app docs & tooltips; link to CRDC references.

6) Pilot Ops & Finish

Success metrics panel (time saved, error reduction).

Pilot configuration profiles (rules toggles).

Handoff docs & runbooks.

Demos / Exit Criteria

SSO login works; roles limit screens/actions.

Validation on large synthetic district finishes within targets.

Audit logs & exports verified; onboarding wizard completes in <30 minutes.

VS Code & Agent Workflow (Daily)

Open the workspace: crdc-precheck.code-workspace with multi-root settings.

Devcontainer up: Reopen in Container → make dev (API, web, worker, db, redis, minio, grafana).

Use the agent for scaffolds:

“Generate FastAPI router + tests for /exceptions with pagination & RBAC.”

“Write Alembic migration for rule_result partitioning (hash by district).”

“Produce React component for Readiness Heatmap with TanStack Query + API hook.”

Run tests: make test or VS Code Test Explorer.

Profiling/tuning: OpenTelemetry traces in VS Code + Grafana panels.

Code review: PR templates enforce security & performance checklists.

Example Artifacts & Config
.vscode/tasks.json (excerpt)
{
  "version": "2.0.0",
  "tasks": [
    { "label": "Dev Up", "type": "shell", "command": "make dev" },
    { "label": "Migrate", "type": "shell", "command": "make migrate" },
    { "label": "API Tests", "type": "shell", "command": "pytest -q" },
    { "label": "Web Tests", "type": "shell", "command": "pnpm --dir apps/web test" },
    { "label": "Seed Data", "type": "shell", "command": "make seed" }
  ]
}

Makefile (excerpt)
dev:
\tdocker compose -f infra/docker/compose.yml up --build
migrate:
\tcd apps/api && alembic upgrade head
seed:
\tpython scripts/seed_synthetic.py
test:
\tpytest -q && pnpm --dir apps/web test
lint:
\truff check . && black --check . && pnpm --dir apps/web lint

Agent Prompts (drop-in)

Rule Engine Unit:
“Generate a rules/evaluator.py that loads YAML, compiles predicates safely (no eval), supports field accessors (student.race_ethnicity), and returns RuleResult models. Add pytest with fixtures and 10 sample rules.”

Connector Dataflow:
“Create apps/api/connectors/powerschool.py with token refresh, pagination, and backoff. Normalize to canonical models; write to DB with lineage + ingest_batch references. Include integration tests with recorded fixtures.”

Readiness Heatmap:
“Implement apps/web/app/(dashboard)/readiness page. Fetch /readiness?school_id=&category=. Render a grid heatmap with drill-downs. Add tests and loading/error states.”

QA Strategy & Test Matrix

Unit: rules evaluator, mappers, RBAC guards, CSV parser.

Integration: connector → ETL → DB; validation run writes results; evidence packet generation.

E2E: Cypress/Playwright: run validation → triage exceptions → generate memo → create packet → approval → readiness updates.

Performance: 250k students synthetic; measure validation p95 per school, total run time, queue depth.

Security: RLS tests (cross-tenant access denied), secret scanners, PII mask in logs, export permissions.

CI/CD (GitHub Actions)

build.yml: lint, unit/integration tests, web tests, build docker images.

e2e.yml: spin up stack, run Cypress/Playwright.

security.yml: Trivy on images, gitleaks, dependency audit.

perf.yml: nightly perf smoke with synthetic data.

release.yml: tag → push images to registry; generate changelog; upload Helm chart (if k8s later).

Definition of Done (per Sprint)

Meets sprint exit criteria & NFRs.

Tests ≥80% on changed modules; e2e happy path green.

Telemetry & dashboards in place for new flows.

Security review complete (if PII touched).

Docs updated: README, runbooks, API reference, onboarding steps.

Risk Log & Mitigation

Connector variance/throttling: Implement backoff & quota; CSV fallback.

Rule misinterpretation: Versioned rules + review with SMEs; feature flags per tenant.

Performance spikes in crunch window: Shard by school; autoscale workers; pre-warm caches.

PII exposure in AI memos: Default redact; reviewer opt-in to reveal specifics.

Sprint Mapping to Backlog (highlights)
Sprint	Must-Ship Stories
S1	US-001,002,010,020,021,022,030,031,050,051,060,061,110,140,141
S2	US-070,071,072,080,081,082,083,090,091,011,110
S3	US-003,100,101,102,120,121,122,130 (wizard), 150,151
Pilot Readiness Checklist (end of Sprint 3)

 SSO enabled and RBAC verified

 Connectors healthy (PS + IC) or CSV path complete

 Validation SLA met on synthetic large district

 Exceptions → Memo → Evidence → Approval flow solid

 Readiness dashboard trusted by pilot users

 Audit logs accessible; exports gated

 Onboarding wizard + docs complete

 Support runbook + escalation paths in place
