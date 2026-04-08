from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from domain.base.core.base_effect import IEffectGenerator
from domain.base.core.cell import Cell
from domain.base.utils.point import Point


@dataclass(eq=False, frozen=False)
class Entity:
    name: str = "Unnamed"
    point: Point = field(default_factory=lambda: Point(0, 0))
    cell: Cell = field(default_factory=Cell)
    action: IEffectGenerator | None = None
    art = None
    uid: uuid.UUID = field(default_factory=uuid.uuid4, init=False, compare=True)
    strength: int = 0

    def __hash__(self) -> int:
        return hash(self.uid)

    def __eq__(self, other: Entity) -> bool:
        if not hasattr(other, "uid"):
            return NotImplemented
        return self.uid == other.uid

    def __post_init__(self):
        if hasattr(self, "cell") and hasattr(self.cell, "owner"):
            self.cell.owner = self
