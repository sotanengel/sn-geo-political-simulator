from game.types import Nation, NationCategory
from game.victory.presets import evaluate_victory, score_territory
from game.types import WorldState


def test_largest_territory_wins() -> None:
    state = WorldState(
        nations={
            "a": Nation(id="a", name="A", category=NationCategory.CONTINENTAL, territory={"1", "2", "3"}),
            "b": Nation(id="b", name="B", category=NationCategory.CONTINENTAL, territory={"4"}),
        }
    )
    winners = evaluate_victory(state, "largest_territory")
    assert winners == ["a"]


def test_survival() -> None:
    state = WorldState(
        nations={
            "a": Nation(id="a", name="A", category=NationCategory.CONTINENTAL, territory={"1"}),
            "b": Nation(id="b", name="B", category=NationCategory.CONTINENTAL, territory=set(), is_extinct=True),
        }
    )
    winners = evaluate_victory(state, "survival")
    assert winners == ["a"]


def test_score_territory() -> None:
    n = Nation(id="a", name="A", category=NationCategory.CONTINENTAL, territory={"x", "y"})
    assert score_territory(n) == 2
