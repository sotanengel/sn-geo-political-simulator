from fastapi import APIRouter

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
