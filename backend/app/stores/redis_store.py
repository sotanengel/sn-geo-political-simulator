from __future__ import annotations

from typing import Any

import redis.asyncio as redis

from app.stores.serialization import (
    pack_game_blob,
    unpack_game_blob,
)
from game.types import WorldState

STATE_KEY_PREFIX = "geo:game:"


class RedisStore:
    """Redis-backed game state persistence."""

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._client: redis.Redis | None = None

    async def init(self) -> None:
        self._client = redis.from_url(self._redis_url, decode_responses=True)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _key(self, game_id: str) -> str:
        return f"{STATE_KEY_PREFIX}{game_id}"

    async def save_state(self, game_id: str, state: WorldState, extra: dict[str, Any]) -> None:
        assert self._client is not None
        await self._client.set(self._key(game_id), pack_game_blob(state, extra))

    async def load_state(self, game_id: str) -> tuple[WorldState, dict[str, Any]] | None:
        assert self._client is not None
        blob = await self._client.get(self._key(game_id))
        if blob is None:
            return None
        return unpack_game_blob(blob)

    async def delete_state(self, game_id: str) -> None:
        assert self._client is not None
        await self._client.delete(self._key(game_id))

    async def game_exists(self, game_id: str) -> bool:
        assert self._client is not None
        return bool(await self._client.exists(self._key(game_id)))
