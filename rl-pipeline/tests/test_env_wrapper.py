import numpy as np

from rl_pipeline.env.geopolitical_env import GeopoliticalEnv


def test_mock_env_reset_step() -> None:
    env = GeopoliticalEnv(mock=True, agent_type="continental")
    obs, _ = env.reset(seed=42)
    assert "own_resources" in obs
    action = env.action_space.sample()
    obs2, reward, terminated, truncated, info = env.step(action)
    assert isinstance(reward, float)
    assert obs2["map"].shape == (64, 8)
    env.close()


def test_mock_island_agent() -> None:
    env = GeopoliticalEnv(mock=True, agent_type="island")
    env.reset()
    _, reward, _, _, _ = env.step(env.action_space.sample())
    assert isinstance(reward, float)
