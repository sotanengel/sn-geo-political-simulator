from fastapi.testclient import TestClient

from app.main import app


def test_api_health_with_services_env() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
