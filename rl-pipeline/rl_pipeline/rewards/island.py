from __future__ import annotations

import numpy as np

from rl_pipeline.rewards.types import TerritorySnapshot


def compute_reward_island(state: TerritorySnapshot, nation_id: str) -> float:
    areas = [
        len(n.territory)
        for n in state.nations.values()
        if n.id != nation_id and not n.is_extinct
    ]
    if len(areas) < 2:
        return 0.0
    return -float(np.std(areas))
