
from app.map_encoding import build_map_cells, build_observation_payload
from game.types import Nation, NationCategory, TerrainType, WorldState
from game.world.h3_grid import get_all_cells


def _minimal_state() -> WorldState:
    cells = get_all_cells(1)[:4]
    c0, c1, c2, c3 = cells
    return WorldState(
        turn=1,
        max_turns=10,
        nations={
            "nation_0": Nation(
                id="nation_0",
                name="A",
                category=NationCategory.CONTINENTAL,
                territory={c0, c1},
            ),
            "nation_1": Nation(
                id="nation_1",
                name="B",
                category=NationCategory.ISLAND,
                territory={c2},
            ),
        },
        cell_terrain={
            c0: TerrainType.LAND,
            c1: TerrainType.LAND,
            c2: TerrainType.SHALLOW_SEA,
            c3: TerrainType.DEEP_SEA,
        },
        cell_owner={
            c0: "nation_0",
            c1: "nation_0",
            c2: "nation_1",
        },
        land_cells={c0, c1, c2},
        resolution=1,
    )


def test_build_map_cells_includes_terrain_and_owner() -> None:
    cells = build_map_cells(_minimal_state())
    state = _minimal_state()
    owned = next(iter(state.nations["nation_0"].territory))
    unowned = next(c for c in state.cell_terrain if c not in state.cell_owner)
    by_h3 = {c["h3"]: c for c in cells}
    assert by_h3[owned]["owner_id"] == "nation_0"
    assert by_h3[owned]["terrain"] == "LAND"
    assert by_h3[unowned]["owner_id"] is None


def test_build_observation_payload_shapes() -> None:
    state = _minimal_state()
    payload = build_observation_payload(state, "nation_0")
    assert len(payload["map"]) == 64
    assert len(payload["map"][0]) == 8
    assert len(payload["nation_resources"]) == 16
    assert payload["own_resources"]["FOOD"] == 0
    assert payload["own_category"] == "CONTINENTAL"
    assert any(v > 0 for row in payload["map"] for v in row)
