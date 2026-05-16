import numpy as np

from game.economy.resources import (
    apply_turn_production,
    can_afford,
    random_initial_resources,
    transfer_resources,
)
from game.types import CellYield, Nation, ResourceStock, ResourceType, WorldState


def test_resource_stock_operations() -> None:
    stock = ResourceStock(food=10, fuel=5)
    assert stock.get(ResourceType.FOOD) == 10
    assert stock.subtract(ResourceType.FOOD, 3)
    assert stock.get(ResourceType.FOOD) == 7
    assert not stock.subtract(ResourceType.FUEL, 10)


def test_transfer_resources() -> None:
    a = ResourceStock(food=50)
    b = ResourceStock()
    assert transfer_resources(a, b, {ResourceType.FOOD: 20})
    assert a.food == 30
    assert b.food == 20


def test_turn_production() -> None:
    from game.types import NationCategory

    nation = Nation(
        id="n1", name="A", category=NationCategory.ISLAND, territory={"c1"}
    )
    state = WorldState(
        nations={"n1": nation},
        cell_yields={"c1": CellYield(food=3, ore=2)},
    )
    apply_turn_production(state)
    assert nation.resources.food == 3
    assert nation.resources.ore == 2


def test_random_initial_resources() -> None:
    rng = np.random.default_rng(1)
    stock = random_initial_resources(rng, 10, 20)
    assert 10 <= stock.food <= 20
