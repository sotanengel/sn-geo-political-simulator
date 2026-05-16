from __future__ import annotations

import uuid

from game.types import ActionType, GameAction, ResourceType, TradeOffer, WorldState
from game.economy.resources import transfer_resources


def create_trade_offer(action: GameAction) -> TradeOffer:
    if action.trade is None:
        raise ValueError("Trade action requires trade payload")
    return TradeOffer(
        from_nation=action.nation_id,
        to_nation=action.trade.to_nation,
        offer=dict(action.trade.offer),
        request=dict(action.trade.request),
        offer_id=str(uuid.uuid4()),
    )


def resolve_trades(state: WorldState, max_trades_per_turn: int = 5) -> None:
    """Execute accepted trades and gifts during resolution phase."""
    trade_counts: dict[str, int] = {nid: 0 for nid in state.nations}

    remaining_offers: list[TradeOffer] = []
    for offer in state.pending_trades:
        if trade_counts.get(offer.from_nation, 0) >= max_trades_per_turn:
            remaining_offers.append(offer)
            continue

        from_n = state.nations.get(offer.from_nation)
        to_n = state.nations.get(offer.to_nation)
        if not from_n or not to_n or from_n.is_extinct or to_n.is_extinct:
            continue

        if not offer.request:
            # Gift path handled separately
            remaining_offers.append(offer)
            continue

        if transfer_resources(from_n.resources, to_n.resources, offer.offer):
            transfer_resources(to_n.resources, from_n.resources, offer.request)
            trade_counts[offer.from_nation] = trade_counts.get(offer.from_nation, 0) + 1

    state.pending_trades = remaining_offers


def execute_gift(state: WorldState, action: GameAction) -> bool:
    if action.trade is None:
        return False
    from_n = state.nations.get(action.nation_id)
    to_n = state.nations.get(action.trade.to_nation)
    if not from_n or not to_n or from_n.is_extinct or to_n.is_extinct:
        return False
    return transfer_resources(from_n.resources, to_n.resources, action.trade.offer)


def queue_trade_offer(state: WorldState, action: GameAction) -> None:
    offer = create_trade_offer(action)
    state.pending_trades.append(offer)


def accept_trade(state: WorldState, offer_id: str, acceptor_nation: str) -> bool:
    for i, offer in enumerate(state.pending_trades):
        if offer.offer_id == offer_id and offer.to_nation == acceptor_nation:
            from_n = state.nations[offer.from_nation]
            to_n = state.nations[offer.to_nation]
            if transfer_resources(from_n.resources, to_n.resources, offer.offer):
                transfer_resources(to_n.resources, from_n.resources, offer.request)
                state.pending_trades.pop(i)
                return True
    return False
