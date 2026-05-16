from __future__ import annotations

from typing import Any

import h3
import numpy as np

from game.types import TerrainType, WorldState

NUM_MAP_CELLS = 64
MAP_FEATURES = 8
MAX_NATIONS = 16
RESOURCE_KEYS = ("FOOD", "FUEL", "ORE", "TECH", "GOLD")


def build_map_cells(state: WorldState) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for h3_cell, terrain in sorted(state.cell_terrain.items()):
        cells.append(
            {
                "h3": h3_cell,
                "owner_id": state.cell_owner.get(h3_cell),
                "terrain": terrain.value,
            }
        )
    return cells


def build_observation_payload(
    state: WorldState,
    nation_id: str,
    *,
    submitted: set[str] | None = None,
) -> dict[str, Any]:
    nation = state.nations[nation_id]
    nation_ids = sorted(state.nations.keys())
    index_by_id = {nid: i for i, nid in enumerate(nation_ids)}

    map_matrix = np.zeros((NUM_MAP_CELLS, MAP_FEATURES), dtype=np.float32)
    ordered_cells = _observation_cell_order(state, nation_id)
    for row, cell in enumerate(ordered_cells[:NUM_MAP_CELLS]):
        map_matrix[row] = _cell_features(cell, state, nation_id, index_by_id)

    nation_resources = np.zeros((MAX_NATIONS, len(RESOURCE_KEYS)), dtype=np.float32)
    for nid in nation_ids[:MAX_NATIONS]:
        idx = index_by_id[nid]
        res = state.nations[nid].resources.to_dict()
        for col, key in enumerate(RESOURCE_KEYS):
            nation_resources[idx, col] = float(res.get(key, 0))

    return {
        "own_resources": nation.resources.to_dict(),
        "own_category": nation.category.value,
        "turn": state.turn,
        "territory_size": len(nation.territory),
        "num_nations": len(state.nations),
        "map": map_matrix.tolist(),
        "nation_resources": nation_resources.tolist(),
        "has_submitted": nation_id in (submitted or set()),
    }


def _observation_cell_order(state: WorldState, nation_id: str) -> list[str]:
    own = sorted(state.nations[nation_id].territory)
    neighbors: set[str] = set()
    for cell in own:
        for nbr in h3.grid_disk(cell, 1):
            if nbr not in own and nbr in state.cell_terrain:
                neighbors.add(nbr)
    rest = sorted(c for c in state.cell_terrain if c not in own and c not in neighbors)
    return own + sorted(neighbors) + rest


def _cell_features(
    cell: str,
    state: WorldState,
    nation_id: str,
    index_by_id: dict[str, int],
) -> np.ndarray:
    terrain = state.cell_terrain.get(cell, TerrainType.DEEP_SEA)
    owner = state.cell_owner.get(cell)
    lat, lng = h3.cell_to_latlng(cell)
    terrain_vec = [
        1.0 if terrain == TerrainType.LAND else 0.0,
        1.0 if terrain == TerrainType.SHALLOW_SEA else 0.0,
        1.0 if terrain == TerrainType.DEEP_SEA else 0.0,
    ]
    owner_idx = index_by_id.get(owner, -1) if owner else -1
    return np.array(
        [
            *terrain_vec,
            1.0 if owner == nation_id else 0.0,
            (owner_idx + 1) / max(len(index_by_id), 1) if owner_idx >= 0 else 0.0,
            1.0 if cell in state.land_cells else 0.0,
            (lat + 90.0) / 180.0,
            (lng + 180.0) / 360.0,
        ],
        dtype=np.float32,
    )
