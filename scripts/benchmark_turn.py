#!/usr/bin/env python3
"""Benchmark turn resolution for performance targets (<500ms at res 2)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import numpy as np

from game.turn.processor import TurnProcessor
from game.types import ActionType, GameAction
from game.world.environment import GameConfig, WorldEnvironment


def main() -> None:
    env = WorldEnvironment()
    state = env.reset(GameConfig(num_nations=10, h3_resolution=2, seed=42))
    processor = TurnProcessor()
    rng = np.random.default_rng(42)
    actions = [
        GameAction(nation_id=nid, action_type=ActionType.PASS)
        for nid in state.nations
    ]

    start = time.perf_counter()
    processor.start_turn(state, rng)
    processor.resolve_actions(state, actions, rng)
    processor.end_turn(state)
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"Turn resolution: {elapsed_ms:.1f}ms (10 nations, res 2)")
    if elapsed_ms > 500:
        print("WARNING: exceeds 500ms target")
        sys.exit(1)
    print("OK: within 500ms target")


if __name__ == "__main__":
    main()
