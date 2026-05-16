from __future__ import annotations

import os
from typing import Any

import httpx
import numpy as np
from gymnasium import Env

from rl_pipeline.env.spaces import build_action_space, build_observation_space
from rl_pipeline.rewards.continental import compute_reward_continental
from rl_pipeline.rewards.island import compute_reward_island
from rl_pipeline.rewards.types import NationSnapshot, TerritorySnapshot


class GeopoliticalEnv(Env):
    """Gymnasium environment wrapping the Game Engine REST API."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        nation_id: str = "nation_0",
        agent_type: str = "continental",
        game_engine_url: str | None = None,
        mock: bool = False,
    ) -> None:
        super().__init__()
        self.nation_id = nation_id
        self.agent_type = agent_type
        self.game_engine_url = game_engine_url or os.getenv(
            "GAME_ENGINE_URL", "http://localhost:8000"
        )
        self.mock = mock
        self.observation_space = build_observation_space()
        self.action_space = build_action_space()
        self._game_id: str | None = None
        self._turn = 0
        self._client = httpx.Client(timeout=30.0)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        if self.mock:
            self._game_id = "mock-game"
            self._turn = 0
            obs = self._mock_observation()
            return obs, {}

        resp = self._client.post(
            f"{self.game_engine_url}/api/v1/games",
            json={
                "config": {"num_nations": 6, "max_turns": 20, "h3_resolution": 1},
                "seed": seed,
            },
        )
        resp.raise_for_status()
        self._game_id = resp.json()["game_id"]
        obs = self._fetch_observation()
        return obs, {}

    def step(self, action: np.ndarray):
        if self.mock:
            self._turn += 1
            obs = self._mock_observation()
            reward = 0.1 if self.agent_type == "continental" else -0.05
            terminated = self._turn >= 5
            return obs, reward, terminated, False, {}

        assert self._game_id
        self._client.post(
            f"{self.game_engine_url}/api/v1/games/{self._game_id}/rl-action/{self.nation_id}",
            json={
                "action": {
                    "nation_id": self.nation_id,
                    "action_type": "PASS",
                }
            },
        )
        state = self._client.get(
            f"{self.game_engine_url}/api/v1/games/{self._game_id}/state"
        ).json()
        obs = self._fetch_observation()
        reward = self._compute_reward(state)
        terminated = state.get("game_over", False)
        return obs, reward, terminated, False, {}

    def close(self) -> None:
        self._client.close()

    def _fetch_observation(self) -> dict[str, np.ndarray]:
        assert self._game_id
        data = self._client.get(
            f"{self.game_engine_url}/api/v1/games/{self._game_id}/observation/{self.nation_id}"
        ).json()
        return self._vectorize_observation(data)

    def _vectorize_observation(self, data: dict[str, Any]) -> dict[str, np.ndarray]:
        resources = data.get("own_resources", {})
        own_res = np.array(
            [resources.get(k, 0) for k in ("FOOD", "FUEL", "ORE", "TECH", "GOLD")],
            dtype=np.float32,
        )
        category = 0 if data.get("own_category") == "ISLAND" else 1
        map_data = np.array(data.get("map", []), dtype=np.float32)
        if map_data.shape != (64, 8):
            map_data = np.zeros((64, 8), dtype=np.float32)
        nation_res = np.array(data.get("nation_resources", []), dtype=np.float32)
        if nation_res.shape != (16, 5):
            nation_res = np.zeros((16, 5), dtype=np.float32)
        return {
            "map": map_data,
            "own_resources": own_res,
            "nation_resources": nation_res,
            "own_category": np.int64(category),
            "turn": np.array([data.get("turn", 0)], dtype=np.int32),
        }

    def _mock_observation(self) -> dict[str, np.ndarray]:
        return {
            "map": np.zeros((64, 8), dtype=np.float32),
            "own_resources": np.array([100, 100, 50, 10, 10], dtype=np.float32),
            "nation_resources": np.zeros((16, 5), dtype=np.float32),
            "own_category": np.int64(1 if self.agent_type == "continental" else 0),
            "turn": np.array([self._turn], dtype=np.int32),
        }

    def _compute_reward(self, state: dict[str, Any]) -> float:
        nations = {
            n["id"]: NationSnapshot(
                id=n["id"],
                territory=set(range(n.get("territory_size", 0))),
                is_extinct=n.get("is_extinct", False),
            )
            for n in state.get("nations", [])
        }
        snap = TerritorySnapshot(nations=nations, total_land_cells=100)
        if self.agent_type == "island":
            return compute_reward_island(snap, self.nation_id)
        return compute_reward_continental(snap, self.nation_id)
