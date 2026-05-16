import numpy as np

from game.turn.processor import TurnProcessor
from game.types import ActionType, GameAction
from game.world.environment import GameConfig, WorldEnvironment


def test_full_turn_cycle() -> None:
    env = WorldEnvironment()
    state = env.reset(GameConfig(num_nations=4, h3_resolution=1, max_turns=3, seed=42))
    processor = TurnProcessor()
    rng = np.random.default_rng(42)

    processor.start_turn(state, rng)
    actions = [
        GameAction(nation_id=nid, action_type=ActionType.PASS)
        for nid in state.nations
    ]
    processor.resolve_actions(state, actions, rng)
    processor.end_turn(state)

    assert state.turn == 1
    assert not state.game_over


def test_game_ends_at_max_turns() -> None:
    env = WorldEnvironment()
    state = env.reset(GameConfig(num_nations=3, h3_resolution=1, max_turns=2, seed=1))
    processor = TurnProcessor(victory_condition="survival")
    rng = np.random.default_rng(1)

    for _ in range(2):
        processor.start_turn(state, rng)
        processor.resolve_actions(
            state,
            [GameAction(nation_id=nid, action_type=ActionType.PASS) for nid in state.nations],
            rng,
        )
        processor.end_turn(state)

    assert state.game_over
    assert len(state.winners) >= 1
