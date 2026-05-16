from rl_pipeline.env.spaces import build_action_space


def test_action_space_contains_sample() -> None:
    space = build_action_space()
    action = space.sample()
    assert space.contains(action)
