CRDC PreCheck — Data Model (v0.1)

Practical, implementation-ready schema for a multi-tenant (district) Postgres stack. Types shown as postgres_type. All PKs are uuid unless noted. Timestamps are UTC. JSON details use jsonb.

Design principles

Multi-tenant by district (district_id) with Row-Level Security (RLS).

Lineage on every domain row (source system, record ids, hashes).

Versioned CRDC rules by collection year.

Immutable events (discipline, restraint) + current state (student, program flags).

Evidence is files with strong hashes; packets are bundles.

ER Diagram (high-level)
erDiagram
  DISTRICT ||--o{ SCHOOL : has
  DISTRICT ||--o{ USER_ACCOUNT : has
  SCHOOL ||--o{ SECTION : offers
  SCHOOL ||--o{ ENROLLMENT : hosts
  STUDENT ||--o{ ENROLLMENT : attends
  STAFF ||--o{ STAFF_ASSIGNMENT : teaches
  SECTION ||--o{ ENROLLMENT : includes
  STUDENT ||--o{ DISCIPLINE_INCIDENT : involved_in
  STUDENT ||--o{ RESTRAINT_SECLUSION_EVENT : involved_in

  CRDC_COLLECTION ||--o{ RULE_VERSION : contains
  RULE_VERSION ||--o{ RULE_RUN : executed_in
  RULE_RUN ||--o{ RULE_RESULT : produced
  RULE_RESULT ||--o{ EXCEPTION : tracked_by
  EXCEPTION ||--o{ EVIDENCE_ITEM : cites
  EVIDENCE_PACKET ||--o{ EVIDENCE_ITEM : groups

  SOURCE_SYSTEM ||--o{ CONNECTOR : uses
  CONNECTOR ||--o{ SYNC_JOB : runs
  SYNC_JOB ||--o{ INGEST_BATCH : creates

1) Tenancy & Access
district
column	type	notes
id	uuid PK	tenant id
nces_id	text unique	optional
name	text	
timezone	text	e.g., America/Chicago
created_at/updated_at	timestamptz	
school
column	type	notes
id	uuid PK	
district_id	uuid FK→district(id)	indexed
nces_id	text	
name	text	
level	text	enum hint: elementary/middle/high/other
created_at/updated_at	timestamptz	
user_account
column	type	notes
id	uuid PK	
district_id	uuid FK	RLS partition key
email	citext unique(district_id,email)	
display_name	text	
role	text	admin,data_engineer,reviewer,readonly
sso_provider	text	clever,classlink,saml,oidc
sso_subject	text	provider subject
is_active	boolean	
created_at/last_login_at	timestamptz	
audit_log
column	type	notes
id	bigserial PK	append-only
district_id	uuid	
user_id	uuid nullable	
action	text	e.g., VALIDATION_RUN, PACKET_EXPORT
entity_type	text	table name
entity_id	uuid	
details	jsonb	request params, diffs
ip	inet	
created_at	timestamptz	
2) Source, Ingestion, Lineage
source_system
column	type	notes
id	uuid PK	
district_id	uuid FK	
kind	text	powerschool,infinite_campus,csv
name	text	display
is_primary	boolean	
created_at	timestamptz	
connector
column	type	notes
id	uuid PK	
district_id	uuid	
source_system_id	uuid FK	
auth_method	text	oauth,token,csv_upload
status	text	healthy,degraded,error
last_sync_at	timestamptz	
sync_job
column	type	notes
id	uuid PK	
connector_id	uuid FK	
scheduled_at	timestamptz	
started_at/finished_at	timestamptz	
status	text	queued,running,success,failed
metrics	jsonb	rows, duration
error	text	nullable
ingest_batch
column	type	notes
id	uuid PK	
district_id	uuid	
source_system_id	uuid	
sync_job_id	uuid	
table_name	text	e.g., students
rows_ingested	int	
source_hash	text	end-to-end checksum
created_at	timestamptz	

Lineage columns (present on all domain tables below):

lineage_source_system_id uuid

lineage_source_table text

lineage_source_record_id text

lineage_source_hash text

ingest_batch_id uuid

Indexes: (district_id), (lineage_source_system_id,lineage_source_record_id)

3) Canonical Domain
student
column	type	notes
id	uuid PK	
district_id	uuid	
sis_id	text	stable external id
state_id	text	nullable PII
first_name/last_name	text	PII
dob	date	PII
sex	text	M,F,X,Unknown
race_ethnicity	text[]	CRDC categories
grade	text	normalized (PK,K,1..12,UE)
enrollment_status	text	active,inactive,withdrawn
ell_flag	boolean	
idea_flag	boolean	
sec504_flag	boolean	
created_at/updated_at	timestamptz	
lineage…	—	see above

Unique: (district_id,sis_id).

staff
column	type	notes
id	uuid PK	
district_id	uuid	
sis_id	text	
role	text	teacher,admin,para,security,other
fte	numeric(4,2)	
highly_qualified_flag	boolean	
school_id	uuid FK→school(id)	nullable
created_at/updated_at	timestamptz	
lineage…	—	
course
column	type	notes
id	uuid PK	
district_id	uuid	
code	text	
title	text	
ap_flag/ib_flag/algebra1_flag	boolean	CRDC indicators
created_at/updated_at	timestamptz	
lineage…	—	
section
column	type	notes
id	uuid PK	
district_id	uuid	
school_id	uuid FK	
course_id	uuid FK	
term	text	e.g., 2025-Fall
period	text	optional
teacher_staff_id	uuid FK→staff(id)	
created_at/updated_at	timestamptz	
lineage…	—	
enrollment
column	type	notes
id	uuid PK	
district_id	uuid	
student_id	uuid FK	
school_id	uuid FK	
section_id	uuid FK	nullable for school-level
start_date/end_date	date	
status	text	active,inactive,completed,withdrawn
lineage…	—	

Constraint: only one active school enrollment per student per day.

staff_assignment
column	type	notes
id	uuid PK	
district_id	uuid	
staff_id	uuid FK	
school_id	uuid FK	
section_id	uuid FK	
role	text	primary_teacher,co_teacher,para
start_date/end_date	date	
4) Event Tables (immutable)
discipline_incident
column	type	notes
id	uuid PK	
district_id	uuid	
student_id	uuid FK	
school_id	uuid FK	
occurred_at	date	
type	text	e.g., OSS,ISS,Expulsion,Referral,Arrest
duration_days	numeric(5,2)	
law_enforcement_referral_flag	boolean	
arrest_flag	boolean	
expulsion_flag	boolean	
oss_flag/iss_flag	boolean	
notes	text	
lineage…	—	
restraint_seclusion_event
column	type	notes
id	uuid PK	
district_id	uuid	
student_id	uuid FK	
school_id	uuid FK	
occurred_at	timestamptz	
type	text	restraint,seclusion
duration_minutes	int	
staff_present_ids	uuid[]	reference staff
notes	text	
lineage…	—	
5) Program Enrollment (flags with dates)
program_enrollment
column	type	notes
id	uuid PK	
district_id	uuid	
student_id	uuid FK	
program_type	text	ELL,IDEA,Section504
start_date/end_date	date	null end = active
attributes	jsonb	IEP dates, service levels
lineage…	—	

Unique active (district_id,student_id,program_type) with exclusion constraint on overlapping date ranges.

6) CRDC Collections & Rules
crdc_collection
column	type	notes
id	uuid PK	
district_id	uuid	tenant scope
year	int	e.g., 2025
window	daterange	official window
status	text	draft,active,closed
created_at/updated_at	timestamptz	
rule_version
column	type	notes
id	uuid PK	
crdc_collection_id	uuid FK	
code	text	e.g., ENR-001
title	text	
severity	text	error,warning,info
applies_to	text	table/entity
dsl	jsonb	normalized rule form
remediation	text	human guidance
enabled	boolean	feature-flag
created_at	timestamptz	

DSL shape example (dsl)
{ "predicate":"len(student.race_ethnicity)=1", "fields":["race_ethnicity"], "where":"student.enrollment_status='active'" }

rule_run
column	type	notes
id	uuid PK	
crdc_collection_id	uuid FK	
initiated_by_user_id	uuid FK	nullable (system)
scope	jsonb	filters (schools, categories)
started_at/finished_at	timestamptz	
status	text	running,success,failed
metrics	jsonb	duration, items checked
rule_result
column	type	notes
id	uuid PK	
rule_run_id	uuid FK	
rule_version_id	uuid FK	
district_id	uuid	
entity_type	text	Student,DisciplineIncident,…
entity_id	uuid	
severity	text	error,warning,info
status	text	open,resolved,deferred,accepted
details	jsonb	field diffs, sample rows
school_id	uuid nullable	quick filter
created_at/updated_at	timestamptz	

Indexes: (district_id,severity,status), (rule_version_id).

7) Exceptions & Evidence
exception
column	type	notes
id	uuid PK	
district_id	uuid	
rule_result_id	uuid FK	
owner_user_id	uuid FK	nullable
status	text	open,in_review,resolved,won't_fix
rationale	text	human/AI drafted
due_date	date	
approval_user_id	uuid FK	legal/superintendent
approved_at	timestamptz	
created_at/updated_at	timestamptz	
evidence_packet
column	type	notes
id	uuid PK	
district_id	uuid	
name	text	
description	text	
pdf_url	text	generated artifact
zip_url	text	bundle
sha256	text	integrity
created_by	uuid FK→user_account(id)	
created_at	timestamptz	
evidence_item
column	type	notes
id	uuid PK	
district_id	uuid	
evidence_packet_id	uuid FK	nullable (standalone)
exception_id	uuid FK	nullable
file_asset_id	uuid FK	
kind	text	csv,screenshot,policy,export
caption	text	
created_at	timestamptz	
file_asset
column	type	notes
id	uuid PK	
district_id	uuid	
file_name	text	
mime_type	text	
byte_size	bigint	
storage_url	text	S3/GCS
sha256	text	integrity
created_at	timestamptz	
exception_memo
column	type	notes
id	uuid PK	
district_id	uuid	
exception_id	uuid FK	
title	text	
body_md	text	markdown
generated_by	text	ai,user
created_at	timestamptz	
8) Readiness & Reporting
readiness_score
column	type	notes
id	uuid PK	
district_id	uuid	
crdc_collection_id	uuid FK	
school_id	uuid FK	nullable = district total
category	text	Enrollment,Discipline,…
score	numeric(5,2)	0–100
computed_at	timestamptz	

Materialized Views (examples)

mv_crdc_category_counts(year, district_id, school_id, category, severity, open_cnt, resolved_cnt)

mv_top_rules_by_hits(district_id, rule_code, open_hits)

Refresh on validation completion.

9) Integrations & Credentials
api_credential (encrypted)
column	type	notes
id	uuid PK	
district_id	uuid	
source_system_id	uuid FK	
name	text	
enc_payload	bytea	KMS-encrypted secrets
created_at/rotated_at	timestamptz	
10) Enumerations (suggested as lookup tables or Postgres enums)

crdc_race: AM7,AS7,BL7,HI7,WH7,TR7,UNKNOWN

incident_type: OSS,ISS,EXPULSION,REFERRAL,ARREST,OTHER

program_type: ELL,IDEA,Section504

severity: error,warning,info

status_result: open,resolved,deferred,accepted

exception_status: open,in_review,resolved,won't_fix

11) Indexing & Constraints (key examples)

student(district_id, sis_id) unique

discipline_incident(district_id, student_id, occurred_at) btree

rule_result(district_id, severity, status) btree

program_enrollment exclusion to prevent overlapping active periods per (district_id,student_id,program_type):

USING gist (district_id, student_id, program_type, daterange(start_date,end_date, '[]') WITH &&)

Partial index for open items:

CREATE INDEX ON rule_result (district_id, school_id) WHERE status='open';

12) Lineage & Data Quality

On every domain row:

lineage_source_system_id, lineage_source_table, lineage_source_record_id, lineage_source_hash, ingest_batch_id

Quality checks (DB constraints):

CHECK (array_length(race_ethnicity,1) BETWEEN 0 AND 1) if district enforces single selection

CHECK (duration_days >= 0); CHECK (duration_minutes >= 0)

13) Security, Privacy, Retention

RLS: USING (district_id = current_setting('app.district_id')::uuid) on all tenant tables.

PII classes:

Tier 1 (direct): name, DOB, state_id → masked in non-admin roles.

Tier 2: demographics/flags.

Tier 3: aggregates.

Retention: raw ingest batches & assets purged N days post-submission (configurable, default 365); evidence retained per district policy.

14) Partitioning & Scale

Table partitioning by district_id (hash) or crdc_collection_id (list) for:

rule_result, discipline_incident, restraint_seclusion_event, file_asset

Job queues (e.g., Redis) track rule_run execution shards by school.

15) Example Records (abridged)

rule_version

{
  "id":"2e5d...","crdc_collection_id":"a1b2...",
  "code":"ENR-001","title":"Exactly one race/ethnicity",
  "severity":"error","applies_to":"Student",
  "dsl":{"predicate":"len(student.race_ethnicity)==1","fields":["race_ethnicity"]},
  "remediation":"Update race/ethnicity in SIS","enabled":true
}


rule_result

{
  "id":"rres...","rule_run_id":"rrun...","rule_version_id":"rv...",
  "district_id":"dist...","entity_type":"Student","entity_id":"stu...",
  "severity":"error","status":"open",
  "details":{"student_sis_id":"12345","current_value":[],"expected":"single value"}
}

16) API Serialization Notes

All IDs as UUID strings.

Date/times ISO-8601.

Large exports streamed; evidence packets referenced by signed URLs.

17) Migration Order (suggested)

district, school, user_account

source_system, connector, api_credential, sync_job, ingest_batch

student, staff, course, section, enrollment, staff_assignment

discipline_incident, restraint_seclusion_event, program_enrollment

crdc_collection, rule_version, rule_run, rule_result

exception, evidence_packet, file_asset, evidence_item, exception_memo

Views/materialized views, indexes, RLS policies
