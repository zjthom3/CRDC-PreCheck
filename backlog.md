CRDC PreCheck — Product Backlog (v0.1)

Scope: Full backlog for MVP + near-term (Post-MVP).
Conventions:

Roles: Director (Data & Accountability), Data Eng, Admin, Reviewer, Legal

Priority: P0 (critical), P1 (important), P2 (nice-to-have)

Estimate: Story points (SP) using Fibonacci (1–13)

AC format: Given / When / Then

Dependencies: Epic or story IDs

Epic E1 — Tenancy, Auth, RBAC

Goal: Secure, multi-tenant access with least privilege.

Stories

US-001 | Tenant bootstrap & RLS — Admin can create district tenants with row-level security. P0, 5SP
AC: Given a new district, when created, then all queries are RLS-scoped to district_id.

US-002 | Roles & permissions (RBAC matrix) — Admin assigns roles: admin, data_engineer, reviewer, readonly. P0, 3SP
AC: When a user role changes, then permitted routes & actions update without redeploy.

US-003 | SSO via Clever/ClassLink — User signs in with Clever/ClassLink. P0, 8SP
AC: Given valid SSO, when login, then user is provisioned/updated and session issued.

US-004 | Session management & audit — Admin can view recent logins, revoke sessions. P1, 3SP

US-005 | IP allowlisting (optional) — Restrict access by CIDR list. P1, 5SP

Dependencies: none

Epic E2 — Source Systems, Connectors & Scheduling

Goal: Pull CRDC-relevant data from SIS (PowerSchool/Infinite Campus) reliably.

Stories

US-010 | PowerSchool connector (read-only) — OAuth/token auth; students, enrollments, sections, staff, incidents. P0, 13SP
AC: A scheduled sync ingests ≥95% required MVP fields with metrics.

US-011 | Infinite Campus connector (read-only) — Same entities as US-010. P0, 13SP

US-012 | Connector health & retry — Status, error surfacing, backoff, throttling. P0, 5SP

US-013 | Scheduled nightly syncs — Cron/queue; district local TZ. P0, 3SP

US-014 | Manual on-demand sync — Data Eng runs now; lock prevents overlap. P1, 3SP

Dependencies: E1

Epic E3 — CSV Import, Mapping & Validation

Goal: Support districts lacking API access or for supplemental data.

Stories

US-020 | CSV templates & schema validation — Generate templates aligned to canonical model. P0, 5SP

US-021 | Column mapping UI — Save re-usable mapping profiles per file type. P0, 8SP

US-022 | Row-level error report — Downloadable CSV of rejects with reasons. P0, 3SP

US-023 | Incremental imports — Upsert strategy with source hash tracking. P1, 5SP

US-024 | Bulk delete by batch — Safe rollback of a bad import. P2, 3SP

Dependencies: E4

Epic E4 — Canonical Data Model & Lineage

Goal: Normalized entities with traceable lineage.

Stories

US-030 | Canonical tables — Student, Staff, Course, Section, Enrollment, Incidents, Programs. P0, 8SP

US-031 | Lineage on all rows — Source system/table/record/hash + batch id. P0, 5SP

US-032 | PII minimization & masking — Role-based field masking in queries/exports. P0, 5SP

US-033 | Constraints & checks — Single active school enrollment per day; non-negative durations. P1, 3SP

Dependencies: E1

Epic E5 — Entity Resolution & Deduplication

Goal: Consistent identity across sources.

Stories

US-040 | Student dedupe heuristic — SIS ID > state ID > name+DOB fuzzy. P0, 8SP

US-041 | Staff dedupe — SIS ID + email fallback. P1, 5SP

US-042 | Merge review UI — Data Eng approves/overrides candidate merges. P1, 8SP

US-043 | Merge audit & rollback — Log before/after with revert. P1, 5SP

Dependencies: E4

Epic E6 — Rules Engine & Catalog (CRDC 2025)

Goal: Versioned rules with deterministic evaluation and hints.

Stories

US-050 | Rules catalog v2025 — Define 30+ rules (Enrollment, Discipline, ELL, IDEA/504, Restraint, Advanced Coursework). P0, 8SP

US-051 | Deterministic evaluator — YAML/JSON DSL, field accessors, filters. P0, 8SP

US-052 | Severity & categories — Error/Warning/Info with table group mapping. P0, 3SP

US-053 | Remediation hints — Configurable text per rule, surfaced in UI. P1, 3SP

US-054 | Rules versioning & toggles — Enable/disable per district. P1, 5SP

Dependencies: E4

Epic E7 — Validation Runs & Scheduling

Goal: On-demand and scheduled pre-checks with scoping.

Stories

US-060 | Run by scope — District-wide, by school, by category. P0, 5SP

US-061 | Performance targets — ≤10 min per school on-demand; metrics recorded. P0, 3SP

US-062 | Concurrent sharding — Queue workers per school; progress UI. P1, 8SP

US-063 | Resume failed runs — Idempotent rerun of failed shards only. P1, 5SP

Dependencies: E6

Epic E8 — Exceptions, Assignments & Workflow

Goal: Turn rule results into actionable work with accountability.

Stories

US-070 | Result list & filters — Filter by severity, school, rule, owner, status. P0, 5SP

US-071 | Assign & due dates — Owners, due dates, status (open/in_review/resolved/won’t_fix). P0, 5SP

US-072 | Bulk actions — Multi-select resolve/defer with reason codes. P0, 3SP

US-073 | Activity & comments — Threaded notes per exception. P1, 3SP

US-074 | Notifications — Email in-app for assignments & nearing due dates. P1, 5SP

Dependencies: E7

Epic E9 — Exception Memos & Evidence Packets

Goal: One-click, defensible documentation bundles.

Stories

US-080 | AI-drafted memo (editable) — Prepopulated context, rule, suggested rationale. P0, 8SP

US-081 | Evidence packet generator — Cover sheet, CSV slice, ZIP bundle, hash. P0, 8SP

US-082 | Evidence items — Upload files, link to exceptions; captions & types. P0, 5SP

US-083 | Approval/sign-off — Reviewer/Legal approve memos & packets. P1, 5SP

US-084 | Export PDF/XLSX — Print-ready packet and exception list. P1, 5SP

Dependencies: E8

Epic E10 — Readiness Dashboard & Reporting

Goal: Instant understanding of CRDC readiness and trends.

Stories

US-090 | Readiness score — Weighted severity per school/category. P0, 5SP

US-091 | Heatmap — Schools × categories (green/yellow/red) with drill-down. P0, 5SP

US-092 | Trend deltas vs prior collection — Top regressions/improvements. P1, 5SP

US-093 | Export & share — CSV/XLSX/PDF of dashboard views. P1, 3SP

US-094 | Bookmarkable filters — Shareable URLs preserve state. P2, 2SP

Dependencies: E7

Epic E11 — Security, Privacy & Compliance

Goal: FERPA-aligned handling, encryption, auditability.

Stories

US-100 | Encryption in transit/at rest — TLS 1.2+, AES-256, KMS rotation. P0, 5SP

US-101 | Audit log events — Who/what/when for reads/writes/exports. P0, 5SP

US-102 | Data retention policies — Configurable purge windows per tenant. P1, 3SP

US-103 | Access reports — Periodic export of access activity for Legal. P1, 3SP

US-104 | DPA templates — Downloadable agreements with variable fields. P2, 3SP

Dependencies: E1

Epic E12 — Observability & Admin Ops

Goal: Operability during crunch windows.

Stories

US-110 | Admin health console — Connector status, last sync, last validation, queue depth. P0, 5SP

US-111 | Metrics & alerts — Ingestion latency, validation duration, rule hit rates; alerts on SLO breaches. P1, 8SP

US-112 | Feature flags — Toggle connectors/rules/UI modules per district. P1, 3SP

US-113 | Rate limit & backpressure — Protect SIS APIs and our workers. P1, 5SP

Dependencies: E2, E6, E7

Epic E13 — Exports & APIs

Goal: Interop with district tools and BI.

Stories

US-120 | REST/GraphQL read APIs — Authz-gated endpoints for results & readiness. P1, 8SP

US-121 | Webhooks — Event notifications (run.completed, evidence.created). P1, 5SP

US-122 | Bulk export jobs — Async large downloads with signed URLs. P1, 5SP

Dependencies: E1, E7, E10

Epic E14 — Onboarding, Help & Templates

Goal: Time-to-value in <1 day.

Stories

US-130 | Guided setup — 4-step wizard: SSO, connector, CSV, run first validation. P0, 5SP

US-131 | In-app docs & tooltips — Embedded CRDC references, field definitions. P1, 3SP

US-132 | Sample datasets — Safe synthetic data for training/demo. P2, 3SP

Dependencies: E2, E3

Epic E15 — Performance & Scale

Goal: Hold up for 250k student districts.

Stories

US-140 | Partitioning & indexes — Hot paths (rule_result, incidents) optimized. P0, 5SP

US-141 | Parallel validation — Worker pool sizing; SLA checks. P0, 5SP

US-142 | Load tests — Baseline & regression gates in CI. P1, 5SP

Dependencies: E6, E7

Epic E16 — Legal & Audit Readiness

Goal: Confidence for Superintendent/Legal.

Stories

US-150 | Policy reference library — Attach district codes/policies to packets. P1, 3SP

US-151 | Chain-of-custody — Evidence hash, signer identity, timestamp. P1, 5SP

US-152 | Read-only audit role — View everything, export-limited. P1, 3SP

Dependencies: E9, E11

Epic E17 — Pilot Ops & Support

Goal: Smooth pilots with measurable ROI.

Stories

US-160 | Pilot configuration profiles — Predefined rules on/off, categories. P1, 3SP

US-161 | Success metrics panel — Time saved, error reduction, packet count. P1, 5SP

US-162 | Support desk integration — Create ticket from exception context. P2, 5SP

Dependencies: E8–E10

Epic E18 — Backup, DR & Residency

Goal: Protect data, meet residency requirements.

Stories

US-170 | Automated backups & restore — PITR tested quarterly. P1, 5SP

US-171 | US region pinning — Ensure US-only storage. P1, 3SP

US-172 | DR runbook — Documented RTO=1h, RPO≈0. P2, 3SP

Dependencies: E11

Post-MVP Epics (Near-Term)
Epic E19 — Additional SIS Connectors

US-190 | Skyward connector — Students/enrollments/discipline. P2, 13SP

US-191 | Aeries connector — Same entities. P2, 13SP

Epic E20 — Rules Authoring & Diff

US-200 | Rules editor UI — Create/edit rules with validation. P2, 8SP

US-201 | Version compare & impact preview — Diff rule versions & sample hits. P2, 8SP

Epic E21 — AI Anomaly Detection v2

US-210 | Outlier detector — Spot unlikely distributions (e.g., 0 arrests across all years). P2, 8SP

US-211 | Explainability cards — Why flagged; feature attributions. P2, 5SP

Epic E22 — Write-Back Assist (Guided)

US-220 | SIS navigation hints — Deep-link instructions/screen paths (no write). P2, 5SP

US-221 | Bulk export to SIS format — Pre-formatted CSV per SIS. P2, 5SP

Epic E23 — BI Connectors

US-230 | Power BI connector — DirectQuery model. P2, 8SP

US-231 | Looker/BigQuery export — Scheduled push. P2, 8SP

Epic E24 — Multilingual UI

US-240 | i18n framework — English baseline with tokenization. P2, 5SP

MVP Cutline (What ships first)

Epics: E1, E2, E3, E4, E5 (student only), E6, E7, E8, E9, E10, E11, E12, E14, E15
Key Stories (must-have): US-001/002/003/010/011/012/013/020/021/022/030/031/040/050/051/052/060/061/070/071/072/080/081/090/091/100/101/110/130/140/141

Sample User Story Detail (Template)
ID: US-071 — Assign & due dates
Role: Director
Need: Assign exceptions to owners with due dates to drive resolution
Priority: P0
Estimate: 5SP
Dependencies: US-070
Acceptance Criteria:
  - Given an open exception, when I assign an owner and set a due date, then the exception shows the owner, due date, and status "open".
  - Given a due date in the past, when the page loads, then I see a "overdue" badge and list is sortable by due date.
  - Given a change in ownership, when saved, then an audit log event is recorded with old/new owner.
Non-Functional:
  - Assignment mutation <300ms p95; changes visible to other users within 2s.
Test Notes:
  - Verify RLS prevents cross-district assignment.

Definition of Ready (DoR)

Clear role, need, and outcome

Acceptance criteria written

Dependencies identified

Estimation complete

UX states sketched (where applicable)

Definition of Done (DoD)

AC satisfied & peer-reviewed

Unit/integration tests ≥80% on touched modules

Observability: metrics & logs added

Docs updated (end-user and runbook)

Security review (if PII touched)
