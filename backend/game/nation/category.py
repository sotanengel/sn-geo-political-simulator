from __future__ import annotations

from collections import defaultdict, deque

from game.types import H3Cell, NationCategory, TerrainType
from game.world.h3_grid import get_neighbors


def _land_components(
    land_cells: set[H3Cell],
    terrain: dict[H3Cell, TerrainType],
) -> list[set[H3Cell]]:
    """Connected components of land cells (4/6-neighbor on land only)."""
    remaining = set(land_cells)
    components: list[set[H3Cell]] = []
    while remaining:
        start = next(iter(remaining))
        component: set[H3Cell] = set()
        queue: deque[H3Cell] = deque([start])
        while queue:
            cell = queue.popleft()
            if cell not in remaining:
                continue
            remaining.remove(cell)
            component.add(cell)
            for neighbor in get_neighbors(cell, 1):
                if neighbor in remaining and terrain.get(neighbor) == TerrainType.LAND:
                    queue.append(neighbor)
        components.append(component)
    return components


def determine_nation_category(
    nation_territory: set[H3Cell],
    all_nations_territory: dict[str, set[H3Cell]],
    nation_id: str,
    terrain: dict[H3Cell, TerrainType],
    land_cells: set[H3Cell],
) -> NationCategory:
    """
    Island nation: sole nation on its landmass component at game start.
    Category is fixed at initialization (this function called once per nation).
    """
    components = _land_components(land_cells, terrain)
    for component in components:
        nations_on_component = [
            nid
            for nid, terr in all_nations_territory.items()
            if terr & component
        ]
        if nation_id in nations_on_component:
            if len(nations_on_component) == 1:
                return NationCategory.ISLAND
            return NationCategory.CONTINENTAL
    return NationCategory.CONTINENTAL


def build_landmass_map(
    land_cells: set[H3Cell],
    terrain: dict[H3Cell, TerrainType],
) -> dict[H3Cell, int]:
    """Map each land cell to landmass component id."""
    components = _land_components(land_cells, terrain)
    mapping: dict[H3Cell, int] = {}
    for idx, component in enumerate(components):
        for cell in component:
            mapping[cell] = idx
    return mapping


def nations_per_landmass(
    nations_territory: dict[str, set[H3Cell]],
    landmass_map: dict[H3Cell, int],
) -> dict[int, set[str]]:
    result: dict[int, set[str]] = defaultdict(set)
    for nid, territory in nations_territory.items():
        for cell in territory:
            if cell in landmass_map:
                result[landmass_map[cell]].add(nid)
    return result
