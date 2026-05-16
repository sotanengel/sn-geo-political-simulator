import pytest

from app.stores.redis_store import RedisStore
from app.stores.serialization import pack_game_blob, unpack_game_blob
from game.types import WorldState


@pytest.mark.asyncio
async def test_redis_store_round_trip() -> None:
    fakeredis = pytest.importorskip("fakeredis")
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    store = RedisStore("redis://localhost")
    store._client = fake

    state = WorldState(turn=2, max_turns=10)
    extra = {"submitted": {"nation_0": True}, "turn_timeout_seconds": 30}
    await store.save_state("test-game-id", state, extra)

    assert await store.game_exists("test-game-id")
    loaded = await store.load_state("test-game-id")
    assert loaded is not None
    s2, e2 = loaded
    assert s2.turn == 2
    assert e2["turn_timeout_seconds"] == 30

    await store.delete_state("test-game-id")
    assert not await store.game_exists("test-game-id")


@pytest.mark.asyncio
async def test_pack_unpack_via_redis() -> None:
    blob = pack_game_blob(WorldState(turn=0, max_turns=5), {"submitted": {}})
    s, e = unpack_game_blob(blob)
    assert s.max_turns == 5
