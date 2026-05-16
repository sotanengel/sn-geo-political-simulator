from __future__ import annotations

import json
from typing import Any

from game.types import WorldState


class MemoryStore:
    """In-memory game state store (default for local dev and tests)."""

    def __init__(self) -> None:
        self._games: dict[str, dict[str, Any]] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}

    async def save_state(self, game_id: str, state: WorldState, extra: dict[str, Any]) -> None:
        self._games[game_id] = {
            "state": _serialize_state(state),
            "extra": extra,
        }

    async def load_state(self, game_id: str) -> tuple[WorldState, dict[str, Any]] | None:
        entry = self._games.get(game_id)
        if not entry:
            return None
        return _deserialize_state(entry["state"]), entry["extra"]

    async def delete_game(self, game_id: str) -> None:
        self._games.pop(game_id, None)
        self._history.pop(game_id, None)

    async def append_history(self, game_id: str, record: dict[str, Any]) -> None:
        self._history.setdefault(game_id, []).append(record)

    async def get_history(self, game_id: str) -> list[dict[str, Any]]:
        return self._history.get(game_id, [])


def _serialize_state(state: WorldState) -> dict[str, Any]:
    return {
        "turn": state.turn,
        "max_turns": state.max_turns,
        "game_over": state.game_over,
        "winners": state.winners,
        "resolution": state.resolution,
        "seed": state.seed,
        "land_cells": list(state.land_cells),
        "cell_terrain": {k: v.value for k, v in state.cell_terrain.items()},
        "cell_owner": state.cell_owner,
        "nations": {
            nid: {
                "id": n.id,
                "name": n.name,
                "category": n.category.value,
                "territory": list(n.territory),
                "military_units": n.military_units,
                "resources": n.resources.to_dict(),
                "controller": n.controller.value,
                "capital": n.capital,
                "tech_investment": n.tech_investment,
                "is_extinct": n.is_extinct,
            }
            for nid, n in state.nations.items()
        },
    }


def _deserialize_state(data: dict[str, Any]) -> WorldState:
    from game.types import (
        ControllerType,
        Nation,
        NationCategory,
        ResourceStock,
        TerrainType,
        WorldState,
    )

    nations = {}
    for nid, nd in data["nations"].items():
        res = nd["resources"]
        nations[nid] = Nation(
            id=nd["id"],
            name=nd["name"],
            category=NationCategory(nd["category"]),
            territory=set(nd["territory"]),
            military_units=nd["military_units"],
            resources=ResourceStock(
                food=res.get("FOOD", 0),
                fuel=res.get("FUEL", 0),
                ore=res.get("ORE", 0),
                tech=res.get("TECH", 0),
                gold=res.get("GOLD", 0),
            ),
            controller=ControllerType(nd["controller"]),
            capital=nd.get("capital"),
            tech_investment=nd.get("tech_investment", 0),
            is_extinct=nd.get("is_extinct", False),
        )

    return WorldState(
        turn=data["turn"],
        max_turns=data["max_turns"],
        game_over=data["game_over"],
        winners=data.get("winners", []),
        nations=nations,
        cell_terrain={k: TerrainType(v) for k, v in data.get("cell_terrain", {}).items()},
        cell_owner=data.get("cell_owner", {}),
        land_cells=set(data.get("land_cells", [])),
        resolution=data.get("resolution", 2),
        seed=data.get("seed"),
    )
