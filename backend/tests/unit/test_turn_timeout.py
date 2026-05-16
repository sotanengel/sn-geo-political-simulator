import asyncio

import pytest

from app.schemas import ActionRequest, CreateGameRequest, GameConfigSchema
from app.services.game_service import GameService
from app.stores.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_turn_timeout_auto_pass() -> None:
    store = MemoryStore()
    svc = GameService(store)
    summary = await svc.create_game(
        CreateGameRequest(
            config=GameConfigSchema(
                num_nations=2,
                max_turns=5,
                h3_resolution=1,
                turn_timeout_seconds=1,
            ),
            seed=42,
        )
    )
    await svc.submit_action(
        summary.game_id,
        ActionRequest(nation_id="nation_0", action_type="PASS"),
    )
    await asyncio.sleep(1.1)
    state = await svc.get_game(summary.game_id)
    assert state is not None
    assert state.turn >= 1


@pytest.mark.asyncio
async def test_all_submit_before_timeout() -> None:
    store = MemoryStore()
    svc = GameService(store)
    summary = await svc.create_game(
        CreateGameRequest(
            config=GameConfigSchema(num_nations=2, max_turns=3, h3_resolution=1),
            seed=1,
        )
    )
    for nid in ("nation_0", "nation_1"):
        await svc.submit_action(
            summary.game_id,
            ActionRequest(nation_id=nid, action_type="PASS"),
        )
    state = await svc.get_game(summary.game_id)
    assert state is not None
    assert state.turn >= 1
