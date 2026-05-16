from rl_pipeline.env.spaces import build_observation_space


def test_observation_space_shapes() -> None:
    space = build_observation_space()
    sample = space.sample()
    assert sample["map"].shape == (64, 8)
    assert sample["own_resources"].shape == (5,)
    assert sample["nation_resources"].shape == (16, 5)
    assert sample["turn"].shape == (1,)
