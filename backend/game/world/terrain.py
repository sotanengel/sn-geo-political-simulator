from __future__ import annotations

import h3
import numpy as np

from game.types import H3Cell, TerrainType


def classify_terrain_from_latlng(lat: float, lng: float) -> TerrainType:
    """Synthetic terrain from coordinates (no external dataset required)."""
    # Simplified land mask: major continental regions
    land_score = (
        np.exp(-((lat - 40) ** 2 + (lng - -100) ** 2) / 800)
        + np.exp(-((lat - 50) ** 2 + (lng - 10) ** 2) / 600)
        + np.exp(-((lat - 35) ** 2 + (lng - 100) ** 2) / 700)
        + np.exp(-((lat - -25) ** 2 + (lng - 135) ** 2) / 900)
        + np.exp(-((lat - -10) ** 2 + (lng - -55) ** 2) / 500)
    )
    if land_score > 0.35:
        return TerrainType.LAND
    if land_score > 0.08:
        return TerrainType.SHALLOW_SEA
    return TerrainType.DEEP_SEA


def generate_terrain_map(cells: list[H3Cell], rng: np.random.Generator) -> dict[H3Cell, TerrainType]:
    terrain: dict[H3Cell, TerrainType] = {}
    for cell in cells:
        lat, lng = h3.cell_to_latlng(cell)
        base = classify_terrain_from_latlng(lat, lng)
        # Small noise for variety
        if base == TerrainType.LAND and rng.random() < 0.02:
            base = TerrainType.SHALLOW_SEA
        terrain[cell] = base
    return terrain


def get_land_cells(terrain: dict[H3Cell, TerrainType]) -> set[H3Cell]:
    return {c for c, t in terrain.items() if t == TerrainType.LAND}
