"""Seed synthetic data for local development."""

from datetime import date, datetime

from sqlalchemy import func, select

from apps.api.app.db.models import (
    AuthMethodEnum,
    Connector,
    ConnectorStatusEnum,
    District,
    EvidenceItem,
    EvidenceKindEnum,
    EvidencePacket,
    ExceptionRecord,
    ExceptionStatusEnum,
    ReadinessScore,
    RuleResult,
    RuleRun,
    RuleRunStatusEnum,
    RuleSeverityEnum,
    RuleVersion,
    School,
    SourceSystem,
    Student,
    UserAccount,
    UserRoleEnum,
)
from apps.api.app.db.session import SessionLocal
from apps.worker.worker.tasks import process_rule_run


def main() -> None:
    session = SessionLocal()
    try:
        district = session.execute(select(District)).scalar_one_or_none()
        if district is None:
            district = create_demo_district(session)
            print("Created Demo Unified School District with sample data.")
        else:
            ensure_demo_data(session, district)

        ensure_rules(session, district)
        ensure_demo_user(session, district)
        ensure_powerschool_connector(session, district)
        violations = ensure_rule_run(session, district)
        create_sample_exceptions(session, district)
        bootstrap_readiness_scores(session, district)
        print(
            f"Seed data ready for district {district.name}. "
            f"Most recent validation produced {violations} violation(s)."
        )
    finally:
        session.close()


def create_demo_district(session: SessionLocal) -> District:
    district = District(name="Demo Unified School District", timezone="America/Chicago")
    session.add(district)
    session.flush()

    elementary = School(district_id=district.id, name="Central Elementary", level="elementary")
    high_school = School(district_id=district.id, name="North High School", level="high")
    session.add_all([elementary, high_school])
    session.flush()

    students = [
        Student(
            district_id=district.id,
            school_id=elementary.id,
            sis_id="E1001",
            first_name="Alex",
            last_name="Rivera",
            grade_level=3,
            enrollment_status="active",
            enrollment_start=date(2024, 8, 15),
        ),
        Student(
            district_id=district.id,
            school_id=elementary.id,
            sis_id="E1002",
            first_name="Taylor",
            last_name="Nguyen",
            grade_level=4,
            enrollment_status="active",
            enrollment_start=date(2024, 8, 15),
        ),
        Student(
            district_id=district.id,
            school_id=high_school.id,
            sis_id="H2001",
            first_name="Morgan",
            last_name="Lee",
            grade_level=10,
            enrollment_status="active",
            enrollment_start=date(2023, 8, 20),
        ),
        Student(
            district_id=district.id,
            school_id=high_school.id,
            sis_id="H2002",
            first_name="Jordan",
            last_name="Patel",
            grade_level=14,
            enrollment_status="active",
            enrollment_start=date(2022, 8, 22),
        ),
        Student(
            district_id=district.id,
            school_id=high_school.id,
            sis_id="H2003",
            first_name="Casey",
            last_name="Brooks",
            grade_level=11,
            enrollment_status="withdrawn",
            enrollment_start=date(2021, 8, 18),
            enrollment_end=date(2024, 1, 10),
        ),
    ]
    session.add_all(students)
    session.commit()
    return district


def ensure_demo_data(session: SessionLocal, district: District) -> None:
    schools_exist = session.execute(
        select(func.count(School.id)).where(School.district_id == district.id)
    ).scalar_one()
    students_exist = session.execute(
        select(func.count(Student.id)).where(Student.district_id == district.id)
    ).scalar_one()

    if not schools_exist or not students_exist:
        session.query(School).filter(School.district_id == district.id).delete()
        session.query(Student).filter(Student.district_id == district.id).delete()
        session.commit()
        create_demo_district(session)


def ensure_rules(session: SessionLocal, district: District) -> None:
    existing_codes = {
        code
        for (code,) in session.execute(
            select(RuleVersion.code).where(
                (RuleVersion.district_id == district.id) | (RuleVersion.district_id.is_(None))
            )
        )
    }

    to_create = []
    if "GRADE-RANGE" not in existing_codes:
        to_create.append(
            RuleVersion(
                district_id=district.id,
                code="GRADE-RANGE",
                title="Student grade level must be between 0 and 12",
                severity=RuleSeverityEnum.error,
                applies_to="Student",
                dsl={"type": "grade_range", "min": 0, "max": 12},
                remediation="Correct the student's grade level in SIS.",
            )
        )
    if "ENROLLMENT-STATUS" not in existing_codes:
        to_create.append(
            RuleVersion(
                district_id=district.id,
                code="ENROLLMENT-STATUS",
                title="Withdrawn students must not appear as active",
                severity=RuleSeverityEnum.warning,
                applies_to="Student",
                dsl={"type": "enrollment_status", "required": "active"},
                remediation="Update enrollment status or remove the record from exports.",
            )
        )

    if to_create:
        session.add_all(to_create)
        session.commit()


def ensure_demo_user(session: SessionLocal, district: District) -> None:
    token = "demo-admin-token"
    user = session.execute(
        select(UserAccount).where(UserAccount.district_id == district.id, UserAccount.email == "admin@demo.edu")
    ).scalar_one_or_none()

    if user is None:
        session.add(
            UserAccount(
                district_id=district.id,
                email="admin@demo.edu",
                display_name="Demo Admin",
                role=UserRoleEnum.admin,
                api_token=token,
                is_active=True,
                sso_provider="clever",
                sso_subject="demo-admin",
                last_login_at=datetime.utcnow(),
            )
        )
    session.commit()
        print("Created demo admin user (token: demo-admin-token).")


def ensure_powerschool_connector(session: SessionLocal, district: District) -> None:
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


def ensure_rule_run(session: SessionLocal, district: District) -> int:
    latest_run = (
        session.query(RuleRun)
        .filter(RuleRun.district_id == district.id)
        .order_by(RuleRun.created_at.desc())
        .first()
    )

    if latest_run is None or latest_run.status != RuleRunStatusEnum.success:
        rule_run = RuleRun(
            district_id=district.id,
            initiated_by="seed",
            status=RuleRunStatusEnum.pending,
            scope={"seed": True},
        )
        session.add(rule_run)
        session.commit()
        process_rule_run(str(rule_run.id))
        latest_run = rule_run

    violation_count = session.execute(
        select(func.count(RuleResult.id)).where(RuleResult.rule_run_id == latest_run.id)
    ).scalar_one()
    return int(violation_count)


def create_sample_exceptions(session: SessionLocal, district: District) -> None:
    existing = session.execute(
        select(ExceptionRecord).where(ExceptionRecord.district_id == district.id)
    ).first()
    if existing:
        return

    rule_results = (
        session.execute(
            select(RuleResult).where(
                RuleResult.district_id == district.id,
                RuleResult.status == "open",
            )
        )
        .scalars()
        .all()
    )

    for result in rule_results[:2]:
        exception = ExceptionRecord(
            district_id=district.id,
            rule_result_id=result.id,
            status=ExceptionStatusEnum.open,
            rationale="Investigating data discrepancy",
        )
        session.add(exception)
        session.flush()

        packet = EvidencePacket(
            district_id=district.id,
            name=f"Evidence for {exception.id}",
            description="Sample evidence packet",
            zip_url=None,
            sha256=None,
        )
        session.add(packet)
        session.flush()

        item = EvidenceItem(
            district_id=district.id,
            packet_id=packet.id,
            exception_id=exception.id,
            kind=EvidenceKindEnum.csv,
            title="Exported student record",
            uri="/samples/evidence/student.csv",
        )
        session.add(item)

    session.commit()


def bootstrap_readiness_scores(session: SessionLocal, district: District) -> None:
    existing = session.execute(
        select(ReadinessScore).where(ReadinessScore.district_id == district.id)
    ).first()
    if existing:
        return

    session.add_all(
        [
            ReadinessScore(district_id=district.id, school_id=None, category="District", score=72),
        ]
    )
    session.commit()


if __name__ == "__main__":
    main()
