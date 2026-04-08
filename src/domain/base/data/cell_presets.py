"""Пресеты для создания клеток на карте."""

from dataclasses import dataclass

from domain.base.core.cell import Cell
from domain.base.data.colors import COLORS


@dataclass
class WallCell(Cell):
    """Стена."""

    content: str = "#"
    blocking_vision: bool = True
    memorable: bool = True
    color: COLORS = COLORS.WHITE


@dataclass
class HallwayCell(Cell):
    """Коридор."""

    content: str = "#"
    blocking_vision: bool = True
    memorable: bool = True
    color: COLORS = COLORS.WHITE


@dataclass
class DoorCell(Cell):
    """Дверь."""

    content: str = "D"
    blocking_vision: bool = True
    memorable: bool = True
    color: COLORS = COLORS.WHITE


@dataclass
class GlassCell(Cell):
    """Стекло"""

    content: str = "▢"
    blocking_vision: bool = False
    memorable: bool = True
    color: COLORS = COLORS.WHITE


@dataclass
class ExitCell(Cell):
    content: str = "E"
    blocking_vision: bool = False
    memorable: bool = True
    color: COLORS = COLORS.MAGNETA


@dataclass
class EatCell(Cell):
    content: str = "+"


@dataclass
class ElixirCell(Cell):
    content: str = "^"


@dataclass
class ScrollCell(Cell):
    content: str = "?"


@dataclass
class WeaponCell(Cell):
    content: str = "&"


@dataclass
class TreasureCell(Cell):
    content: str = "$"


@dataclass
class KeyCell(Cell):
    content: str = "k"
    blocking_vision: bool = False
    memorable: bool = True
    color: COLORS = COLORS.YELLOW


@dataclass
class LockedDoorCell(DoorCell):
    door_id: str = ""
    content: str = "D"
    color: COLORS = COLORS.RED
