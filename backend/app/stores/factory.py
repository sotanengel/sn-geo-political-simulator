from __future__ import annotations

from typing import Any

from app.config import Settings
from app.stores.composite_store import CompositeStore
from app.stores.memory_store import MemoryStore
from app.stores.postgres_store import PostgresHistoryStore
from app.stores.redis_store import RedisStore


async def build_store(settings: Settings) -> Any:
    if settings.use_memory_store:
        return MemoryStore()

    redis_store = RedisStore(settings.redis_url)
    history_store = PostgresHistoryStore(settings.database_url)
    await redis_store.init()
    await history_store.init()
    return CompositeStore(redis_store, history_store)


async def close_store(store: Any) -> None:
    if isinstance(store, MemoryStore):
        return
    if isinstance(store, CompositeStore):
        await store._redis.close()
        await store._history.close()
