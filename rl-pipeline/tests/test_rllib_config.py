from rl_pipeline.rllib.multi_agent import build_policy_mapping_fn, default_multi_agent_config


def test_policy_mapping_shares_by_category() -> None:
    nations = ["nation_0", "nation_1", "nation_2"]
    categories = {
        "nation_0": "ISLAND",
        "nation_1": "CONTINENTAL",
        "nation_2": "CONTINENTAL",
    }
    mapping_fn, groups = build_policy_mapping_fn(nations, categories)
    assert mapping_fn("nation_0") == "policy_island"
    assert mapping_fn("nation_1") == "policy_continental"
    assert "nation_1" in groups["policy_continental"]
    assert "nation_0" in groups["policy_island"]


def test_default_config() -> None:
    cfg = default_multi_agent_config(4)
    assert "policy_island" in cfg["policies"]
    assert cfg["algorithm"] == "PPO"
