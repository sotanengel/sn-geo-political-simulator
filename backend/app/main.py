import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.api.v1 import config as config_api
from app.api.v1 import games
from app.config import settings
from app.logging_config import configure_json_logging
from app.services.game_service import GameService
from app.stores.factory import build_store, close_store

configure_json_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = await build_store(settings)
    app.state.store = store
    app.state.game_service = GameService(store)
    logger.info("game_engine_started use_memory_store=%s", settings.use_memory_store)
    yield
    await close_store(store)
    logger.info("game_engine_stopped")


app = FastAPI(title="Geo-Political Simulator", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router, prefix="/api/v1")
app.include_router(config_api.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
