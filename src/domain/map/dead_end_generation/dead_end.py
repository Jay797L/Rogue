from dataclasses import dataclass

from domain.base.utils.point import Point


@dataclass
class DeadEnd:
    """Тупик (мертвый конец) в лабиринте."""

    room_id: int
    door: Point
    points: set[Point]
    direction: Point
