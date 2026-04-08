"""Класс для отображения всей карты без тумана войны."""

import logging

from domain.base.core.base_vision import BaseVision
from domain.base.core.character import Character
from domain.base.core.pixel import Pixel
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)


class UnlimitVision(BaseVision):
    """Полный обзор карты без тумана войны (закрыт для модификации)."""

    @staticmethod
    def __init__(map_manager: MapManager, character_of_view: Character):
        super().__init__(map_manager, character_of_view)

    def _get_all_pixels(self) -> dict[tuple[int, int], Pixel]:
        """
        Получает все пиксели карты.

        Returns:
            Словарь всех пикселей {координата: пиксель}
        """
        movable_points, unmovable_points = self.map_manager.split_cells_by_owner()
        all_points = movable_points.union(unmovable_points)

        pixels = {}
        for point in all_points:
            cell = self.map_manager[point]
            y, x = point
            pixels[(y, x)] = Pixel(y, x, cell.content, cell.color)

        return pixels

    def take_all(self, force_refresh: bool = False) -> list[Pixel]:
        """
        Возвращает все пиксели (полный обзор карты).

        Args:
            force_refresh: Если True, принудительно обновляет данные даже если уже инициализирован

        Returns:
            Список всех пикселей на карте
        """
        current_pixels = self._get_all_pixels()
        self._update_screen_state(current_pixels)
        self._initialized = True
        self._log_state()

        return self.screen

    def take_changes(self) -> list[Pixel]:
        """Возвращает только изменившиеся пиксели."""
        if not self._initialized:
            return self.take_all()

        current_pixels = self._get_all_pixels()

        old_pixels = {(p.y, p.x): p for p in self.old_screen}

        changes = self._compute_changes(current_pixels, old_pixels)

        self._update_screen_state(current_pixels)

        if changes:
            logger.debug("Найдено {} изменений на всей карте", len(changes))
