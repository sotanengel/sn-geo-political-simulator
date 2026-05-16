from __future__ import annotations

from typing import Any


def build_policy_mapping_fn(nation_ids: list[str], categories: dict[str, str]):
    """
    Parameter sharing: nations with the same category share a policy.
    categories values: 'ISLAND' | 'CONTINENTAL'
    """

    def policy_mapping_fn(agent_id: str, *args: Any, **kwargs: Any) -> str:
        category = categories.get(agent_id, "CONTINENTAL")
        return f"policy_{category.lower()}"

    policies = {
        "policy_island": [],
        "policy_continental": [],
    }
    for nid in nation_ids:
        cat = categories.get(nid, "CONTINENTAL")
        key = f"policy_{cat.lower()}"
        policies[key].append(nid)

    return policy_mapping_fn, {k: v for k, v in policies.items() if v}


def default_multi_agent_config(num_nations: int = 8) -> dict[str, Any]:
    """RLlib MultiAgentEnv configuration scaffold."""
    nation_ids = [f"nation_{i}" for i in range(num_nations)]
    categories = {nid: "ISLAND" if i % 4 == 0 else "CONTINENTAL" for i, nid in enumerate(nation_ids)}
    policy_mapping_fn, policy_groups = build_policy_mapping_fn(nation_ids, categories)
    return {
        "policies": list(policy_groups.keys()),
        "policy_mapping_fn": policy_mapping_fn,
        "policy_groups": policy_groups,
        "algorithm": "PPO",
        "framework": "rllib",
    }
