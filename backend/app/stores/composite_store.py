from __future__ import annotations

from typing import Any

from app.stores.postgres_store import PostgresHistoryStore
from app.stores.redis_store import RedisStore
from game.types import WorldState


class CompositeStore:
    """Redis for live state, PostgreSQL for history."""

    def __init__(self, redis_store: RedisStore, history_store: PostgresHistoryStore) -> None:
        self._redis = redis_store
        self._history = history_store

    async def save_state(self, game_id: str, state: WorldState, extra: dict[str, Any]) -> None:
        await self._redis.save_state(game_id, state, extra)

    async def load_state(self, game_id: str) -> tuple[WorldState, dict[str, Any]] | None:
        return await self._redis.load_state(game_id)

    async def delete_game(self, game_id: str) -> None:
        await self._redis.delete_state(game_id)
        await self._history.delete_history(game_id)

    async def game_exists(self, game_id: str) -> bool:
        return await self._redis.game_exists(game_id)

    async def append_history(self, game_id: str, record: dict[str, Any]) -> None:
        await self._history.append_history(game_id, record)

    async def get_history(self, game_id: str) -> list[dict[str, Any]]:
        return await self._history.get_history(game_id)
