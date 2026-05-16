import uuid

import pytest

from app.config import Settings
from app.stores.factory import build_store, close_store
from game.types import WorldState


@pytest.mark.asyncio
async def test_composite_store_persistence() -> None:
    settings = Settings(use_memory_store=False)
    store = await build_store(settings)
    try:
        game_id = str(uuid.uuid4())
        state = WorldState(turn=0, max_turns=20)
        extra = {"submitted": {}, "pending_actions": {}, "turn_timeout_seconds": 30}

        await store.save_state(game_id, state, extra)
        assert await store.game_exists(game_id)

        await store.append_history(game_id, {"event": "game_created", "turn": 0})
        history = await store.get_history(game_id)
        assert len(history) == 1
        assert history[0]["event"] == "game_created"

        loaded = await store.load_state(game_id)
        assert loaded is not None
        assert loaded[0].max_turns == 20

        await store.delete_game(game_id)
        assert not await store.game_exists(game_id)
        assert await store.get_history(game_id) == []
    finally:
        await close_store(store)
