from __future__ import annotations

import json
from typing import Any

from game.types import (
    ActionType,
    ControllerType,
    GameAction,
    Nation,
    NationCategory,
    ResourceStock,
    ResourceType,
    TerrainType,
    TradeOffer,
    WorldState,
)


def serialize_state(state: WorldState) -> dict[str, Any]:
    return {
        "turn": state.turn,
        "max_turns": state.max_turns,
        "game_over": state.game_over,
        "winners": state.winners,
        "resolution": state.resolution,
        "seed": int(state.seed) if state.seed is not None else None,
        "land_cells": list(state.land_cells),
        "cell_terrain": {k: v.value for k, v in state.cell_terrain.items()},
        "cell_owner": state.cell_owner,
        "cell_yields": {
            k: {
                "food": y.food,
                "fuel": y.fuel,
                "ore": y.ore,
                "tech": y.tech,
                "gold": y.gold,
            }
            for k, y in state.cell_yields.items()
        },
        "nations": {
            nid: {
                "id": n.id,
                "name": n.name,
                "category": n.category.value,
                "territory": list(n.territory),
                "military_units": {k: int(v) for k, v in n.military_units.items()},
                "resources": n.resources.to_dict(),
                "controller": n.controller.value,
                "capital": n.capital,
                "tech_investment": n.tech_investment,
                "is_extinct": n.is_extinct,
            }
            for nid, n in state.nations.items()
        },
    }


def deserialize_state(data: dict[str, Any]) -> WorldState:
    from game.types import CellYield

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

    cell_yields = {}
    for k, y in data.get("cell_yields", {}).items():
        cell_yields[k] = CellYield(**y)

    return WorldState(
        turn=data["turn"],
        max_turns=data["max_turns"],
        game_over=data["game_over"],
        winners=data.get("winners", []),
        nations=nations,
        cell_terrain={k: TerrainType(v) for k, v in data.get("cell_terrain", {}).items()},
        cell_owner=data.get("cell_owner", {}),
        cell_yields=cell_yields,
        land_cells=set(data.get("land_cells", [])),
        resolution=data.get("resolution", 2),
        seed=data.get("seed"),
    )


def serialize_game_action(action: GameAction) -> dict[str, Any]:
    trade = None
    if action.trade:
        trade = {
            "from_nation": action.trade.from_nation,
            "to_nation": action.trade.to_nation,
            "offer": {k.value: v for k, v in action.trade.offer.items()},
            "request": {k.value: v for k, v in action.trade.request.items()},
            "offer_id": action.trade.offer_id,
        }
    return {
        "nation_id": action.nation_id,
        "action_type": action.action_type.value,
        "source_cell": action.source_cell,
        "target_cell": action.target_cell,
        "units": action.units,
        "trade": trade,
        "trade_offer_id": action.trade_offer_id,
    }


def deserialize_game_action(data: dict[str, Any]) -> GameAction:
    trade = None
    if data.get("trade"):
        t = data["trade"]
        trade = TradeOffer(
            from_nation=t["from_nation"],
            to_nation=t["to_nation"],
            offer={ResourceType(k): v for k, v in t.get("offer", {}).items()},
            request={ResourceType(k): v for k, v in t.get("request", {}).items()},
            offer_id=t.get("offer_id", ""),
        )
    return GameAction(
        nation_id=data["nation_id"],
        action_type=ActionType(data["action_type"]),
        source_cell=data.get("source_cell"),
        target_cell=data.get("target_cell"),
        units=data.get("units", 0),
        trade=trade,
        trade_offer_id=data.get("trade_offer_id"),
    )


def serialize_extra(extra: dict[str, Any]) -> dict[str, Any]:
    out = dict(extra)
    pending = extra.get("pending_actions", {})
    if pending:
        out["pending_actions"] = {
            nid: serialize_game_action(a) if isinstance(a, GameAction) else a
            for nid, a in pending.items()
        }
    return out


def deserialize_extra(extra: dict[str, Any]) -> dict[str, Any]:
    out = dict(extra)
    pending = extra.get("pending_actions", {})
    if pending:
        out["pending_actions"] = {
            nid: deserialize_game_action(a) if isinstance(a, dict) else a
            for nid, a in pending.items()
        }
    return out


def pack_game_blob(state: WorldState, extra: dict[str, Any]) -> str:
    return json.dumps(
        {
            "state": serialize_state(state),
            "extra": serialize_extra(extra),
        }
    )


def unpack_game_blob(blob: str) -> tuple[WorldState, dict[str, Any]]:
    data = json.loads(blob)
    return deserialize_state(data["state"]), deserialize_extra(data["extra"])
