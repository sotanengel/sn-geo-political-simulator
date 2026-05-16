from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.schemas import ActionRequest, CreateGameRequest, GameStateResponse, GameSummary
from app.services.game_service import game_service

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameSummary)
async def create_game(request: CreateGameRequest) -> GameSummary:
    return await game_service.create_game(request)


@router.get("/{game_id}", response_model=GameStateResponse)
async def get_game(game_id: str) -> GameStateResponse:
    state = await game_service.get_game(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    return state


@router.delete("/{game_id}")
async def delete_game(game_id: str) -> dict[str, bool]:
    ok = await game_service.delete_game(game_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"deleted": True}


@router.post("/{game_id}/actions", response_model=GameStateResponse)
async def submit_action(game_id: str, action: ActionRequest) -> GameStateResponse:
    state = await game_service.submit_action(game_id, action)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    return state


@router.get("/{game_id}/state", response_model=GameStateResponse)
async def get_state(game_id: str) -> GameStateResponse:
    return await get_game(game_id)


@router.get("/{game_id}/history")
async def get_history(game_id: str) -> list[dict]:
    history = await game_service.get_history(game_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return history


@router.get("/{game_id}/observation/{nation_id}")
async def get_observation(game_id: str, nation_id: str) -> dict:
    obs = await game_service.get_observation(game_id, nation_id)
    if not obs:
        raise HTTPException(status_code=404, detail="Game or nation not found")
    return obs


class RLActionRequest(BaseModel):
    action: ActionRequest


@router.post("/{game_id}/rl-action/{nation_id}", response_model=GameStateResponse)
async def submit_rl_action(
    game_id: str, nation_id: str, body: RLActionRequest
) -> GameStateResponse:
    body.action.nation_id = nation_id
    return await submit_action(game_id, body.action)


@router.get("/{game_id}/events")
async def game_events(game_id: str) -> EventSourceResponse:
    loaded = await game_service.get_game(game_id)
    if not loaded:
        raise HTTPException(status_code=404, detail="Game not found")

    queue = game_service.subscribe(game_id)

    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {"event": "message", "data": json.dumps(event)}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
        except asyncio.CancelledError:
            return

    return EventSourceResponse(event_generator())
