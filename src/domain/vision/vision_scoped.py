import logging

from domain.base.core.base_vision import BaseVision
from domain.base.core.character import Character
from domain.base.core.pixel import Pixel
from domain.base.utils.point import Point
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)


class ScopedVision(BaseVision):
    """Вижн с ограниченным радиусом обзора (scope)."""

    def __init__(self, map_manager: MapManager, character_of_view: Character):
        super().__init__(map_manager, character_of_view)
        self._last_visible_cells: set[Point] = set()
        self._raycaster = None

    def _get_visible_cells(self) -> set[Point]:
        """
        Возвращает множество клеток, видимых персонажем,
        с учётом блокирующих объектов (рейкастинг).
        Всегда включает точку персонажа.
        """
        if self._raycaster:
            cells = self._raycaster.get_visible_cells(
                self.character_of_view.point, self.character_of_view.scope
            )
        else:
            cells = self.map_manager.get_visible_cells(
                self.character_of_view.point, self.character_of_view.scope
            )

        result = set(cells)
        result.add(self.character_of_view.point)
        return result

    def _get_current_pixels(self) -> tuple[dict[tuple[int, int], Pixel], set[Point]]:
        """
        Получает текущие пиксели в области видимости.

        Returns:
            Кортеж (словарь пикселей, множество видимых точек)
        """
        visible_points = self._get_visible_cells()
        current_pixels = {}

        for point in visible_points:
            cell = self.map_manager[point]
            if cell:
                y, x = point
                current_pixels[(y, x)] = Pixel(y, x, cell.content, cell.color)

        return current_pixels, visible_points

    def take_all(self) -> list[Pixel]:
        """Возвращает все видимые пиксели."""
        current_pixels, visible_points = self._get_current_pixels()

        visible_tuples = {(p.y, p.x) for p in visible_points}
        self._update_screen_state(current_pixels, visible_tuples)
        self._last_visible_cells = visible_points
        self._initialized = True
        self._log_state()

        return self.screen

    def take_changes(self) -> list[Pixel]:
        """Возвращает изменившиеся пиксели в пределах видимости."""
        if not self._initialized:
            return self.take_all()

        current_pixels, visible_points = self._get_current_pixels()

        old_pixels = {(p.y, p.x): p for p in self.old_screen}

        changes = self._compute_changes(current_pixels, old_pixels)

        visible_tuples = {(p.y, p.x) for p in visible_points}
        self._update_screen_state(current_pixels, visible_tuples)
        self._last_visible_cells = visible_points

        if changes:
            logger.debug("Найдено {} изменений в области видимости", len(changes))
