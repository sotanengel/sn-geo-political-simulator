import pytest

from game.world.h3_grid import are_adjacent, cell_distance, get_all_cells, get_neighbors
from game.world.terrain import classify_terrain_from_latlng, generate_terrain_map, get_land_cells
from game.types import TerrainType
import numpy as np


def test_get_all_cells_resolution_2() -> None:
    cells = get_all_cells(2)
    assert len(cells) > 5000
    assert len(set(cells)) == len(cells)


def test_neighbors_are_adjacent() -> None:
    cells = get_all_cells(2)
    cell = cells[100]
    neighbors = get_neighbors(cell, 1)
    assert len(neighbors) <= 6
    for n in neighbors:
        assert are_adjacent(cell, n)


def test_cell_distance_zero() -> None:
    cells = get_all_cells(2)
    assert cell_distance(cells[0], cells[0]) == 0


def test_terrain_generation() -> None:
    rng = np.random.default_rng(42)
    cells = get_all_cells(1)[:200]
    terrain = generate_terrain_map(cells, rng)
    assert all(t in TerrainType for t in terrain.values())
    land = get_land_cells(terrain)
    assert len(land) > 0


def test_classify_terrain_land() -> None:
    # North America approximate
    assert classify_terrain_from_latlng(40.0, -100.0) == TerrainType.LAND
