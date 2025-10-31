import csv
import io
import json
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.app.db.base import Base
import apps.api.app.db.models  # noqa: F401
from apps.api.app.db.session import get_session
from apps.api.app.main import create_app
from apps.worker.worker import tasks as worker_tasks

engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base.metadata.create_all(engine)

db_session_module = __import__("apps.api.app.db.session", fromlist=["SessionLocal", "engine"])
db_session_module.SessionLocal = TestingSessionLocal
db_session_module.engine = engine
worker_tasks.SessionLocal = TestingSessionLocal
worker_tasks.process_rule_run.delay = lambda rule_run_id: worker_tasks.process_rule_run(rule_run_id)
worker_tasks.sync_powerschool.delay = lambda district_id: worker_tasks.sync_powerschool(district_id)

app = create_app()


def _get_test_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = _get_test_session
client = TestClient(app)


def _create_district() -> UUID:
    response = client.post("/districts", json={"name": "Import District", "timezone": "America/Chicago"})
    assert response.status_code == 201
    return UUID(response.json()["id"])


def _create_school(district_id: UUID, name: str) -> UUID:
    response = client.post(
        "/schools",
        headers={"X-District-ID": str(district_id)},
        json={"name": name, "level": "other"},
    )
    assert response.status_code == 201
    return UUID(response.json()["id"])


def test_csv_import_creates_students():
    district_id = _create_district()
    _create_school(district_id, "Central Elementary")

    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    writer.writerow([
        "Student ID",
        "First Name",
        "Last Name",
        "Grade",
        "School",
        "Enrollment Status",
        "ELL",
        "IDEA",
    ])
    writer.writerow(["CSV1", "Taylor", "Brooks", "5", "Central Elementary", "active", "true", "false"])
    writer.writerow(["CSV2", "Chris", "Jordan", "7", "Central Elementary", "active", "false", "1"])

    mapping = {
        "sis_id": "Student ID",
        "first_name": "First Name",
        "last_name": "Last Name",
        "grade_level": "Grade",
        "school_name": "School",
        "enrollment_status": "Enrollment Status",
        "ell_status": "ELL",
        "idea_flag": "IDEA",
    }

    response = client.post(
        "/import/students/csv",
        headers={"X-District-ID": str(district_id)},
        data={"mapping": json.dumps(mapping)},
        files={"file": ("students.csv", csv_data.getvalue(), "text/csv")},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["rows_processed"] == 2
    assert body["students_created"] == 2
    assert body["students_updated"] == 0
    assert body["errors"] == []

    students = client.get(
        "/students",
        headers={"X-District-ID": str(district_id)},
    ).json()
    assert len(students) == 2
    assert {student["sis_id"] for student in students} == {"CSV1", "CSV2"}


def test_powerschool_sync_endpoint():
    district_id = _create_district()

    response = client.post(
        "/connectors/powerschool/sync",
        headers={"X-District-ID": str(district_id)},
    )
    assert response.status_code == 202
    assert response.json()["status"] == "queued"

    students = client.get(
        "/students",
        headers={"X-District-ID": str(district_id)},
    ).json()
    assert any(student["sis_id"] == "PS1001" for student in students)
