import logging
import math

from domain.base.core.base_vision import BaseVision
from domain.base.core.character import Character
from domain.base.core.pixel import Pixel
from domain.map.map_assembly.map_manager import MapManager
from domain.vision.stuff_for_3d.entity_renderer import EntityRenderer
from domain.vision.stuff_for_3d.minimap_renderer import MinimapRenderer
from domain.vision.stuff_for_3d.raycasting_engine import RaycastingEngine

logger = logging.getLogger(__name__)


class Pseudo3DVision(BaseVision):
    """
    Псевдо-3D вид + миникарта с туманом войны.
    Основной вид – 70x40 (raycasting), миникарта – 20x20 (справа).
    """

    SCREEN3D_WIDTH = 70
    SCREEN3D_HEIGHT = 40
    MAX_RENDER_DIST = 20
    FOV = math.pi / 3
    PLAYER_HEIGHT = 0.5

    MINIMAP_SIZE = 15
    MINIMAP_RADIUS = 7
    MINIMAP_X_OFFSET = 0
    MINIMAP_Y_OFFSET = 1

    def __init__(
        self,
        map_manager: MapManager,
        character_of_view: Character,
        minimap_vision: BaseVision,
        direction: int = 0,
        screen_width: int = 70,
        screen_height: int = 40,
    ):
        super().__init__(map_manager, character_of_view)
        self._direction = direction
        self._fog_vision = minimap_vision
        self._last_screen = None
        self._initialized = False

        self.SCREEN3D_WIDTH = max(40, screen_width)
        self.SCREEN3D_HEIGHT = max(20, screen_height)
        self.FOV = math.pi / 3

        self._raycaster = RaycastingEngine(
            map_manager, character_of_view, self.MAX_RENDER_DIST
        )
        self._entity_renderer = EntityRenderer(
            self.SCREEN3D_WIDTH, self.SCREEN3D_HEIGHT
        )
        self._minimap_renderer = MinimapRenderer(
            self.SCREEN3D_WIDTH, self.SCREEN3D_HEIGHT, direction
        )

        self.MINIMAP_SIZE = min(15, self.SCREEN3D_HEIGHT // 3, self.SCREEN3D_WIDTH // 4)
        self.MINIMAP_RADIUS = self.MINIMAP_SIZE // 2

        self.MINIMAP_X_OFFSET = 1
        self.MINIMAP_Y_OFFSET = 1

    def set_direction(self, direction: int):
        self._direction = direction
        self._minimap_renderer.set_direction(direction)
        self._initialized = False
        self._last_screen = None

    def update_screen_dimensions(self, width: int, height: int):
        """Обновляет размеры экрана без сброса исследованных клеток."""
        self.SCREEN3D_WIDTH = max(40, width)
        self.SCREEN3D_HEIGHT = max(20, height)

        self._entity_renderer.update_screen_dimensions(
            self.SCREEN3D_WIDTH, self.SCREEN3D_HEIGHT
        )
        self._minimap_renderer.update_screen_dimensions(
            self.SCREEN3D_WIDTH, self.SCREEN3D_HEIGHT
        )

        self.MINIMAP_SIZE = min(15, self.SCREEN3D_HEIGHT // 3, self.SCREEN3D_WIDTH // 4)
        self.MINIMAP_RADIUS = self.MINIMAP_SIZE // 2

        self.MINIMAP_X_OFFSET = 1
        self.MINIMAP_Y_OFFSET = 1

    def _get_player_angle(self) -> float:
        """Преобразует дискретное направление в радианы для raycasting."""
        angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        return angles[self._direction % 4]

    def take_all(self) -> list[Pixel]:
        """Генерирует 3D-вид + миникарту и возвращает общий список пикселей."""
        pixels = [*self._render_3d(), *self._render_minimap()]

        self._last_screen = pixels
        self._initialized = True
        return pixels

    def take_changes(self) -> list[Pixel]:
        """Возвращает изменения (всегда весь экран для простоты)."""
        if not self._initialized:
            return self.take_all()
        return self._last_screen if self._last_screen else []

    def _render_3d(self) -> list[Pixel]:
        """Генерирует пиксели для псевдо-3D вида (левая часть экрана) с сущностями."""
        pixels = []
        player = self.character_of_view
        px = player.point.x + 0.5
        py = player.point.y + 0.5
        angle = self._get_player_angle()

        start_angle = angle - self.FOV / 2
        angle_step = self.FOV / self.SCREEN3D_WIDTH

        entity_columns = {}
        entity_distances = {}
        entity_objects = {}

        for col in range(self.SCREEN3D_WIDTH):
            ray_angle = start_angle + col * angle_step
            distance, display_char, entity = self._raycaster.cast_ray(py, px, ray_angle)
            distance *= math.cos(ray_angle - angle)
            if distance <= 0:
                distance = 0.001

            # Always render the wall/floor/ceiling column
            self._raycaster.render_column(
                pixels,
                col,
                distance,
                display_char,
                self.SCREEN3D_WIDTH,
                self.SCREEN3D_HEIGHT,
            )

            # If there is an entity, collect it for later overlay rendering
            if entity is not None:
                self._entity_renderer.collect_entity_columns(
                    col,
                    distance,
                    entity,
                    entity_columns,
                    entity_distances,
                    entity_objects,
                )

        # Render all entities on top of the walls
        self._entity_renderer.render_entities(
            pixels, entity_columns, entity_distances, entity_objects
        )

        return pixels

    def _render_minimap(self) -> list[Pixel]:
        """Генерирует миникарту с поворотом в соответствии с направлением взгляда."""
        player = self.character_of_view
        explored_pixels = self._fog_vision.take_all()
        return self._minimap_renderer.render(
            [], player.point.y, player.point.x, explored_pixels
        )

    @property
    def get_cam(self) -> tuple[int, int]:
        """Центр экрана (используется для совместимости с GameView)."""
        return (self.SCREEN3D_HEIGHT // 2, self.SCREEN3D_WIDTH // 2)
