import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_create_and_get_game(client: TestClient) -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 3, "max_turns": 5, "h3_resolution": 1}, "seed": 1},
    )
    assert create.status_code == 200
    game_id = create.json()["game_id"]

    get_resp = client.get(f"/api/v1/games/{game_id}")
    assert get_resp.status_code == 200
    assert len(get_resp.json()["nations"]) == 3


def test_submit_pass_action(client: TestClient) -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 2, "max_turns": 3, "h3_resolution": 1}, "seed": 2},
    )
    game_id = create.json()["game_id"]

    for nid in ("nation_0", "nation_1"):
        resp = client.post(
            f"/api/v1/games/{game_id}/actions",
            json={"nation_id": nid, "action_type": "PASS"},
        )
        assert resp.status_code == 200

    state = client.get(f"/api/v1/games/{game_id}/state")
    assert state.json()["turn"] >= 1


def test_history_persisted(client: TestClient) -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 2, "h3_resolution": 1}, "seed": 5},
    )
    game_id = create.json()["game_id"]
    history = client.get(f"/api/v1/games/{game_id}/history")
    assert history.status_code == 200
    events = [h["event"] for h in history.json()]
    assert "game_created" in events


def test_history_404_unknown_game(client: TestClient) -> None:
    resp = client.get(
        "/api/v1/games/00000000-0000-0000-0000-000000000099/history"
    )
    assert resp.status_code == 404


def test_config_validate(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/config/validate",
        json={"config": {"num_nations": 8, "h3_resolution": 3}},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


def test_state_includes_map_cells(client: TestClient) -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 2, "h3_resolution": 1}, "seed": 7},
    )
    game_id = create.json()["game_id"]
    state = client.get(f"/api/v1/games/{game_id}/state").json()
    assert len(state["cells"]) > 0
    assert "h3" in state["cells"][0]
    assert "terrain" in state["cells"][0]


def test_observation_includes_map_matrix(client: TestClient) -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 2, "h3_resolution": 1}, "seed": 8},
    )
    game_id = create.json()["game_id"]
    obs = client.get(f"/api/v1/games/{game_id}/observation/nation_0").json()
    assert len(obs["map"]) == 64
    assert len(obs["map"][0]) == 8
    assert len(obs["nation_resources"]) == 16


def test_observation_endpoint(client: TestClient) -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 2, "h3_resolution": 1}, "seed": 3},
    )
    game_id = create.json()["game_id"]
    obs = client.get(f"/api/v1/games/{game_id}/observation/nation_0")
    assert obs.status_code == 200
    assert "own_resources" in obs.json()


def test_delete_game(client: TestClient) -> None:
    create = client.post("/api/v1/games", json={})
    game_id = create.json()["game_id"]
    assert client.delete(f"/api/v1/games/{game_id}").status_code == 200
    assert client.get(f"/api/v1/games/{game_id}").status_code == 404
    assert client.get(f"/api/v1/games/{game_id}/history").status_code == 404
