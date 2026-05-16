import numpy as np

from game.types import Nation, NationCategory, WorldState
from game.victory.presets import score_territory


def compute_reward_island(state: WorldState, nation_id: str) -> float:
    areas = [
        len(n.territory)
        for n in state.nations.values()
        if n.id != nation_id and not n.is_extinct
    ]
    if len(areas) < 2:
        return 0.0
    return -float(np.std(areas))


def compute_reward_continental(state: WorldState, nation_id: str) -> float:
    own_area = len(state.nations[nation_id].territory)
    total_land = state.total_land_cells or 1
    return own_area / total_land


def test_island_reward_balanced() -> None:
    state = WorldState(
        nations={
            "a": Nation(id="a", name="A", category=NationCategory.ISLAND, territory={"1", "2"}),
            "b": Nation(id="b", name="B", category=NationCategory.CONTINENTAL, territory={"3", "4"}),
            "c": Nation(id="c", name="C", category=NationCategory.CONTINENTAL, territory={"5", "6"}),
        },
        land_cells={"1", "2", "3", "4", "5", "6"},
    )
    reward = compute_reward_island(state, "a")
    assert reward == 0.0


def test_continental_reward_normalized() -> None:
    state = WorldState(
        nations={
            "a": Nation(id="a", name="A", category=NationCategory.CONTINENTAL, territory={"1", "2"}),
        },
        land_cells={"1", "2", "3", "4"},
    )
    assert compute_reward_continental(state, "a") == 0.5
