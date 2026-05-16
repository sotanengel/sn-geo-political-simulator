import logging

from fastapi import FastAPI

from app.logging_config import configure_json_logging

configure_json_logging()
logger = logging.getLogger(__name__)
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.api.v1 import games, config as config_api

app = FastAPI(title="Geo-Political Simulator", version="0.1.0")
logger.info("game_engine_started")

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
