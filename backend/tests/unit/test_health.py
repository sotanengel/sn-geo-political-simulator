from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_config_presets() -> None:
    response = client.get("/api/v1/config/presets")
    assert response.status_code == 200
    assert "largest_territory" in response.json()["victory_conditions"]
