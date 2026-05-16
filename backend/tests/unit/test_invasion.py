import numpy as np

from game.military.invasion import resolve_invasion, tech_multiplier
from game.types import InvasionResult


def test_tech_multiplier_increases_with_investment() -> None:
    assert tech_multiplier(0) == 1.0
    assert tech_multiplier(10) > 1.0


def test_resolve_invasion_returns_result() -> None:
    rng = np.random.default_rng(42)
    for _ in range(20):
        result, atk, def_ = resolve_invasion(100, 10, 1.0, 1.0, rng)
        assert result in (InvasionResult.SUCCESS, InvasionResult.FAILURE)
        assert atk >= 0
        assert def_ >= 0


def test_strong_attacker_usually_wins() -> None:
    rng = np.random.default_rng(0)
    wins = 0
    for _ in range(50):
        result, _, _ = resolve_invasion(1000, 1, 2.0, 1.0, rng)
        if result == InvasionResult.SUCCESS:
            wins += 1
    assert wins > 40
