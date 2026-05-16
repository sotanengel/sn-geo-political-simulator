from __future__ import annotations

import json
from typing import Any

import asyncpg

MIGRATE_SQL = """
CREATE TABLE IF NOT EXISTS game_history (
  id BIGSERIAL PRIMARY KEY,
  game_id UUID NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_game_history_game_id ON game_history(game_id);
"""


class PostgresHistoryStore:
    """PostgreSQL-backed turn/event history."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: asyncpg.Pool | None = None

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(self._database_url, min_size=1, max_size=5)
        async with self._pool.acquire() as conn:
            await conn.execute(MIGRATE_SQL)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def append_history(self, game_id: str, record: dict[str, Any]) -> None:
        assert self._pool is not None
        event_type = record.get("event", "unknown")
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO game_history (game_id, event_type, payload)
                VALUES ($1::uuid, $2, $3::jsonb)
                """,
                game_id,
                event_type,
                json.dumps(record),
            )

    async def get_history(self, game_id: str) -> list[dict[str, Any]]:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT payload FROM game_history
                WHERE game_id = $1::uuid
                ORDER BY id ASC
                """,
                game_id,
            )
        result: list[dict[str, Any]] = []
        for row in rows:
            payload = row["payload"]
            if isinstance(payload, str):
                result.append(json.loads(payload))
            else:
                result.append(dict(payload))
        return result

    async def delete_history(self, game_id: str) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM game_history WHERE game_id = $1::uuid",
                game_id,
            )
