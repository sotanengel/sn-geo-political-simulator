from __future__ import annotations

from rl_pipeline.rewards.types import TerritorySnapshot


def compute_reward_continental(state: TerritorySnapshot, nation_id: str) -> float:
    own_area = len(state.nations[nation_id].territory)
    total_land = state.total_land_cells or 1
    return own_area / total_land
