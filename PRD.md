PRD — CRDC PreCheck

Audience: U.S. K–12 Data & Accountability Directors, SIS/LMS/HR admins
Purpose: Automate data extraction, pre-validation, and documentation for the Civil Rights Data Collection (CRDC) so districts submit clean, defensible data without last-minute fire drills.

1) Purpose & Goals

Problem: Every two years, districts scramble to assemble/validate CRDC data across SIS/LMS/HR systems, leading to high error rates, overtime, and audit risk.

Product Goal: An AI-powered SaaS that:

Auto-extracts CRDC-relevant data from SIS/LMS/HR

Runs pre-validation against CRDC business rules

Generates one-click exception memos and evidence packets

Provides readiness dashboards and audit trails

Success Criteria:

Reduce pre-submission errors by ≥70%

Cut CRDC prep time by ≥50%

Produce audit-ready evidence for 100% flagged exceptions

Hit NPS ≥ 50 with target users during pilot

2) Target Users & Personas

Primary Persona — Data & Accountability Director

Needs: Fast, accurate pre-check; rule clarity; exception documentation; sign-off workflow.

Wins: Single view of readiness; fewer rework cycles; defensible submissions.

Secondary Persona — SIS/LMS/HR Data Engineer/Admin

Needs: Clear data mappings; repeatable extractions; field-level traceability.

Wins: Automated jobs, schema maps, deltas, and source-of-truth lineage.

Tertiary Persona — Superintendent/Legal (Reviewer)

Needs: Confidence & audit readiness; clear exception rationale.

Wins: Evidence packets & sign-offs with risk scoring.

3) Scope
In-Scope (MVP)

Connectors: PowerSchool, Infinite Campus (read-only), SSO/user provisioning via Clever/ClassLink

Flat-file/CSV import templates

Rule engine for high-impact CRDC table groups (MVP):

Enrollment & Demographics (race/ethnicity, sex)

Students with Disabilities (IDEA & 504)

English Learners

Discipline (ISS/OSS, expulsions, arrests, referrals)

Restraint/Seclusion

Advanced Coursework (AP/IB, Algebra I)

Staff FTE high-level counts

Exception memos (auto-drafted), evidence packet generation (PDF/ZIP)

Readiness dashboard & heatmap

Audit trail & data lineage to source records

Role-based access control (RBAC), SSO (Clever/ClassLink), FERPA-aligned data handling

Out-of-Scope (MVP)

Full write-back to SIS/LMS/HR

All CRDC edge-case categories

Multi-language UI

District-to-state rollups

4) Key Requirements
Functional

Data Ingestion

OAuth/API for PowerSchool/Infinite Campus; nightly incremental pulls

CSV import with schema validation & guided mapping

Entity resolution (student/staff deduping) with confidence scoring

Rules & Validation

Versioned Rules Catalog by CRDC collection year

Deterministic checks + AI-assisted anomaly detection

Rule outputs: Error / Warning / Info, severity, remediation hints

Field-level lineage: source system, table, record ID, timestamp

Exceptions & Documentation

One-click Exception Memo: context, rule, rationale, remediation

Evidence Packet: data extract, screenshots guidance, policy references, sign-offs

Bulk resolve/defer with reason codes; workflow for review/approval

Readiness & Reporting

Readiness score by table group/school

Trend deltas vs prior collection

Export: CSV, XLSX, PDF; API for downstream BI

Admin & Security

RBAC: Admin, Data Engineer, Reviewer, Read-only

SSO via Clever/ClassLink; optional SAML/OIDC

Audit logs (who/what/when), IP allowlisting

Non-Functional

Security/Privacy: FERPA/COPPA aligned; PII minimization; at-rest/in-transit encryption; least-privilege; data retention policies

Reliability: 99.9% uptime target during CRDC windows; zero data loss RPO; 1h RTO

Performance: Validate 250k student districts ≤ 2h end-to-end nightly; on-demand rule run ≤ 10 min for a school

Scalability: Multi-tenant; horizontal scaling of ETL and rule engine

Operability: Feature flags by collection year; rules hot-reload; connector health checks

Compliance Readiness: SOC 2 path (post-MVP), DPA templates, data residency in U.S.

5) System Architecture (Overview)

Connectors Layer: PowerSchool, Infinite Campus (REST/GraphQL/SIF where applicable); CSV importer; Clever/ClassLink (SSO & rostering)

Ingestion/ETL: Schema mappers, PII minimizer, entity resolver, incremental change capture

Validated Warehouse: Normalized domain models (Student, Staff, Enrollment, Discipline, Course, Section, Incident)

Rules Engine: Versioned ruleset (YAML/JSON) + deterministic evaluator + anomaly detector

Application Services: Exceptions service, Evidence packet generator (PDF/ZIP), Readiness scorer, Audit logger

API & UI: GraphQL/REST API; React/Next.js UI; Job queue (e.g., Celery/Sidekiq)

Storage: Postgres (OLTP), object storage for packets, Redis for queues/cache

Security: KMS-managed keys; Vault for secrets; IAM isolation per tenant

6) Data Model (MVP)
Entities (selected)

District(id, name, nces_id)

School(id, district_id, name, nces_id, level)

Student(id, sis_id, state_id, dob, sex, race_ethnicity[], ell_flag, idea_flag, sec504_flag, grade, enrollment_status)

Staff(id, sis_id, role, fte, school_id, highly_qualified_flag)

Course(id, code, title, ap_flag, ib_flag, algebra1_flag)

Section(id, course_id, school_id, term, teacher_staff_id)

Enrollment(id, student_id, school_id, section_id, start_date, end_date, status)

DisciplineIncident(id, student_id, date, school_id, type, duration_days, law_enforcement_referral_flag, arrest_flag, expulsion_flag, iss_flag, oss_flag)

RestraintSeclusion(id, student_id, date, type, duration_minutes, staff_present[])

RuleResult(id, rule_code, entity_type, entity_id, severity, status, details_json, created_at, resolved_by, resolution_note)

EvidencePacket(id, scope, rule_result_ids[], pdf_url, zip_url, created_at)

User(id, role, email, sso_provider, district_id)

Example: Rules DSL (YAML)
- code: ENR-001
  year: 2025
  applies_to: Student
  severity: error
  description: "Every enrolled student must have exactly one race/ethnicity."
  predicate: "len(student.race_ethnicity) == 1"
  remediation: "Update race/ethnicity selection in SIS; ensure no duplicates."
- code: DIS-101
  year: 2025
  applies_to: DisciplineIncident
  severity: warning
  description: "Suspension >10 days requires review."
  predicate: "incident.oss_flag and incident.duration_days > 10"
  remediation: "Confirm documentation and due process records are attached."

7) Rules Catalog (MVP Focus Areas)

Enrollment/Demographics

Missing/invalid race/ethnicity; sex missing; grade out-of-range; duplicate active enrollments

Disabilities (IDEA/504)

IDEA/504 flags misaligned with services; conflicting flags; missing IEP start/end

English Learner

ELL flag present without test date; expired status; missing proficiency level

Discipline

Incident type/flag conflicts (e.g., expulsion + zero days); >10 day suspensions; missing law-enforcement indicator

Restraint/Seclusion

Event without staff; duration zero or extreme; multiple events same timestamp

Advanced Coursework

AP/IB enrollment counts inconsistent with section/course flags; Algebra I grade misclassification

8) Exception Memos & Evidence Packets

Exception Memo (auto-drafted):

Title: Rule code + summary

Context: Student/School, timeframe, source lineage

Rule: Description, CRDC table group reference

Proposed Rationale: AI-suggested text, editable

Remediation Steps: SIS/LMS actions

Status/Owner/Due Date

Evidence Packet (PDF/ZIP):

Cover sheet: Summary & sign-offs

Data extract: CSV/XLSX slice for impacted records

Screenshots guidance checklist (SIS pages to capture)

Policy references (district codes, handbook excerpts)

Change log (who/what/when)

Final approval signature

9) Readiness & Reporting

Readiness Score: Weighted by severity & count per table group/school

Heatmap: Schools × categories (green/yellow/red)

Trends: Compare to prior collection; show top improvements & regressions

Exports: CSV/XLSX/PDF; API for BI tools

10) Integrations (MVP)

PowerSchool / Infinite Campus: Read-only API (students, enrollments, sections, incidents, staff)

Clever / ClassLink: SSO & user provisioning; optional rostering checks

CSV Templates: Mapped to canonical model; upload wizard with validation

11) Security, Privacy, Compliance

FERPA-aligned processing; DPA templates

At-rest (AES-256) & in-transit (TLS 1.2+) encryption; KMS-managed keys

RBAC + least privilege; IP allowlists; audit logs exposed to admins

U.S. data residency; configurable retention and purge

12) Analytics & Telemetry

Connector health, ingestion latency, validation duration

Rule hit rates by category & school

Evidence packet creation and approval funnel

User activity & task completion times

13) Assumptions & Risks

Assumptions

Districts can provide API access or CSV exports

CRDC business rules are publicly codifiable per year

Risks

Connector API variance & throttling

Rule misinterpretation—mitigated with versioning & legal review

Data quality edge cases—mitigated with lineage & human-in-the-loop review

14) MVP Backlog (Epics → Sample User Stories)

E1. Data Ingestion & Mapping

As a Data Engineer, I can connect PowerSchool and schedule nightly pulls (AC: OAuth, success ping, delta support).

As a Data Engineer, I can upload CSVs and map columns to the canonical schema (AC: template validation, mapping saved).

E2. Entity Resolution & Lineage

As a Director, I can see the source system/record for any validation finding (AC: clickable lineage panel).

E3. Rules Engine (2025 Ruleset)

As a Director, I can run validations by school/table group (AC: severity counts, run time ≤10 min/school on-demand).

As an Admin, I can select the CRDC year and rules version (AC: hot-reload rules without deploy).

E4. Exceptions & Workflow

As a Director, I can bulk-resolve or assign exceptions with reasons (AC: status, owner, due date, audit log).

As a Reviewer, I get AI-drafted exception memos (AC: editable, saved, exportable).

E5. Evidence Packets

As a Director, I can generate a packet for selected exceptions (AC: PDF cover, CSV slice, zip with artifacts).

E6. Readiness Dashboard

As a Director, I see readiness scores by school/category (AC: heatmap, filter, export).

E7. Security & SSO

As an Admin, I can enforce SSO (Clever/ClassLink) and RBAC (AC: role matrix, audit log events).

E8. Observability & Admin

As an Admin, I can monitor connector health and last run times (AC: health page, alerts).

E9. Docs & Onboarding

As a Director, I can follow step-by-step setup and CSV templates (AC: embedded guides, tooltips).

15) Acceptance Criteria (High-Level)

Connectors authenticate and pull ≥95% required fields for MVP categories

Validation runs complete within stated performance targets

Every exception has lineage, remediation hints, and can be assigned/resolved

Evidence packets export successfully with unique hash, stored securely

RBAC & SSO enforced; audit logs capture all data/view/changes

16) Metrics (Product & Business)

Product

Error reduction %, time saved hours/district, #exceptions resolved/created, rule coverage %, packet generation rate

Business

Conversion to paid pilots, ARR per district ($4–12k/collection), renewal %, gross margin, support ticket volume

17) 3-Sprint Implementation Plan (6 weeks total)
Sprint 1 (Weeks 1–2): Foundations

PowerSchool read-only connector (students, enrollments, incidents, staff)

CSV importer + mapping UI + schema validation

Canonical data model + Postgres + S3 object storage

Rules engine core + 10 baseline rules (Enrollment, Discipline)

Minimal readiness view (counts by severity)

Deliverable: Ingest + first validations + CSV exports

Sprint 2 (Weeks 3–4): Exceptions, Evidence, Dashboard

Exceptions service (assign, status, bulk actions)

AI-drafted Exception Memo v1 (templated, editable)

Evidence Packet generator (cover + CSV slice + ZIP)

Readiness heatmap & filters; lineage panel

Infinite Campus connector (key entities)

Deliverable: End-to-end pre-check flow for pilot schools

Sprint 3 (Weeks 5–6): SSO, Scale, Pilot Hardening

Clever/ClassLink SSO + RBAC

Performance tuning (batching, parallelism), observability dashboard

Expand rules to 30+ across MVP categories; rules versioning UI

Audit logs, exports (PDF/XLSX), admin health page

Pilot onboarding guide & CSV templates

Deliverable: Pilot-ready release with security, scale, and docs

18) Go-To-Market (Snapshot)

Pricing: $4k–$12k per district per collection (bi-annual); multi-year discounts

ARR Path: 200 districts × $6k avg = $1.2M

Beachhead: Districts on PowerSchool/Infinite Campus with ≥10k students

Value Proof: Time saved, error reduction, audit-ready packets

19) Glossary (selected)

CRDC: Federal Civil Rights Data Collection (biennial)

Pre-validation: Checking data against rules before official submission

Exception Memo: Documented rationale/remediation for flagged items

Evidence Packet: Defensible artifact bundle for audits and sign-offs
