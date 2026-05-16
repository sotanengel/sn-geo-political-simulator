from __future__ import annotations

import numpy as np

from game.types import Nation, WorldState


def score_territory(nation: Nation) -> int:
    return len(nation.territory)


def evaluate_victory(
    state: WorldState,
    condition: str,
    target_cells: int = 500,
) -> list[str]:
    active = [n for n in state.nations.values() if not n.is_extinct]

    if condition == "largest_territory":
        max_score = max(score_territory(n) for n in active)
        return [n.id for n in active if score_territory(n) == max_score]

    if condition == "smallest_territory":
        min_score = min(score_territory(n) for n in active)
        return [n.id for n in active if score_territory(n) == min_score]

    if condition == "balance_enforcer":
        areas = [score_territory(n) for n in active]
        std = float(np.std(areas)) if len(areas) > 1 else 0.0
        # Nation whose removal would have been closest to balance — simplified:
        mean = sum(areas) / len(areas)
        return [min(active, key=lambda n: abs(score_territory(n) - mean)).id]

    if condition == "target_score":
        return [n.id for n in active if score_territory(n) >= target_cells]

    if condition == "survival":
        return [n.id for n in active if score_territory(n) >= 1]

    return [n.id for n in active]
