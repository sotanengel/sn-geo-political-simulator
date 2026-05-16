from __future__ import annotations

from typing import Any

from app.stores.serialization import (
    deserialize_extra,
    deserialize_state,
    serialize_extra,
    serialize_state,
)
from game.types import WorldState


class MemoryStore:
    """In-memory game state store (unit tests and local dev)."""

    def __init__(self) -> None:
        self._games: dict[str, dict[str, Any]] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}

    async def save_state(self, game_id: str, state: WorldState, extra: dict[str, Any]) -> None:
        self._games[game_id] = {
            "state": serialize_state(state),
            "extra": serialize_extra(extra),
        }

    async def load_state(self, game_id: str) -> tuple[WorldState, dict[str, Any]] | None:
        entry = self._games.get(game_id)
        if not entry:
            return None
        return deserialize_state(entry["state"]), deserialize_extra(entry["extra"])

    async def delete_game(self, game_id: str) -> None:
        self._games.pop(game_id, None)
        self._history.pop(game_id, None)

    async def game_exists(self, game_id: str) -> bool:
        return game_id in self._games

    async def append_history(self, game_id: str, record: dict[str, Any]) -> None:
        self._history.setdefault(game_id, []).append(record)

    async def get_history(self, game_id: str) -> list[dict[str, Any]]:
        return list(self._history.get(game_id, []))
