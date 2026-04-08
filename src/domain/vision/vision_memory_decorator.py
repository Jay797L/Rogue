import logging
from typing import Any

import domain.base.core.pixel
from domain.base.core.base_vision import BaseVision
from domain.base.core.pixel import Pixel

logger = logging.getLogger(__name__)


class VisionMemoryDecorator(BaseVision):
    """
    Декоратор, добавляющий память об исследованных клетках.

    Оборачивает любой BaseVision и запоминает все клетки, которые когда-либо были видны.
    take_all() возвращает: текущие видимые клетки + всё, что было исследовано ранее.
    take_changes() возвращает изменения только для текущего вида.
    """

    def __init__(self, inner_vision: BaseVision):

        self._wrapped = inner_vision
        self.explored_cells: dict[tuple[int, int], Pixel] = {}
        logger.info("[VisionMemoryDecorator] ИНИЦИАЛИЗАЦИЯ, explored_cells пуст")

    def __getattr__(self, name: str) -> list[Any | domain.base.core.pixel.Pixel]:
        return getattr(self._wrapped, name)

    def __dir__(self):
        return sorted(set(super().__dir__() + dir(self._wrapped)))

    def take_all(self) -> list[Pixel]:
        """
        Возвращает все видимые клетки + всё, что было исследовано ранее.
        """
        logger.debug(
            f"[take_all] ВХОД: explored_cells={len(self.explored_cells)}, tracked={len(self.tracked) if hasattr(self, 'tracked') else 0}"
        )

        for pixel in self.tracked:
            if pixel in self.explored_cells.values():
                del self.explored_cells[pixel.y, pixel.x]

        current_visible = self._wrapped.take_all()

        for pixel in current_visible:
            self.explored_cells[(pixel.y, pixel.x)] = pixel

        self._initialized = True

        logger.debug(f"[take_all] ВЫХОД: explored_cells={len(self.explored_cells)}")
        return list(self.explored_cells.values())

    def take_changes(self) -> list[Pixel]:
        """
        Возвращает изменения только для текущего вида.
        """
        logger.debug(
            f"[take_changes] ВХОД: explored_cells={len(self.explored_cells)}, initialized={self._initialized}"
        )

        if not self._initialized:
            logger.debug("[take_changes] не инициализирован -> take_all")
            return self.take_all()

        current_changes = self._wrapped.take_changes()

        for pixel in current_changes:
            if (
                not self._is_empty_pixel(pixel)
                or (pixel.y, pixel.x) in self.explored_cells
            ):
                self.explored_cells[(pixel.y, pixel.x)] = pixel

        logger.debug(
            f"[take_changes] ВЫХОД: explored_cells={len(self.explored_cells)}, changes={len(current_changes)}"
        )
        return current_changes

    @property
    def explored_count(self) -> int:
        return len(self.explored_cells)

    def clear_explored(self):
        logger.warning(
            f"[clear_explored] ВЫЗВАН! explored_cells был {len(self.explored_cells)}"
        )
        self.explored_cells.clear()
        self._initialized = False
