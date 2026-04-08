from dataclasses import dataclass

from domain.base.utils.point import Point
from domain.game.core.entity_logic.enemy_manager import EnemyManager
from domain.game.core.entity_logic.entity_placement import EntityPlacer
from domain.map.map_assembly.map_layout import MapLayout
from domain.map.map_assembly.map_manager import MapManager


@dataclass
class Level:
    def __init__(
        self,
        map_layout: MapLayout,
        map_manager: MapManager,
        enemy_manager: EnemyManager,
        entity_placer: EntityPlacer,
        exit_point: Point,
    ):
        self.map_layout: MapLayout = map_layout
        self.map_manager: MapManager = map_manager
        self.enemy_manager: EnemyManager = enemy_manager
        self.entity_placer: EntityPlacer = entity_placer
        self.exit_point: Point = exit_point
