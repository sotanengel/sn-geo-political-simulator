from __future__ import annotations

from game.types import TerrainType


def movement_cost(from_terrain: TerrainType, to_terrain: TerrainType) -> int:
    """Movement cost per spec section 5.3."""
    if from_terrain == TerrainType.LAND and to_terrain == TerrainType.LAND:
        return 1
    if from_terrain == TerrainType.LAND and to_terrain == TerrainType.SHALLOW_SEA:
        return 3
    if from_terrain == TerrainType.SHALLOW_SEA and to_terrain == TerrainType.SHALLOW_SEA:
        return 3
    if from_terrain == TerrainType.LAND and to_terrain == TerrainType.DEEP_SEA:
        return 6
    if from_terrain == TerrainType.DEEP_SEA and to_terrain == TerrainType.DEEP_SEA:
        return 6
    if from_terrain in (TerrainType.SHALLOW_SEA, TerrainType.DEEP_SEA) and to_terrain == TerrainType.LAND:
        return 4
    if from_terrain == TerrainType.SHALLOW_SEA and to_terrain == TerrainType.DEEP_SEA:
        return 6
    if from_terrain == TerrainType.DEEP_SEA and to_terrain == TerrainType.SHALLOW_SEA:
        return 6
    return 6
