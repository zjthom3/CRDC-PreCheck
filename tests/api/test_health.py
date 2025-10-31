from fastapi.testclient import TestClient

from apps.api.app.main import create_app


def test_health_live_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
