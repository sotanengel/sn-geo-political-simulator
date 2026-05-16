from __future__ import annotations

import numpy as np
from gymnasium import spaces

# Compact spaces for SB3 at resolution 1 scale
NUM_CELLS = 64
MAP_FEATURES = 8
MAX_RESOURCE = 1000
MAX_NATIONS = 16
MAX_UNITS = 100
MAX_RESOURCE_TRADE = 500
ACTION_TYPE = 5  # PASS, MOVE, INVADE, TRADE, GIFT


def build_observation_space() -> spaces.Dict:
    return spaces.Dict(
        {
            "map": spaces.Box(
                low=0,
                high=1,
                shape=(NUM_CELLS, MAP_FEATURES),
                dtype=np.float32,
            ),
            "own_resources": spaces.Box(
                low=0,
                high=MAX_RESOURCE,
                shape=(5,),
                dtype=np.float32,
            ),
            "nation_resources": spaces.Box(
                low=0,
                high=MAX_RESOURCE,
                shape=(MAX_NATIONS, 5),
                dtype=np.float32,
            ),
            "own_category": spaces.Discrete(2),
            "turn": spaces.Box(low=0, high=500, shape=(1,), dtype=np.int32),
        }
    )


def build_action_space() -> spaces.MultiDiscrete:
    return spaces.MultiDiscrete(
        [
            NUM_CELLS,
            NUM_CELLS,
            MAX_UNITS,
            ACTION_TYPE,
            MAX_NATIONS,
            5,
            MAX_RESOURCE_TRADE,
            5,
            MAX_RESOURCE_TRADE,
        ]
    )
