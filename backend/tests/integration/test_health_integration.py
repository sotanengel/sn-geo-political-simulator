from fastapi.testclient import TestClient

from app.main import app


def test_api_health_with_services_env() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
