from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

H3Cell = str


class TerrainType(str, Enum):
    LAND = "LAND"
    SHALLOW_SEA = "SHALLOW_SEA"
    DEEP_SEA = "DEEP_SEA"


class NationCategory(str, Enum):
    ISLAND = "ISLAND"
    CONTINENTAL = "CONTINENTAL"


class ControllerType(str, Enum):
    HUMAN = "HUMAN"
    RL_AGENT = "RL_AGENT"
    AI_RULE_BASED = "AI_RULE_BASED"


class ActionType(str, Enum):
    MOVE = "MOVE"
    INVADE = "INVADE"
    TRADE_OFFER = "TRADE_OFFER"
    TRADE_ACCEPT = "TRADE_ACCEPT"
    TRADE_REJECT = "TRADE_REJECT"
    GIFT = "GIFT"
    PASS = "PASS"


class InvasionResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class ResourceType(str, Enum):
    FOOD = "FOOD"
    FUEL = "FUEL"
    ORE = "ORE"
    TECH = "TECH"
    GOLD = "GOLD"


RESOURCE_TYPES = list(ResourceType)


@dataclass
class ResourceStock:
    food: int = 0
    fuel: int = 0
    ore: int = 0
    tech: int = 0
    gold: int = 0

    def get(self, resource: ResourceType) -> int:
        return getattr(self, resource.value.lower())

    def set(self, resource: ResourceType, value: int) -> None:
        setattr(self, resource.value.lower(), max(0, value))

    def add(self, resource: ResourceType, amount: int) -> None:
        self.set(resource, self.get(resource) + amount)

    def subtract(self, resource: ResourceType, amount: int) -> bool:
        current = self.get(resource)
        if current < amount:
            return False
        self.set(resource, current - amount)
        return True

    def to_dict(self) -> dict[str, int]:
        return {r.value: self.get(r) for r in RESOURCE_TYPES}


@dataclass
class CellYield:
    food: int = 0
    fuel: int = 0
    ore: int = 0
    tech: int = 0
    gold: int = 0

    def as_stock(self) -> ResourceStock:
        return ResourceStock(
            food=self.food,
            fuel=self.fuel,
            ore=self.ore,
            tech=self.tech,
            gold=self.gold,
        )


@dataclass
class TradeOffer:
    from_nation: str
    to_nation: str
    offer: dict[ResourceType, int]
    request: dict[ResourceType, int]
    offer_id: str = ""


@dataclass
class GameAction:
    nation_id: str
    action_type: ActionType
    source_cell: H3Cell | None = None
    target_cell: H3Cell | None = None
    units: int = 0
    trade: TradeOffer | None = None
    trade_offer_id: str | None = None


@dataclass
class Nation:
    id: str
    name: str
    category: NationCategory
    territory: set[H3Cell] = field(default_factory=set)
    military_units: dict[H3Cell, int] = field(default_factory=dict)
    resources: ResourceStock = field(default_factory=ResourceStock)
    controller: ControllerType = ControllerType.AI_RULE_BASED
    capital: H3Cell | None = None
    tech_investment: int = 0
    is_extinct: bool = False

    @property
    def total_units(self) -> int:
        return sum(self.military_units.values())


@dataclass
class WorldState:
    turn: int = 0
    max_turns: int = 50
    nations: dict[str, Nation] = field(default_factory=dict)
    cell_terrain: dict[H3Cell, TerrainType] = field(default_factory=dict)
    cell_yields: dict[H3Cell, CellYield] = field(default_factory=dict)
    cell_owner: dict[H3Cell, str] = field(default_factory=dict)
    pending_trades: list[TradeOffer] = field(default_factory=list)
    land_cells: set[H3Cell] = field(default_factory=set)
    resolution: int = 2
    seed: int | None = None
    game_over: bool = False
    winners: list[str] = field(default_factory=list)

    @property
    def total_land_cells(self) -> int:
        return len(self.land_cells)
