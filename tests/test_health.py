from fastapi.testclient import TestClient

from cockroach_continuity.main import app


def test_liveness_is_independent_of_database() -> None:
    client = TestClient(app)
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_exposes_database_state() -> None:
    client = TestClient(app)
    response = client.get("/health/ready")

    assert response.status_code in {200, 503}
    body = response.json()
    assert "database" in body
    assert body["status"] in {"ready", "degraded"}
