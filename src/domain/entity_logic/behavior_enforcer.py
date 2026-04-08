from typing import Any

from domain.base.core.character import check_status_in_character
from domain.base.core.effect import Effect
from domain.base.data.entities import register_all_patterns
from domain.base.data.entities._collection_of_behaviors import (
    CollectionOfBehaviors,
)
from domain.base.data.entities.ghost import Ghost
from domain.base.data.entities.ogr import Ogr
from domain.base.data.entities.player import Player
from domain.base.data.entities.vampire import Vampire
from domain.base.data.entities.zombie import Zombie
from domain.base.utils.point import Point
from domain.entity_logic.enemy_mover import EnemyMover
from domain.map.map_assembly.map_manager import MapManager

register_all_patterns()


class BehaviorEnforcer:
    """Класс для применения поведения сущностей."""

    def __init__(self, map_manager: MapManager, player: Player | None = None):
        self.map_manager = map_manager
        self.player = player
        self.mover = EnemyMover(self.map_manager)

    def perform_live_tick(
        self, entity: Ogr | Ghost | Vampire | Zombie
    ) -> list[Any | Effect]:
        """
        Выполняет поведение для живого существа (врага).

        Args:
            entity: Сущность (враг)

        Returns:
            Список эффектов от поведения
        """
        if self.player:
            if check_status_in_character(entity, "stun"):
                return []

            move_order, effects = CollectionOfBehaviors.think_over(
                entity, self.player.point, self.map_manager
            )
            if move_order:
                self.mover.perform(move_order)
            return effects
        return []

    def perform_player_behavior(self, direction: Point) -> list[Any | Effect]:
        """
        Выполняет поведение для игрока.

        Args:
            direction: Направление движения

        Returns:
            Список эффектов от действия игрока
        """
        if self.player:
            # Импортируем AI игрока
            if check_status_in_character(self.player, "stun"):
                return []
            move_order, effects = CollectionOfBehaviors.think_over(
                self.player, direction, self.map_manager
            )
            if move_order:
                self.mover.perform(move_order)
            return effects
        return []
