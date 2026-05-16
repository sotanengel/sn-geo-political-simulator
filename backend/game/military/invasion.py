from __future__ import annotations

import math

import numpy as np

from game.types import InvasionResult


def tech_multiplier(tech_investment: int, scale_factor: float = 0.1) -> float:
    return 1.0 + math.log(1 + tech_investment) * scale_factor


def resolve_invasion(
    attack_force: int,
    defend_force: int,
    attacker_tech: float,
    defender_tech: float,
    rng: np.random.Generator,
    attrition_rate: float = 0.3,
) -> tuple[InvasionResult, int, int]:
    """
    Returns result and remaining attacker/defender units after battle.
    """
    eff_attack = attack_force * attacker_tech * rng.uniform(0.8, 1.2)
    eff_defend = defend_force * defender_tech * rng.uniform(0.8, 1.2)

    atk_loss = max(1, int(attack_force * attrition_rate))
    def_loss = max(1, int(defend_force * attrition_rate))

    if eff_attack > eff_defend:
        return InvasionResult.SUCCESS, max(0, attack_force - atk_loss), 0
    return InvasionResult.FAILURE, max(0, attack_force - atk_loss), max(0, defend_force - def_loss)
