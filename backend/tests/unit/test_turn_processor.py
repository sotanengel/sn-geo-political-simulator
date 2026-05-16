import numpy as np

from game.turn.processor import TurnProcessor
from game.types import ActionType, GameAction, Nation, NationCategory, ResourceStock, TerrainType, WorldState
from game.world.environment import GameConfig, WorldEnvironment


def test_move_consumes_fuel() -> None:
    env = WorldEnvironment()
    state = env.reset(GameConfig(num_nations=2, h3_resolution=1, seed=7))
    processor = TurnProcessor()
    rng = np.random.default_rng(7)

    n0 = state.nations["nation_0"]
    from game.world.h3_grid import get_neighbors

    source = next(iter(n0.territory))
    neighbors = [c for c in get_neighbors(source, 1) if c in n0.territory and c != source]
    if not neighbors:
        neighbors = [c for c in get_neighbors(source, 1) if c in state.cell_terrain]
    if not neighbors:
        return
    target = neighbors[0]
    n0.military_units[source] = 5
    n0.resources.fuel = 100

    processor.resolve_actions(
        state,
        [
            GameAction(
                nation_id="nation_0",
                action_type=ActionType.MOVE,
                source_cell=source,
                target_cell=target,
                units=2,
            )
        ],
        rng,
    )
    assert n0.resources.fuel < 100


def test_pass_actions_all_nations() -> None:
    env = WorldEnvironment()
    state = env.reset(GameConfig(num_nations=3, h3_resolution=1, seed=3))
    processor = TurnProcessor()
    rng = np.random.default_rng(3)
    processor.start_turn(state, rng)
    processor.resolve_actions(
        state,
        [GameAction(nation_id=nid, action_type=ActionType.PASS) for nid in state.nations],
        rng,
    )
    processor.end_turn(state)
    assert state.turn == 1
