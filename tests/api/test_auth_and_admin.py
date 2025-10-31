from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.app.db.base import Base
from apps.api.app import db as _db  # noqa: F401 ensures models imported
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
    response = client.post("/districts", json={"name": "Admin District", "timezone": "America/New_York"})
    assert response.status_code == 201
    return UUID(response.json()["id"])


def test_sso_login_and_me():
    district_id = _create_district()

    login_resp = client.post(
        "/auth/sso",
        headers={"X-District-ID": str(district_id)},
        json={
            "provider": "clever",
            "subject": "user-123",
            "email": "principal@example.edu",
            "display_name": "Principal",
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}", "X-District-ID": str(district_id)})
    assert me_resp.status_code == 200
    assert me_resp.json()["user"]["email"] == "principal@example.edu"


def test_admin_health_and_export():
    district_id = _create_district()

    login_resp = client.post(
        "/auth/sso",
        headers={"X-District-ID": str(district_id)},
        json={
            "provider": "clever",
            "subject": "admin-user",
            "email": "admin@example.edu",
            "display_name": "Admin",
        },
    )
    token = login_resp.json()["token"]

    sync_resp = client.post(
        "/connectors/powerschool/sync",
        headers={"X-District-ID": str(district_id), "Authorization": f"Bearer {token}"},
    )
    assert sync_resp.status_code == 202

    health_resp = client.get(
        "/admin/health",
        headers={"X-District-ID": str(district_id), "Authorization": f"Bearer {token}"},
    )
    assert health_resp.status_code == 200
    assert "connectors" in health_resp.json()

    export_resp = client.get(
        "/exports/exceptions.csv",
        headers={"X-District-ID": str(district_id), "Authorization": f"Bearer {token}"},
    )
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"].startswith("text/csv")
