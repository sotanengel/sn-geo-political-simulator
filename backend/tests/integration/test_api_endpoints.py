from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_game() -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 3, "max_turns": 5, "h3_resolution": 1}, "seed": 1},
    )
    assert create.status_code == 200
    game_id = create.json()["game_id"]

    get_resp = client.get(f"/api/v1/games/{game_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert len(data["nations"]) == 3


def test_submit_pass_action() -> None:
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

    state = client.get(f"/api/v1/games/{game_id}/state").json()
    assert state["turn"] >= 1


def test_config_validate() -> None:
    resp = client.post(
        "/api/v1/config/validate",
        json={"config": {"num_nations": 8, "h3_resolution": 3}},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


def test_observation_endpoint() -> None:
    create = client.post(
        "/api/v1/games",
        json={"config": {"num_nations": 2, "h3_resolution": 1}, "seed": 3},
    )
    game_id = create.json()["game_id"]
    obs = client.get(f"/api/v1/games/{game_id}/observation/nation_0")
    assert obs.status_code == 200
    assert "own_resources" in obs.json()


def test_delete_game() -> None:
    create = client.post("/api/v1/games", json={})
    game_id = create.json()["game_id"]
    assert client.delete(f"/api/v1/games/{game_id}").status_code == 200
    assert client.get(f"/api/v1/games/{game_id}").status_code == 404
