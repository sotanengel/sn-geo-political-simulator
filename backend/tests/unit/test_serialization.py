from game.types import ActionType, GameAction, Nation, NationCategory, ResourceStock, WorldState
from app.stores.serialization import (
    deserialize_extra,
    deserialize_state,
    pack_game_blob,
    serialize_extra,
    serialize_game_action,
    serialize_state,
    unpack_game_blob,
)


def test_state_round_trip() -> None:
    state = WorldState(
        turn=1,
        max_turns=10,
        nations={
            "nation_0": Nation(
                id="nation_0",
                name="A",
                category=NationCategory.ISLAND,
                territory={"c1", "c2"},
                resources=ResourceStock(food=10),
            )
        },
        land_cells={"c1", "c2"},
    )
    restored = deserialize_state(serialize_state(state))
    assert restored.turn == 1
    assert restored.nations["nation_0"].resources.food == 10
    assert restored.land_cells == {"c1", "c2"}


def test_extra_with_game_action() -> None:
    action = GameAction(nation_id="nation_0", action_type=ActionType.PASS)
    extra = {"pending_actions": {"nation_0": action}, "submitted": {"nation_0": True}}
    blob = serialize_extra(extra)
    restored = deserialize_extra(blob)
    assert restored["pending_actions"]["nation_0"].action_type == ActionType.PASS


def test_pack_unpack_blob() -> None:
    state = WorldState(turn=0, max_turns=5)
    extra = {"submitted": {}}
    blob = pack_game_blob(state, extra)
    s2, e2 = unpack_game_blob(blob)
    assert s2.max_turns == 5
    assert e2["submitted"] == {}


def test_serialize_game_action() -> None:
    data = serialize_game_action(GameAction(nation_id="n1", action_type=ActionType.INVADE, units=3))
    assert data["action_type"] == "INVADE"
    assert data["units"] == 3
