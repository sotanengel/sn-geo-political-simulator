from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.schemas import ActionRequest, CreateGameRequest, GameStateResponse, GameSummary
from app.services.game_service import GameService

router = APIRouter(prefix="/games", tags=["games"])


def _service(request: Request) -> GameService:
    return request.app.state.game_service


@router.post("", response_model=GameSummary)
async def create_game(request: Request, body: CreateGameRequest) -> GameSummary:
    return await _service(request).create_game(body)


@router.get("/{game_id}", response_model=GameStateResponse)
async def get_game(request: Request, game_id: str) -> GameStateResponse:
    state = await _service(request).get_game(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    return state


@router.delete("/{game_id}")
async def delete_game(request: Request, game_id: str) -> dict[str, bool]:
    ok = await _service(request).delete_game(game_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"deleted": True}


@router.post("/{game_id}/actions", response_model=GameStateResponse)
async def submit_action(request: Request, game_id: str, action: ActionRequest) -> GameStateResponse:
    state = await _service(request).submit_action(game_id, action)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    return state


@router.get("/{game_id}/state", response_model=GameStateResponse)
async def get_state(request: Request, game_id: str) -> GameStateResponse:
    return await get_game(request, game_id)


@router.get("/{game_id}/history")
async def get_history(request: Request, game_id: str) -> list[dict]:
    svc = _service(request)
    history = await svc.get_history(game_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return history


@router.get("/{game_id}/observation/{nation_id}")
async def get_observation(request: Request, game_id: str, nation_id: str) -> dict:
    obs = await _service(request).get_observation(game_id, nation_id)
    if not obs:
        raise HTTPException(status_code=404, detail="Game or nation not found")
    return obs


class RLActionRequest(BaseModel):
    action: ActionRequest


@router.post("/{game_id}/rl-action/{nation_id}", response_model=GameStateResponse)
async def submit_rl_action(
    request: Request,
    game_id: str,
    nation_id: str,
    body: RLActionRequest,
) -> GameStateResponse:
    body.action.nation_id = nation_id
    return await submit_action(request, game_id, body.action)


@router.get("/{game_id}/events")
async def game_events(request: Request, game_id: str) -> EventSourceResponse:
    svc = _service(request)
    loaded = await svc.get_game(game_id)
    if not loaded:
        raise HTTPException(status_code=404, detail="Game not found")

    queue = svc.subscribe(game_id)

    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {"event": "message", "data": json.dumps(event)}
                except TimeoutError:
                    yield {"event": "ping", "data": "{}"}
        except asyncio.CancelledError:
            return

    return EventSourceResponse(event_generator())
