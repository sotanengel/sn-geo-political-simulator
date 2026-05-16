#!/usr/bin/env python3
"""Train RL agents with Stable-Baselines3."""

from __future__ import annotations

import argparse
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from rl_pipeline.env.geopolitical_env import GeopoliticalEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Train geopolitical RL agent")
    parser.add_argument("--agent-type", choices=["island", "continental"], default="continental")
    parser.add_argument("--num-nations", type=int, default=12)
    parser.add_argument("--resolution", type=int, default=2)
    parser.add_argument("--victory", default="largest_territory")
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("/checkpoints"))
    parser.add_argument("--timesteps", type=int, default=10_000)
    parser.add_argument("--mock", action="store_true", help="Train on mock env (no API)")
    args = parser.parse_args()

    env = GeopoliticalEnv(agent_type=args.agent_type, mock=args.mock)
    check_env(env, warn=True)

    model = PPO("MultiInputPolicy", env, verbose=1)
    model.learn(total_timesteps=args.timesteps)

    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    out = args.checkpoint_dir / f"{args.agent_type}_ppo"
    model.save(str(out))
    print(f"Saved checkpoint to {out}")


if __name__ == "__main__":
    main()
