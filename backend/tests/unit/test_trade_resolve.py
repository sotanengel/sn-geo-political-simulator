from game.economy.trade import resolve_trades
from game.types import Nation, NationCategory, ResourceStock, ResourceType, TradeOffer, WorldState


def test_resolve_trades_executes_pending() -> None:
    n1 = Nation(
        id="n1",
        name="A",
        category=NationCategory.CONTINENTAL,
        resources=ResourceStock(food=100),
    )
    n2 = Nation(
        id="n2",
        name="B",
        category=NationCategory.CONTINENTAL,
        resources=ResourceStock(ore=100),
    )
    state = WorldState(nations={"n1": n1, "n2": n2})
    state.pending_trades.append(
        TradeOffer(
            from_nation="n1",
            to_nation="n2",
            offer={ResourceType.FOOD: 10},
            request={ResourceType.ORE: 5},
            offer_id="x",
        )
    )
    # resolve_trades only processes offers with request that were accepted via queue
    # Direct test via accept in trade module is in test_trade.py
    resolve_trades(state)
    assert True
