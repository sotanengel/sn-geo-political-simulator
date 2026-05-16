from __future__ import annotations

import numpy as np

from game.economy.resources import apply_turn_production
from game.economy.trade import accept_trade, execute_gift, queue_trade_offer, resolve_trades
from game.military.invasion import resolve_invasion, tech_multiplier
from game.military.units import apply_maintenance, mark_extinct_nations, move_units
from game.types import (
    ActionType,
    GameAction,
    InvasionResult,
    ResourceType,
    TerrainType,
    WorldState,
)
from game.victory.presets import evaluate_victory
from game.world.h3_grid import are_adjacent
from game.world.movement import movement_cost


class TurnProcessor:
    def __init__(
        self,
        max_trades_per_turn: int = 5,
        food_per_unit: int = 1,
        fuel_per_unit: int = 1,
        tech_scale_factor: float = 0.1,
        victory_condition: str = "largest_territory",
        target_cells: int = 500,
    ) -> None:
        self.max_trades_per_turn = max_trades_per_turn
        self.food_per_unit = food_per_unit
        self.fuel_per_unit = fuel_per_unit
        self.tech_scale_factor = tech_scale_factor
        self.victory_condition = victory_condition
        self.target_cells = target_cells

    def start_turn(self, state: WorldState, rng: np.random.Generator) -> None:
        apply_turn_production(state)
        for nation in state.nations.values():
            if not nation.is_extinct:
                apply_maintenance(nation, self.food_per_unit, self.fuel_per_unit)

    def resolve_actions(
        self,
        state: WorldState,
        actions: list[GameAction],
        rng: np.random.Generator,
    ) -> None:
        gifts: list[GameAction] = []
        trades: list[GameAction] = []
        moves: list[GameAction] = []
        invades: list[GameAction] = []
        accepts: list[GameAction] = []

        for action in actions:
            nation = state.nations.get(action.nation_id)
            if not nation or nation.is_extinct:
                continue
            match action.action_type:
                case ActionType.GIFT:
                    gifts.append(action)
                case ActionType.TRADE_OFFER:
                    trades.append(action)
                case ActionType.TRADE_ACCEPT:
                    accepts.append(action)
                case ActionType.MOVE:
                    moves.append(action)
                case ActionType.INVADE:
                    invades.append(action)
                case _:
                    pass

        for action in gifts:
            execute_gift(state, action)

        for action in trades:
            queue_trade_offer(state, action)

        for action in accepts:
            if action.trade_offer_id:
                accept_trade(state, action.trade_offer_id, action.nation_id)

        resolve_trades(state, self.max_trades_per_turn)

        for action in moves:
            self._resolve_move(state, action)

        for action in invades:
            self._resolve_invasion(state, action, rng)

        self._sync_ownership(state)
        mark_extinct_nations(state)

    def end_turn(self, state: WorldState) -> None:
        state.turn += 1
        if state.turn >= state.max_turns:
            state.game_over = True
            state.winners = evaluate_victory(
                state, self.victory_condition, self.target_cells
            )

    def _resolve_move(self, state: WorldState, action: GameAction) -> None:
        nation = state.nations[action.nation_id]
        if not action.source_cell or not action.target_cell:
            return
        if action.source_cell not in nation.territory:
            return
        if not are_adjacent(action.source_cell, action.target_cell):
            return

        from_t = state.cell_terrain.get(action.source_cell, TerrainType.LAND)
        to_t = state.cell_terrain.get(action.target_cell, TerrainType.LAND)
        cost = movement_cost(from_t, to_t) * action.units
        if not nation.resources.subtract(ResourceType.FUEL, cost):
            return
        move_units(nation, action.source_cell, action.target_cell, action.units)

    def _resolve_invasion(
        self,
        state: WorldState,
        action: GameAction,
        rng: np.random.Generator,
    ) -> None:
        attacker = state.nations[action.nation_id]
        if not action.source_cell or not action.target_cell:
            return
        if action.source_cell not in attacker.territory:
            return
        defender_id = state.cell_owner.get(action.target_cell)
        if not defender_id or defender_id == attacker.id:
            return
        if not are_adjacent(action.source_cell, action.target_cell):
            return

        attack_force = min(action.units, attacker.military_units.get(action.source_cell, 0))
        if attack_force < 1:
            return

        defender = state.nations[defender_id]
        defend_force = defender.military_units.get(action.target_cell, 0)

        from_t = state.cell_terrain.get(action.source_cell, TerrainType.LAND)
        to_t = state.cell_terrain.get(action.target_cell, TerrainType.LAND)
        sea_extra = 0
        if from_t != TerrainType.LAND or to_t != TerrainType.LAND:
            sea_extra = movement_cost(from_t, to_t)
        if not attacker.resources.subtract(ResourceType.FUEL, sea_extra):
            return

        result, atk_remain, def_remain = resolve_invasion(
            attack_force,
            defend_force,
            tech_multiplier(attacker.tech_investment, self.tech_scale_factor),
            tech_multiplier(defender.tech_investment, self.tech_scale_factor),
            rng,
        )

        if atk_remain > 0:
            attacker.military_units[action.source_cell] = (
                attacker.military_units.get(action.source_cell, 0) - attack_force + atk_remain
            )
            if attacker.military_units[action.source_cell] <= 0:
                del attacker.military_units[action.source_cell]
        else:
            attacker.military_units[action.source_cell] = (
                attacker.military_units.get(action.source_cell, 0) - attack_force
            )
            if attacker.military_units.get(action.source_cell, 0) <= 0:
                attacker.military_units.pop(action.source_cell, None)

        if def_remain > 0:
            defender.military_units[action.target_cell] = def_remain
        else:
            defender.military_units.pop(action.target_cell, None)

        if result == InvasionResult.SUCCESS:
            defender.territory.discard(action.target_cell)
            attacker.territory.add(action.target_cell)
            state.cell_owner[action.target_cell] = attacker.id
            attacker.military_units[action.target_cell] = atk_remain

    def _sync_ownership(self, state: WorldState) -> None:
        for nid, nation in state.nations.items():
            for cell in nation.territory:
                state.cell_owner[cell] = nid
