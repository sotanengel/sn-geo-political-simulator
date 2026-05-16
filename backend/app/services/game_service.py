from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

import numpy as np

from app.schemas import (
    ActionRequest,
    CreateGameRequest,
    GameConfigSchema,
    GameStateResponse,
    GameSummary,
    NationView,
    ResourceDict,
)
from app.stores.protocol import GameStore
from game.turn.processor import TurnProcessor
from game.types import (
    ActionType,
    GameAction,
    ResourceType,
    TradeOffer,
    WorldState,
)
from game.world.environment import GameConfig, WorldEnvironment


class GameService:
    def __init__(self, store: GameStore) -> None:
        self._store = store
        self._env = WorldEnvironment()
        self._subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._timeout_tasks: dict[str, asyncio.Task[None]] = {}

    def _lock_for(self, game_id: str) -> asyncio.Lock:
        if game_id not in self._locks:
            self._locks[game_id] = asyncio.Lock()
        return self._locks[game_id]

    async def create_game(self, request: CreateGameRequest) -> GameSummary:
        game_id = str(uuid.uuid4())
        cfg = _to_game_config(request.config, request.seed)
        state = self._env.reset(cfg)

        extra = {
            "submitted": {},
            "processor_config": request.config.model_dump(),
            "pending_actions": {},
            "turn_timeout_seconds": request.config.turn_timeout_seconds,
        }
        self._start_turn_collection(extra)

        async with self._lock_for(game_id):
            await self._store.save_state(game_id, state, extra)
            await self._store.append_history(game_id, {"event": "game_created", "turn": 0})

        self._schedule_turn_timeout(game_id)

        return GameSummary(
            game_id=game_id,
            turn=state.turn,
            max_turns=state.max_turns,
            game_over=state.game_over,
            num_nations=len(state.nations),
        )

    async def get_game(self, game_id: str) -> GameStateResponse | None:
        async with self._lock_for(game_id):
            loaded = await self._store.load_state(game_id)
            if not loaded:
                return None
            state, extra = loaded
            await self._maybe_finalize_by_timeout(game_id, state, extra)
            await self._store.save_state(game_id, state, extra)
            return _state_to_response(game_id, state, extra)

    async def delete_game(self, game_id: str) -> bool:
        if not await self._store.game_exists(game_id):
            return False
        self._cancel_timeout(game_id)
        await self._store.delete_game(game_id)
        self._subscribers.pop(game_id, None)
        self._locks.pop(game_id, None)
        return True

    async def submit_action(self, game_id: str, action: ActionRequest) -> GameStateResponse | None:
        async with self._lock_for(game_id):
            loaded = await self._store.load_state(game_id)
            if not loaded:
                return None
            state, extra = loaded
            if state.game_over:
                return _state_to_response(game_id, state, extra)

            game_action = _to_game_action(action)
            extra["pending_actions"][action.nation_id] = game_action
            extra["submitted"][action.nation_id] = True

            active = [nid for nid, n in state.nations.items() if not n.is_extinct]
            if len(extra["submitted"]) >= len(active):
                await self._resolve_turn(game_id, state, extra)

            await self._store.save_state(game_id, state, extra)
            return _state_to_response(game_id, state, extra)

    async def get_history(self, game_id: str) -> list[dict[str, Any]] | None:
        if not await self._store.game_exists(game_id):
            return None
        return await self._store.get_history(game_id)

    async def get_observation(self, game_id: str, nation_id: str) -> dict[str, Any] | None:
        loaded = await self._store.load_state(game_id)
        if not loaded:
            return None
        state, _ = loaded
        nation = state.nations.get(nation_id)
        if not nation:
            return None
        return {
            "own_resources": nation.resources.to_dict(),
            "own_category": nation.category.value,
            "turn": state.turn,
            "territory_size": len(nation.territory),
            "num_nations": len(state.nations),
        }

    def subscribe(self, game_id: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._subscribers.setdefault(game_id, []).append(queue)
        return queue

    def _start_turn_collection(self, extra: dict[str, Any]) -> None:
        extra["turn_started_at"] = time.monotonic()
        extra["submitted"] = {}
        extra["pending_actions"] = {}

    def _schedule_turn_timeout(self, game_id: str) -> None:
        self._cancel_timeout(game_id)

        async def _watch() -> None:
            loaded = await self._store.load_state(game_id)
            if not loaded:
                return
            _, extra = loaded
            timeout = float(extra.get("turn_timeout_seconds", 30))
            await asyncio.sleep(timeout)
            async with self._lock_for(game_id):
                loaded2 = await self._store.load_state(game_id)
                if not loaded2:
                    return
                state, extra2 = loaded2
                if state.game_over:
                    return
                await self._maybe_finalize_by_timeout(game_id, state, extra2)
                await self._store.save_state(game_id, state, extra2)

        self._timeout_tasks[game_id] = asyncio.create_task(_watch())

    def _cancel_timeout(self, game_id: str) -> None:
        task = self._timeout_tasks.pop(game_id, None)
        if task and not task.done():
            task.cancel()

    async def _maybe_finalize_by_timeout(
        self,
        game_id: str,
        state: WorldState,
        extra: dict[str, Any],
    ) -> bool:
        if state.game_over:
            return False

        active = [nid for nid, n in state.nations.items() if not n.is_extinct]
        submitted = extra.get("submitted", {})
        if len(submitted) >= len(active):
            await self._resolve_turn(game_id, state, extra)
            return True

        started = extra.get("turn_started_at", time.monotonic())
        timeout = float(extra.get("turn_timeout_seconds", 30))
        if time.monotonic() - started < timeout:
            return False

        for nid in active:
            if nid not in submitted:
                extra["pending_actions"][nid] = GameAction(
                    nation_id=nid, action_type=ActionType.PASS
                )
                extra["submitted"][nid] = True

        await self._resolve_turn(game_id, state, extra)
        return True

    async def _resolve_turn(
        self,
        game_id: str,
        state: WorldState,
        extra: dict[str, Any],
    ) -> None:
        self._cancel_timeout(game_id)

        cfg = GameConfigSchema.model_validate(extra.get("processor_config", {}))
        processor = _processor_from_config(cfg)
        rng = np.random.default_rng(state.seed if state.seed is not None else None)

        processor.start_turn(state, rng)
        actions = list(extra.get("pending_actions", {}).values())
        processor.resolve_actions(state, actions, rng)
        processor.end_turn(state)

        if not state.game_over:
            self._start_turn_collection(extra)
            extra["turn_timeout_seconds"] = cfg.turn_timeout_seconds
            self._schedule_turn_timeout(game_id)
        else:
            extra["submitted"] = {}
            extra["pending_actions"] = {}

        await self._store.append_history(
            game_id,
            {"event": "turn_resolved", "turn": state.turn, "game_over": state.game_over},
        )
        await self._broadcast(game_id, {"event": "state_updated", "turn": state.turn})

    async def _broadcast(self, game_id: str, event: dict[str, Any]) -> None:
        for queue in self._subscribers.get(game_id, []):
            await queue.put(event)


def _to_game_config(schema: GameConfigSchema, seed: int | None) -> GameConfig:
    res_cfg = schema.resources or {}
    initial = res_cfg.get("initial_range", {})
    return GameConfig(
        num_nations=schema.num_nations,
        max_turns=schema.max_turns,
        h3_resolution=schema.h3_resolution,
        seed=seed,
        initial_resource_min=initial.get("min", 100),
        initial_resource_max=initial.get("max", 300),
        max_trades_per_turn=res_cfg.get("max_trades_per_turn", 5),
        victory_condition=schema.victory_condition,
    )


def _processor_from_config(schema: GameConfigSchema) -> TurnProcessor:
    mil = schema.military or {}
    res = schema.resources or {}
    return TurnProcessor(
        max_trades_per_turn=res.get("max_trades_per_turn", 5),
        food_per_unit=mil.get("unit_maintenance_food", 1),
        fuel_per_unit=mil.get("unit_maintenance_fuel", 1),
        tech_scale_factor=mil.get("tech_scale_factor", 0.1),
        victory_condition=schema.victory_condition,
    )


def _to_game_action(req: ActionRequest) -> GameAction:
    trade = None
    if req.trade:
        trade = TradeOffer(
            from_nation=req.nation_id,
            to_nation=req.trade.get("to_nation", ""),
            offer={ResourceType(k): v for k, v in req.trade.get("offer", {}).items()},
            request={ResourceType(k): v for k, v in req.trade.get("request", {}).items()},
        )
    return GameAction(
        nation_id=req.nation_id,
        action_type=ActionType(req.action_type),
        source_cell=req.source_cell,
        target_cell=req.target_cell,
        units=req.units,
        trade=trade,
        trade_offer_id=req.trade_offer_id,
    )


def _state_to_response(game_id: str, state: WorldState, extra: dict[str, Any]) -> GameStateResponse:
    submitted = extra.get("submitted", {})
    nations = [
        NationView(
            id=n.id,
            name=n.name,
            category=n.category.value,
            territory_size=len(n.territory),
            resources=ResourceDict(**{k: v for k, v in n.resources.to_dict().items()}),
            is_extinct=n.is_extinct,
            controller=n.controller.value,
        )
        for n in state.nations.values()
    ]
    return GameStateResponse(
        game_id=game_id,
        turn=state.turn,
        max_turns=state.max_turns,
        game_over=state.game_over,
        winners=state.winners,
        nations=nations,
        pending_actions={nid: nid not in submitted for nid in state.nations},
    )
