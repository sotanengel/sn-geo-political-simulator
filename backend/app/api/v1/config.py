from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas import GameConfigSchema

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/presets")
def list_presets() -> dict[str, list[str]]:
    return {
        "victory_conditions": [
            "largest_territory",
            "smallest_territory",
            "balance_enforcer",
            "target_score",
            "survival",
            "custom",
        ]
    }


class ValidateConfigRequest(BaseModel):
    config: GameConfigSchema


@router.post("/validate")
def validate_config(request: ValidateConfigRequest) -> dict[str, bool]:
    cfg = request.config
    valid = 2 <= cfg.h3_resolution <= 4 and 2 <= cfg.num_nations <= 32
    return {"valid": valid}
