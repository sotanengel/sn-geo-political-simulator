import numpy as np

from rl_pipeline.rewards.continental import compute_reward_continental
from rl_pipeline.rewards.island import compute_reward_island
from rl_pipeline.rewards.types import NationSnapshot, TerritorySnapshot


def test_island_reward_balanced() -> None:
    state = TerritorySnapshot(
        nations={
            "a": NationSnapshot("a", {"1", "2"}),
            "b": NationSnapshot("b", {"3", "4"}),
            "c": NationSnapshot("c", {"5", "6"}),
        },
        total_land_cells=6,
    )
    assert compute_reward_island(state, "a") == 0.0


def test_continental_reward() -> None:
    state = TerritorySnapshot(
        nations={"a": NationSnapshot("a", {"1", "2", "3"})},
        total_land_cells=10,
    )
    assert compute_reward_continental(state, "a") == 0.3
