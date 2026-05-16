#!/usr/bin/env python3
"""Ray RLlib multi-agent training entry point (requires ray[rllib])."""

from __future__ import annotations

import argparse
import json

from rl_pipeline.rllib.multi_agent import default_multi_agent_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-nations", type=int, default=8)
    parser.add_argument("--checkpoint-dir", default="/checkpoints/rllib")
    args = parser.parse_args()

    config = default_multi_agent_config(args.num_nations)

    try:
        import ray  # noqa: F401
        from ray.rllib.algorithms.ppo import PPOConfig  # noqa: F401

        print("Ray RLlib available — multi-agent training scaffold ready.")
        print(f"Policies: {config['policies']}")
        # Full training loop requires custom MultiAgentEnv registered with RLlib.
        # See docs/requirements-epic.md Phase 5 for integration roadmap.
    except ImportError:
        print("ray[rllib] not installed. Install with: pip install 'ray[rllib]'")
        print("Writing configuration scaffold only.")

    out_path = f"{args.checkpoint_dir}/multi_agent_config.json"
    import os

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    serializable = {
        "policies": config["policies"],
        "policy_groups": config["policy_groups"],
        "algorithm": config["algorithm"],
    }
    with open(out_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
