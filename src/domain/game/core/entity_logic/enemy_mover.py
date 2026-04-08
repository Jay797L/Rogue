import logging

from domain.game.core.entity_logic.move_order import MoveOrder
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)


class EnemyMover:
    def __init__(self, map_manager: MapManager) -> None:
        self.map_manager = map_manager
        if map_manager is None:
            logger.warning("Enemy mover create a map manager. Attantion")

    def perform(self, move_order: MoveOrder):

        entity = move_order.movable_entity
        current_point = entity.point
        target_point = move_order.target_point
        if current_point and self.map_manager[current_point] != entity.cell:
            self.map_manager[target_point] = entity.cell
            logger.debug(
                "Set {} (owner: {}) to {}",
                entity.cell.__class__.__name__,
                entity.__class__.__name__,
                target_point,
            )
        elif self.map_manager.move_cell(current_point, target_point):
            entity.point = target_point
            logger.debug(
                "Move {} (owner: {}) from {} to {}",
                entity.cell.__class__.__name__,
                entity.__class__.__name__,
                current_point,
                target_point,
            )
        else:
            message = "Try move something but some not existing"
            logger.error(message)
            raise ValueError(message)
