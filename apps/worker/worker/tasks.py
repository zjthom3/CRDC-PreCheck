import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.rules.rules.evaluator import evaluate_rule
from packages.rules.rules.models import RuleDefinition, RuleSeverity

from apps.api.app.db.models import (
    AuthMethodEnum,
    Connector,
    ConnectorStatusEnum,
    District,
    IngestBatch,
    IngestStatusEnum,
    RuleResult,
    RuleResultStatusEnum,
    RuleRun,
    RuleRunStatusEnum,
    RuleSeverityEnum,
    RuleVersion,
    SourceSystem,
    Student,
    SyncJob,
    SyncStatusEnum,
)
from apps.api.app.db.session import SessionLocal
from apps.api.app.services.students import upsert_student

from .app import app


@app.task(name="worker.tasks.heartbeat")
def heartbeat() -> dict[str, str]:
    """Return a timestamp to verify Celery scheduling works."""

    return {"status": "alive", "timestamp": datetime.now(tz=timezone.utc).isoformat()}


@app.task(name="worker.tasks.process_rule_run")
def process_rule_run(rule_run_id: str) -> dict[str, Any]:
    """Execute a rule run for the given identifier."""

    session: Session = SessionLocal()
    try:
        rule_run = session.get(RuleRun, UUID(rule_run_id))
        if rule_run is None:
            return {"status": "not_found", "rule_run_id": rule_run_id}

        rule_run.status = RuleRunStatusEnum.running
        rule_run.started_at = datetime.utcnow()
        session.commit()
        session.refresh(rule_run)

        rules = _load_rules(session, rule_run)
        violations_created = 0

        for rule in rules:
            violations_created += _apply_rule(session, rule_run, rule)

        rule_run.status = RuleRunStatusEnum.success
        rule_run.finished_at = datetime.utcnow()
        session.commit()
        return {"status": "success", "rule_run_id": rule_run_id, "violations": violations_created}
    except Exception:  # pragma: no cover - defensive logging branch
        session.rollback()
        rule_run = session.get(RuleRun, UUID(rule_run_id))
        if rule_run:
            rule_run.status = RuleRunStatusEnum.failed
            rule_run.finished_at = datetime.utcnow()
            session.commit()
        raise
    finally:
        session.close()


def _load_rules(session: Session, rule_run: RuleRun) -> list[RuleDefinition]:
    query = select(RuleVersion).where(RuleVersion.enabled.is_(True))
    if rule_run.rule_version_id:
        query = query.where(RuleVersion.id == rule_run.rule_version_id)
    else:
        query = query.where(
            (RuleVersion.district_id == rule_run.district_id) | (RuleVersion.district_id.is_(None))
        )

    rule_versions = list(session.execute(query).scalars())
    definitions: list[RuleDefinition] = []
    for rv in rule_versions:
        predicate = _compile_predicate(rv)
        definitions.append(
            RuleDefinition(
                code=rv.code,
                description=rv.title,
                severity=RuleSeverity(rv.severity.value),
                predicate=predicate,
            )
        )
    return definitions


def _compile_predicate(rule_version: RuleVersion):
    dsl = rule_version.dsl or {}
    rule_type = dsl.get("type")

    if rule_type == "grade_range":
        min_grade = dsl.get("min", 0)
        max_grade = dsl.get("max", 12)

        def predicate(record: dict[str, Any]) -> bool:
            grade = record.get("grade_level")
            return grade is not None and min_grade <= grade <= max_grade

        return predicate

    if rule_type == "enrollment_status":
        required_status = dsl.get("required", "active")

        def predicate(record: dict[str, Any]) -> bool:
            return record.get("enrollment_status") == required_status

        return predicate

    # Fallback to always passing if rule type unknown.
    return lambda record: True


def _apply_rule(session: Session, rule_run: RuleRun, rule: RuleDefinition) -> int:
    students = list(
        session.execute(
            select(Student).where(Student.district_id == rule_run.district_id)
        ).scalars()
    )
    student_dicts = [
        {
            "id": str(student.id),
            "school_id": str(student.school_id),
            "grade_level": student.grade_level,
            "enrollment_status": student.enrollment_status,
            "first_name": student.first_name,
            "last_name": student.last_name,
        }
        for student in students
    ]

    violations = evaluate_rule(rule, student_dicts)

    for violation in violations:
        student_id = UUID(violation["id"])
        school_uuid = UUID(violation["school_id"]) if violation.get("school_id") else None
        message = _build_violation_message(rule, violation)
        result = RuleResult(
            rule_run_id=rule_run.id,
            district_id=rule_run.district_id,
            school_id=school_uuid,
            entity_type="Student",
            entity_id=student_id,
            severity=RuleSeverityEnum(rule.severity.value),
            status=RuleResultStatusEnum.open,
            message=message,
            details=violation,
        )
        session.add(result)

    session.commit()
    return len(violations)


def _build_violation_message(rule: RuleDefinition, violation: dict[str, Any]) -> str:
    if rule.code == "GRADE-RANGE":
        grade = violation.get("grade_level")
        return f"Grade level {grade} outside configured range"
    if rule.code == "ENROLLMENT-STATUS":
        status = violation.get("enrollment_status")
        return f"Unexpected enrollment status: {status}"
    return rule.description


@app.task(name="worker.tasks.sync_powerschool")
def sync_powerschool(district_id: str) -> dict[str, Any]:
    """Simulate a PowerSchool sync by loading local sample data."""

    session: Session = SessionLocal()
    started_at = datetime.utcnow()
    job: SyncJob | None = None
    batch: IngestBatch | None = None
    try:
        district = session.get(District, UUID(district_id))
        if district is None:
            return {"status": "not_found", "district_id": district_id}

        source = session.execute(
            select(SourceSystem).where(
                SourceSystem.district_id == district.id, SourceSystem.kind == "powerschool"
            )
        ).scalar_one_or_none()
        if source is None:
            source = SourceSystem(
                district_id=district.id,
                kind="powerschool",
                name="PowerSchool",
                is_primary=True,
            )
            session.add(source)
            session.commit()

        connector = session.execute(
            select(Connector).where(Connector.source_system_id == source.id)
        ).scalar_one_or_none()
        if connector is None:
            connector = Connector(
                district_id=district.id,
                source_system_id=source.id,
                auth_method=AuthMethodEnum.token,
                status=ConnectorStatusEnum.healthy,
            )
            session.add(connector)
            session.commit()

        job = SyncJob(
            connector_id=connector.id,
            status=SyncStatusEnum.running,
            scheduled_at=started_at,
            started_at=started_at,
        )
        session.add(job)
        session.commit()

        batch = IngestBatch(
            district_id=district.id,
            source_system_id=source.id,
            sync_job_id=job.id,
            table_name="student",
            status=IngestStatusEnum.pending,
        )
        session.add(batch)
        session.commit()

        sample_path = Path(__file__).resolve().parents[3] / "samples" / "powerschool" / "students.json"
        data = json.loads(sample_path.read_text(encoding="utf-8"))

        rows = 0
        for entry in data:
            _upsert_student_from_dict(session, district.id, entry)
            rows += 1

        batch.rows_ingested = rows
        batch.status = IngestStatusEnum.success
        connector.status = ConnectorStatusEnum.healthy
        connector.last_sync_at = datetime.utcnow()
        job.status = SyncStatusEnum.success
        job.finished_at = datetime.utcnow()
        session.commit()

        return {"status": "success", "rows_ingested": rows, "sync_job_id": str(job.id)}
    except Exception:
        session.rollback()
        if job is not None:
            job.status = SyncStatusEnum.failed
            job.finished_at = datetime.utcnow()
            session.commit()
        if batch is not None:
            batch.status = IngestStatusEnum.failed
            session.commit()
        raise
    finally:
        session.close()


def _upsert_student_from_dict(session: Session, district_id: UUID, payload: dict[str, Any]) -> None:
    sis_id = payload["sis_id"]
    grade_level = int(payload.get("grade_level", 0))
    enrollment_status = payload.get("enrollment_status") or "active"
    school_name = payload.get("school_name") or "North High School"
    ell = payload.get("ell_status")
    idea = payload.get("idea_flag")
    upsert_student(
        session,
        district_id=district_id,
        sis_id=sis_id,
        first_name=payload.get("first_name", ""),
        last_name=payload.get("last_name", ""),
        grade_level=grade_level,
        enrollment_status=enrollment_status,
        school_name=school_name,
        ell_status=bool(ell) if ell is not None else None,
        idea_flag=bool(idea) if idea is not None else None,
    )
