from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResourceDict(BaseModel):
    FOOD: int = 0
    FUEL: int = 0
    ORE: int = 0
    TECH: int = 0
    GOLD: int = 0


class GameConfigSchema(BaseModel):
    num_nations: int = 10
    max_turns: int = 50
    h3_resolution: int = 2
    island_nation_count: int | None = None
    victory_condition: str = "largest_territory"
    turn_timeout_seconds: int = 30
    resources: dict[str, Any] = Field(default_factory=dict)
    military: dict[str, Any] = Field(default_factory=dict)
    controllers: dict[str, str] = Field(default_factory=dict)


class CreateGameRequest(BaseModel):
    config: GameConfigSchema = Field(default_factory=GameConfigSchema)
    seed: int | None = None


class ActionRequest(BaseModel):
    nation_id: str
    action_type: str
    source_cell: str | None = None
    target_cell: str | None = None
    units: int = 0
    trade: dict[str, Any] | None = None
    trade_offer_id: str | None = None


class GameSummary(BaseModel):
    game_id: str
    turn: int
    max_turns: int
    game_over: bool
    num_nations: int


class NationView(BaseModel):
    id: str
    name: str
    category: str
    territory_size: int
    resources: ResourceDict
    is_extinct: bool
    controller: str


class GameStateResponse(BaseModel):
    game_id: str
    turn: int
    max_turns: int
    game_over: bool
    winners: list[str]
    nations: list[NationView]
    pending_actions: dict[str, bool]
