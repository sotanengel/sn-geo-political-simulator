from __future__ import annotations

import h3

from game.types import H3Cell


def get_all_cells(resolution: int) -> list[H3Cell]:
    """Return all H3 cells at resolution."""
    cells: list[H3Cell] = []
    for res0 in h3.get_res0_cells():
        cells.extend(h3.cell_to_children(res0, resolution))
    return cells


def get_neighbors(cell: H3Cell, k: int = 1) -> list[H3Cell]:
    return [n for n in h3.grid_disk(cell, k) if n != cell]


def are_adjacent(cell_a: H3Cell, cell_b: H3Cell) -> bool:
    return cell_b in get_neighbors(cell_a, 1)


def cell_distance(cell_a: H3Cell, cell_b: H3Cell) -> int:
    return h3.grid_distance(cell_a, cell_b)
