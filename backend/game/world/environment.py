from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from game.nation.borders import generate_initial_borders
from game.nation.category import determine_nation_category
from game.economy.resources import generate_cell_yields, random_initial_resources
from game.types import ControllerType, Nation, NationCategory, WorldState
from game.world.h3_grid import get_all_cells
from game.world.terrain import generate_terrain_map, get_land_cells


@dataclass
class GameConfig:
    num_nations: int = 8
    max_turns: int = 50
    h3_resolution: int = 2
    seed: int | None = None
    initial_resource_min: int = 100
    initial_resource_max: int = 300
    max_trades_per_turn: int = 5
    victory_condition: str = "largest_territory"
    target_cells: int = 500
    default_controller: ControllerType = ControllerType.RL_AGENT


class WorldEnvironment:
    def reset(self, config: GameConfig | None = None) -> WorldState:
        cfg = config or GameConfig()
        rng = np.random.default_rng(cfg.seed)

        cells = get_all_cells(cfg.h3_resolution)
        terrain = generate_terrain_map(cells, rng)
        land_cells = get_land_cells(terrain)
        yields = generate_cell_yields(terrain, rng)

        territories, capitals = generate_initial_borders(
            land_cells, cfg.num_nations, rng
        )

        nations: dict[str, Nation] = {}
        for nid, territory in territories.items():
            nations[nid] = Nation(
                id=nid,
                name=f"Nation-{nid}",
                category=NationCategory.CONTINENTAL,
                territory=set(territory),
                capital=capitals[nid],
                resources=random_initial_resources(
                    rng, cfg.initial_resource_min, cfg.initial_resource_max
                ),
                controller=cfg.default_controller,
                military_units={capitals[nid]: rng.integers(5, 15)},
            )

        all_terr = {nid: n.territory for nid, n in nations.items()}
        for nid, nation in nations.items():
            nation.category = determine_nation_category(
                nation.territory, all_terr, nid, terrain, land_cells
            )

        cell_owner: dict[str, str] = {}
        for nid, nation in nations.items():
            for cell in nation.territory:
                cell_owner[cell] = nid

        return WorldState(
            turn=0,
            max_turns=cfg.max_turns,
            nations=nations,
            cell_terrain=terrain,
            cell_yields=yields,
            cell_owner=cell_owner,
            land_cells=land_cells,
            resolution=cfg.h3_resolution,
            seed=cfg.seed,
        )
