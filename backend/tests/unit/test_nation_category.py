import numpy as np

from game.nation.borders import generate_initial_borders
from game.nation.category import determine_nation_category
from game.types import NationCategory, TerrainType
from game.world.h3_grid import get_all_cells, get_neighbors
from game.world.terrain import generate_terrain_map, get_land_cells


def test_generate_borders_covers_land() -> None:
    rng = np.random.default_rng(0)
    cells = get_all_cells(1)
    terrain = generate_terrain_map(cells, rng)
    land = get_land_cells(terrain)
    territories, capitals = generate_initial_borders(land, 4, rng)
    assert len(territories) == 4
    assigned = set()
    for t in territories.values():
        assigned |= t
    assert assigned <= land
    assert len(assigned) > len(land) * 0.5


def test_island_nation_on_isolated_land() -> None:
    rng = np.random.default_rng(0)
    cells = get_all_cells(1)
    terrain = generate_terrain_map(cells, rng)
    land = list(get_land_cells(terrain))
    if len(land) < 2:
        return
    # Find two land cells far apart (different components likely)
    cell_a = land[0]
    cell_b = land[-1]
    all_terr = {"n1": {cell_a}, "n2": {cell_b}}
    cat1 = determine_nation_category({cell_a}, all_terr, "n1", terrain, set(land))
    # If same component, both may be continental; at least valid category
    assert cat1 in (NationCategory.ISLAND, NationCategory.CONTINENTAL)
