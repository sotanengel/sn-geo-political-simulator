from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NationSnapshot:
    id: str
    territory: set[str] = field(default_factory=set)
    is_extinct: bool = False


@dataclass
class TerritorySnapshot:
    nations: dict[str, NationSnapshot]
    total_land_cells: int = 1
