from __future__ import annotations

from game.types import Nation, ResourceStock, ResourceType, WorldState


def apply_maintenance(
    nation: Nation,
    food_per_unit: int = 1,
    fuel_per_unit: int = 1,
) -> None:
    total = nation.total_units
    food_cost = total * food_per_unit
    fuel_cost = total * fuel_per_unit

    if not nation.resources.subtract(ResourceType.FOOD, food_cost):
        _reduce_units_for_shortage(nation, ResourceType.FOOD, food_per_unit)
    if not nation.resources.subtract(ResourceType.FUEL, fuel_cost):
        _reduce_units_for_shortage(nation, ResourceType.FUEL, fuel_per_unit)


def _reduce_units_for_shortage(
    nation: Nation,
    resource: ResourceType,
    per_unit: int,
) -> None:
    """Force unit reduction when maintenance cannot be paid."""
    while nation.total_units > 0 and nation.resources.get(resource) < per_unit:
        cell = max(nation.military_units, key=nation.military_units.get)  # type: ignore[arg-type]
        nation.military_units[cell] -= 1
        if nation.military_units[cell] <= 0:
            del nation.military_units[cell]


def produce_units(
    nation: Nation,
    count: int,
    ore_cost_per_unit: int = 10,
) -> bool:
    total_ore = count * ore_cost_per_unit
    if nation.capital is None:
        return False
    if not nation.resources.subtract(ResourceType.ORE, total_ore):
        return False
    nation.military_units[nation.capital] = nation.military_units.get(nation.capital, 0) + count
    return True


def move_units(
    nation: Nation,
    from_cell: str,
    to_cell: str,
    count: int,
) -> bool:
    available = nation.military_units.get(from_cell, 0)
    if count <= 0 or count > available:
        return False
    nation.military_units[from_cell] = available - count
    if nation.military_units[from_cell] == 0:
        del nation.military_units[from_cell]
    nation.military_units[to_cell] = nation.military_units.get(to_cell, 0) + count
    return True


def mark_extinct_nations(state: WorldState) -> None:
    for nation in state.nations.values():
        if len(nation.territory) == 0:
            nation.is_extinct = True
            nation.military_units.clear()
            nation.resources = ResourceStock()
