"""Базовый класс для всех видов отображения карты."""

import logging
from abc import ABC, abstractmethod

from domain.base.core.character import Character
from domain.base.core.pixel import Pixel
from domain.base.data.colors import COLORS
from domain.base.utils.point import Point
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)


class BaseVision(ABC):
    """Абстрактный базовый класс для отображения карты."""

    def __init__(
        self,
        map_manager: MapManager,
        character_of_view: Character,
    ):
        """Инициализирует базового смотрителя

        Args:
            map_manager: Менеджер карты
            character_of_view: Персонаж, от лица которого ведется обзор

        """
        self.map_manager: MapManager = map_manager
        self.character_of_view: Character = character_of_view
        self.reminder: list[Pixel] = []
        self.tracked: list[Pixel] = []
        self.screen: list[Pixel] = []
        self.old_screen: list[Pixel] = []
        self._initialized = False

        map_cells = len(self.map_manager._content) if self.map_manager else 0
        logger.info(
            f"Инициализация {self.__class__.__name__}: "
            f"map_cells={map_cells}, "
            f"player_pos={self.character_of_view.point if self.character_of_view else None}"
        )

    @property
    def get_cam(self):
        return (self.character_of_view.point.y, self.character_of_view.point.x)

    @staticmethod
    @abstractmethod
    def take_changes() -> list[Pixel]:
        pass

    @staticmethod
    @abstractmethod
    def take_all() -> list[Pixel]:
        pass

    def __call__(self):
        return self.take_all()

    def _get_pixels_from_points(
        self, points: set[tuple[int, int]]
    ) -> dict[tuple[int, int], Pixel]:
        """
        Преобразует множество координат в словарь пикселей.

        Args:
            points: Множество координат (y, x)

        Returns:
            Словарь {координата: пиксель}
        """
        pixels = {}
        for y, x in points:
            cell = self.map_manager[Point(y, x)]
            pixels[(y, x)] = Pixel(y, x, str(cell.content), int(cell.color))
        return pixels

    def _classify_pixels(
        self, pixels: dict[tuple[int, int], Pixel]
    ) -> tuple[list[Pixel], list[Pixel]]:
        """
        Классифицирует пиксели на статические (reminder) и динамические (tracked).

        Args:
            pixels: Словарь пикселей {координата: пиксель}

        Returns:
            Кортеж (reminder, tracked)
        """
        reminder = []
        tracked = []

        for (y, x), pixel in pixels.items():
            cell = self.map_manager[Point(y, x)]
            if cell.owner is not None:
                tracked.append(pixel)
            else:
                reminder.append(pixel)

        return reminder, tracked

    @classmethod
    def _compute_changes(
        cls,
        current_pixels: dict[tuple[int, int], Pixel],
        old_pixels: dict[tuple[int, int], Pixel],
    ) -> list[Pixel]:
        """
        Вычисляет изменения между двумя состояниями экрана.

        Args:
            current_pixels: Текущие пиксели {координата: пиксель}
            old_pixels: Предыдущие пиксели {координата: пиксель}

        Returns:
            Список измененных пикселей (новые, удаленные, измененные)
        """
        changes = []
        for coord, current_pixel in current_pixels.items():
            old_pixel = old_pixels.get(coord)

            if old_pixel is None:
                changes.append(current_pixel)
                logger.debug(f"Новый пиксель на {coord}: {current_pixel.content}")
            elif cls._check_entity_changed(old_pixel, current_pixel):
                changes.append(current_pixel)
                logger.debug(
                    f"Изменен пиксель на {coord}: {old_pixel.content} -> {current_pixel.content}"
                )
        for coord, old_pixel in old_pixels.items():
            if coord not in current_pixels:
                changes.append(Pixel(old_pixel.y, old_pixel.x, " ", COLORS.BLACK))
                logger.debug(f"Удален пиксель на {coord}")
        return changes

    def _update_screen_state(
        self,
        current_pixels: dict[tuple[int, int], Pixel],
        visible_points: set[tuple[int, int]] | None = None,
    ) -> None:
        """
        Обновляет состояние экрана (screen, old_screen, reminder, tracked).

        Args:
            current_pixels: Текущие пиксели
            visible_points: Множество видимых точек (опционально, для классификации)
        """
        self.screen = list(current_pixels.values())
        self.old_screen = self.screen.copy()

        self.reminder, self.tracked = self._classify_pixels(current_pixels)

    @staticmethod
    def _check_entity_changed(old_pixel: Pixel | None, new_pixel: Pixel | None) -> bool:
        """
        Проверяет, изменилась ли сущность.

        Args:
            old_pixel: Предыдущий пиксель
            new_pixel: Новый пиксель

        Returns:
            True если сущность изменилась, иначе False
        """
        if old_pixel is None and new_pixel is None:
            return False
        if old_pixel is None or new_pixel is None:
            return True
        return (
            old_pixel.content != new_pixel.content or old_pixel.color != new_pixel.color
        )

    @staticmethod
    def _is_empty_pixel(pixel: Pixel) -> bool:
        """
        Проверяет, является ли пиксель пустым.

        Args:
            pixel: Проверяемый пиксель

        Returns:
            True если пиксель пустой
        """
        return pixel.content == " " and pixel.color == COLORS.BLACK

    def _log_state(self) -> None:
        """Логирует текущее состояние вижна (для отладки)."""
        logger.debug(
            f"{self.__class__.__name__} состояние: "
            f"screen={len(self.screen)}, "
            f"reminder={len(self.reminder)}, "
            f"tracked={len(self.tracked)}, "
            f"initialized={self._initialized}"
        )
