from __future__ import annotations

import h3
import numpy as np

from game.types import H3Cell
from game.world.h3_grid import get_neighbors


def _latlng_distance(cell_a: H3Cell, cell_b: H3Cell) -> float:
    lat1, lng1 = h3.cell_to_latlng(str(cell_a))
    lat2, lng2 = h3.cell_to_latlng(str(cell_b))
    return float(np.hypot(lat1 - lat2, lng1 - lng2))


def _safe_distance(cell_a: H3Cell, cell_b: H3Cell) -> float:
    a, b = str(cell_a), str(cell_b)
    try:
        return float(h3.grid_distance(a, b))
    except Exception:
        return _latlng_distance(a, b)


def _remove_exclaves(territory: set[H3Cell], capital: H3Cell) -> set[H3Cell]:
    """Keep only the largest connected component containing capital."""
    if capital not in territory:
        if not territory:
            return set()
        capital = next(iter(territory))

    visited: set[H3Cell] = set()
    components: list[set[H3Cell]] = []
    remaining = set(territory)

    while remaining:
        start = next(iter(remaining))
        component: set[H3Cell] = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell not in remaining or cell in visited:
                continue
            visited.add(cell)
            remaining.remove(cell)
            component.add(cell)
            for n in get_neighbors(cell, 1):
                if n in territory and n not in visited:
                    stack.append(n)
        components.append(component)

    capital_component = next((c for c in components if capital in c), components[0])
    return capital_component


def generate_initial_borders(
    land_cells: set[H3Cell],
    num_nations: int,
    rng: np.random.Generator,
) -> tuple[dict[str, set[H3Cell]], dict[str, H3Cell]]:
    """
    Voronoi partition on land cells from evenly dispersed capitals.
    Returns territory per nation id and capital cells.
    """
    land_list = list(land_cells)
    if len(land_list) < num_nations:
        raise ValueError("Not enough land cells for requested nations")

    # Select capitals with max-min distance heuristic
    capitals: list[H3Cell] = [str(rng.choice(land_list))]
    for _ in range(num_nations - 1):
        best_cell = land_list[0]
        best_dist = -1.0
        for candidate in land_list:
            if candidate in capitals:
                continue
            min_d = min(_safe_distance(candidate, cap) for cap in capitals)
            if min_d > best_dist:
                best_dist = min_d
                best_cell = candidate
        capitals.append(str(best_cell))

    territories: dict[str, set[H3Cell]] = {f"nation_{i}": set() for i in range(num_nations)}
    capital_map: dict[str, H3Cell] = {
        f"nation_{i}": capitals[i] for i in range(num_nations)
    }

    for cell in land_list:
        cell = str(cell)
        best_nation = "nation_0"
        best_dist = float("inf")
        for i, cap in enumerate(capitals):
            d = _safe_distance(cell, cap)
            if d < best_dist:
                best_dist = d
                best_nation = f"nation_{i}"
        territories[best_nation].add(cell)

    for nid, cap in capital_map.items():
        territories[nid] = _remove_exclaves(territories[nid], cap)

    return territories, capital_map
