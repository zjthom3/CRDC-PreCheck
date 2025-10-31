from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.app.db.base import Base
import apps.api.app.db.models  # noqa: F401
from apps.api.app.db.session import get_session
from apps.api.app.main import create_app
from apps.worker.worker import tasks as worker_tasks

# Reuse the same in-memory SQLite DB across the test run
engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base.metadata.create_all(engine)

# Ensure worker tasks use the testing session maker
db_session_module = __import__("apps.api.app.db.session", fromlist=["SessionLocal", "engine"])
db_session_module.SessionLocal = TestingSessionLocal
db_session_module.engine = engine
worker_tasks.SessionLocal = TestingSessionLocal

app = create_app()


def _get_test_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = _get_test_session

# Patch Celery delay to run synchronously for tests
worker_tasks.sync_powerschool.delay = lambda district_id: worker_tasks.sync_powerschool(district_id)
worker_tasks.process_rule_run.delay = lambda rule_run_id: worker_tasks.process_rule_run(rule_run_id)

client = TestClient(app)


def _create_district() -> UUID:
    response = client.post("/districts", json={"name": "Test District", "timezone": "America/New_York"})
    assert response.status_code == 201
    body = response.json()
    return UUID(body["id"])


def test_rule_run_generates_results():
    district_id = _create_district()

    # Create school
    school_resp = client.post(
        "/schools",
        headers={"X-District-ID": str(district_id)},
        json={"name": "Test High", "level": "high"},
    )
    assert school_resp.status_code == 201
    school_id = UUID(school_resp.json()["id"])

    # Create student with invalid grade
    student_resp = client.post(
        "/students",
        headers={"X-District-ID": str(district_id)},
        json={
            "school_id": str(school_id),
            "sis_id": "S1",
            "first_name": "Jordan",
            "last_name": "Smith",
            "grade_level": 15,
            "ell_status": False,
            "idea_flag": False,
        },
    )
    assert student_resp.status_code == 201

    # Create rule version enforcing grade range
    rule_version_resp = client.post(
        "/rules/versions",
        headers={"X-District-ID": str(district_id)},
        json={
            "code": "GRADE-RANGE",
            "title": "Students must be between grades 0 and 12",
            "severity": "error",
            "applies_to": "Student",
            "dsl": {"type": "grade_range", "min": 0, "max": 12},
        },
    )
    assert rule_version_resp.status_code == 201

    # Trigger rule run
    run_resp = client.post(
        "/rules/runs",
        headers={"X-District-ID": str(district_id)},
        json={},
    )
    assert run_resp.status_code == 202

    results_resp = client.get(
        "/rules/results",
        headers={"X-District-ID": str(district_id)},
    )
    assert results_resp.status_code == 200
    results = results_resp.json()
    assert len(results) == 1
    assert results[0]["message"].startswith("Grade level")

    exception_resp = client.post(
        "/exceptions",
        headers={"X-District-ID": str(district_id)},
        json={"rule_result_id": results[0]["id"], "rationale": "Review needed"},
    )
    assert exception_resp.status_code == 201
    exception_id = exception_resp.json()["id"]

    update_resp = client.patch(
        f"/exceptions/{exception_id}",
        headers={"X-District-ID": str(district_id)},
        json={"status": "in_review"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "in_review"

    memo_resp = client.post(
        f"/exceptions/{exception_id}/memo",
        headers={"X-District-ID": str(district_id)},
        json={"title": "Initial review", "body_md": "Investigating."},
    )
    assert memo_resp.status_code == 201

    packet_resp = client.post(
        "/evidence/packets",
        headers={"X-District-ID": str(district_id)},
        json={
            "name": "Exception packet",
            "description": "Auto-generated evidence",
            "exception_ids": [exception_id],
        },
    )
    assert packet_resp.status_code == 201

    readiness_resp = client.get(
        "/readiness",
        headers={"X-District-ID": str(district_id)},
    )
    assert readiness_resp.status_code == 200
    readiness = readiness_resp.json()
    assert "items" in readiness
