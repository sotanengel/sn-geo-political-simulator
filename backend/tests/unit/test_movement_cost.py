from game.types import TerrainType
from game.world.movement import movement_cost


def test_land_to_land() -> None:
    assert movement_cost(TerrainType.LAND, TerrainType.LAND) == 1


def test_land_to_shallow_sea() -> None:
    assert movement_cost(TerrainType.LAND, TerrainType.SHALLOW_SEA) == 3


def test_sea_to_land_amphibious() -> None:
    assert movement_cost(TerrainType.SHALLOW_SEA, TerrainType.LAND) == 4


def test_deep_sea_to_deep_sea() -> None:
    assert movement_cost(TerrainType.DEEP_SEA, TerrainType.DEEP_SEA) == 6
