from game.world.environment import GameConfig, WorldEnvironment


def test_environment_reset() -> None:
    env = WorldEnvironment()
    state = env.reset(GameConfig(num_nations=6, h3_resolution=1, seed=99))

    assert len(state.nations) == 6
    assert state.turn == 0
    assert len(state.land_cells) > 0
    assert all(len(n.territory) > 0 for n in state.nations.values())
    assert len(state.cell_owner) > 0


def test_deterministic_reset_with_seed() -> None:
    env = WorldEnvironment()
    cfg = GameConfig(num_nations=4, h3_resolution=1, seed=123)
    s1 = env.reset(cfg)
    s2 = env.reset(cfg)
    assert set(s1.nations.keys()) == set(s2.nations.keys())
    assert s1.nations["nation_0"].resources.food == s2.nations["nation_0"].resources.food
