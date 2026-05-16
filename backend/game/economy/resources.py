from __future__ import annotations

import numpy as np

from game.types import CellYield, H3Cell, Nation, ResourceStock, ResourceType, TerrainType, WorldState


def generate_cell_yields(
    terrain: dict[H3Cell, TerrainType],
    rng: np.random.Generator,
) -> dict[H3Cell, CellYield]:
    yields: dict[H3Cell, CellYield] = {}
    for cell, t in terrain.items():
        if t != TerrainType.LAND:
            continue
        yields[cell] = CellYield(
            food=int(rng.integers(1, 5)),
            fuel=int(rng.integers(0, 3)),
            ore=int(rng.integers(0, 3)),
            tech=int(rng.integers(0, 2)),
            gold=int(rng.integers(0, 2)),
        )
    return yields


def apply_turn_production(state: WorldState) -> None:
    for nation in state.nations.values():
        if nation.is_extinct:
            continue
        for cell in nation.territory:
            cy = state.cell_yields.get(cell)
            if cy:
                stock = cy.as_stock()
                for rt in ResourceType:
                    nation.resources.add(rt, stock.get(rt))


def random_initial_resources(
    rng: np.random.Generator,
    min_val: int = 100,
    max_val: int = 300,
) -> ResourceStock:
    return ResourceStock(
        food=int(rng.integers(min_val, max_val + 1)),
        fuel=int(rng.integers(min_val, max_val + 1)),
        ore=int(rng.integers(min_val, max_val + 1)),
        tech=int(rng.integers(min_val, max_val + 1)),
        gold=int(rng.integers(min_val, max_val + 1)),
    )


def can_afford(stock: ResourceStock, costs: dict[ResourceType, int]) -> bool:
    return all(stock.get(r) >= amount for r, amount in costs.items())


def transfer_resources(
    from_stock: ResourceStock,
    to_stock: ResourceStock,
    amounts: dict[ResourceType, int],
) -> bool:
    if not can_afford(from_stock, amounts):
        return False
    for r, amount in amounts.items():
        from_stock.subtract(r, amount)
        to_stock.add(r, amount)
    return True
