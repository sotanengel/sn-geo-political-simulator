import time

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_api_turn_timeout(client: TestClient) -> None:
    create = client.post(
        "/api/v1/games",
        json={
            "config": {
                "num_nations": 2,
                "max_turns": 5,
                "h3_resolution": 1,
                "turn_timeout_seconds": 1,
            },
            "seed": 99,
        },
    )
    assert create.status_code == 200
    game_id = create.json()["game_id"]

    resp = client.post(
        f"/api/v1/games/{game_id}/actions",
        json={"nation_id": "nation_0", "action_type": "PASS"},
    )
    assert resp.status_code == 200

    time.sleep(1.5)

    state = client.get(f"/api/v1/games/{game_id}/state")
    assert state.status_code == 200
    assert state.json()["turn"] >= 1
