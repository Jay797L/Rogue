import random

from domain.base.core.character import Character
from domain.base.utils.directions import ALL_DIRECTIONS
from domain.base.utils.point import Point
from domain.game.core.entity_logic.move_order import MoveOrder
from domain.map.map_assembly.map_manager import MapManager


class BaseBehavior:
    @staticmethod
    def base_attack(
        entity: Character,
        map_manager: MapManager,
        directions: list[Point] = ALL_DIRECTIONS,
    ) -> tuple[list, bool]:
        effects = []
        tried_to_attack = False
        difficulty = random.randint(0, 100)
        for direction in directions:
            check_point = entity.point + direction
            cell = map_manager[check_point]
            if cell and cell.owner and cell.owner.name == "player":
                tried_to_attack = True
                if difficulty < entity.dexterity:
                    effects.append(
                        entity.action.from_caster(entity).to_target(cell.owner).build()
                    )
        return effects, tried_to_attack

    @staticmethod
    def persecution(entity: Character, target: Point, map_manager: MapManager):
        if target is None:
            return None

        delta = target - entity.point
        step_y = 1 if delta.y > 0 else -1 if delta.y < 0 else 0
        step_x = 1 if delta.x > 0 else -1 if delta.x < 0 else 0

        if abs(delta.y) > abs(delta.x):
            selected_point = entity.point + Point(step_y, 0)
        elif abs(delta.x) > abs(delta.y):
            selected_point = entity.point + Point(0, step_x)
        else:
            selected_point = entity.point + (
                Point(step_y, 0) if random.choice([True, False]) else Point(0, step_x)
            )

        if map_manager.is_empty(selected_point):
            return MoveOrder(entity, selected_point)

    @staticmethod
    def ebluet(entity: Character, map_manager: MapManager) -> list[Point]:
        options = []
        for direction in ALL_DIRECTIONS:
            check_point = entity.point + direction
            if map_manager.is_empty(check_point):
                options.append(check_point)
        return options

    @staticmethod
    def update_target(entity: Character, player_point: Point, map_manager: MapManager):
        if entity.point == entity.target:
            entity.target = None
        if (
            entity.point.distance_float(player_point) < entity.scope
            and map_manager.ray_caster
            and map_manager.ray_caster.check_visibility(entity.point, player_point)
        ):
            entity.target = player_point
