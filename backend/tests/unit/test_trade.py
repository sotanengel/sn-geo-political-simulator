from game.economy.trade import execute_gift, queue_trade_offer, accept_trade
from game.types import (
    ActionType,
    GameAction,
    Nation,
    NationCategory,
    ResourceStock,
    ResourceType,
    TradeOffer,
    WorldState,
)


def _state() -> WorldState:
    n1 = Nation(
        id="n1",
        name="A",
        category=NationCategory.CONTINENTAL,
        resources=ResourceStock(food=100, ore=50),
    )
    n2 = Nation(
        id="n2",
        name="B",
        category=NationCategory.CONTINENTAL,
        resources=ResourceStock(food=10, ore=50),
    )
    return WorldState(nations={"n1": n1, "n2": n2})


def test_gift_transfer() -> None:
    state = _state()
    action = GameAction(
        nation_id="n1",
        action_type=ActionType.GIFT,
        trade=TradeOffer(
            from_nation="n1",
            to_nation="n2",
            offer={ResourceType.FOOD: 30},
            request={},
        ),
    )
    assert execute_gift(state, action)
    assert state.nations["n1"].resources.food == 70
    assert state.nations["n2"].resources.food == 40


def test_trade_accept() -> None:
    state = _state()
    offer = TradeOffer(
        from_nation="n1",
        to_nation="n2",
        offer={ResourceType.FOOD: 20},
        request={ResourceType.ORE: 10},
        offer_id="offer-1",
    )
    state.pending_trades.append(offer)
    assert accept_trade(state, "offer-1", "n2")
    assert state.nations["n1"].resources.food == 80
    assert state.nations["n2"].resources.ore == 40
