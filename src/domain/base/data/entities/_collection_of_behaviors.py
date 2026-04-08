from __future__ import annotations

import logging
import typing
from collections.abc import Callable

from domain.base.core.base_behavior import BaseBehavior
from domain.base.core.effect import Effect
from domain.game.core.entity_logic.move_order import MoveOrder
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)


class CollectionOfBehaviors:
    _strategies: dict[str, Callable] = {}

    @classmethod
    def register_strategy(cls, entity_type: str) -> typing.Callable:
        def decorator(func: Callable):
            cls._strategies[entity_type] = staticmethod(func)
            return func

        return decorator

    @classmethod
    def think_over(
        cls, entity: "Character", player_point: "Point", map_manager: MapManager
    ) -> tuple[MoveOrder | None, list[Effect]]:
        entity_type = type(entity).__name__
        strategy = cls._strategies.get(entity_type)

        if strategy is None:
            message = f"Unsupported type: {entity_type}. Strategy not found"
            logger.error(message)
            raise TypeError(message)
        if entity.name == "player":
            return strategy(entity, player_point, map_manager)
        BaseBehavior.update_target(entity, player_point, map_manager)

        return strategy(entity, entity.target, map_manager)
