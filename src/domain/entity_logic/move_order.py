from domain.base.core.character import Character
from domain.base.utils.point import Point


class MoveOrder:
    def __init__(self, movable_entity: Character, target_point: Point) -> None:
        self.movable_entity = movable_entity
        self.target_point = target_point
