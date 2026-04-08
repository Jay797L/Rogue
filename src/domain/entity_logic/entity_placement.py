# src/domain/features/entity_placement/entity_placer.py
import logging
from typing import Any, TypeVar

from domain.base.core.character import Character
from domain.base.utils.point import Point
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Character)


class EntityPlacer:
    """Утилита для удобного создания и размещения сущностей на карте."""

    def __init__(self, map_manager: MapManager):
        self.map_manager = map_manager

    def place(self, entity_or_class: type[T] | T, point: Point, **kwargs: Any) -> T:
        """
        Создаёт или принимает уже созданную сущность и размещает её на карте.
        """
        if not self.map_manager.is_empty(point):
            logger.warning(
                f"Клетка {point} уже занята: {self.map_manager[point]}, пропускаем"
            )
            # Возвращаем entity даже если не разместили, чтобы не ломать логику
            if isinstance(entity_or_class, type):
                return entity_or_class(**kwargs)
            return entity_or_class

        # Если передан класс — создаём экземпляр, иначе — используем переданный экземпляр
        if isinstance(entity_or_class, type):
            entity = entity_or_class(**kwargs)
        else:
            entity = entity_or_class
            if kwargs:
                for k, v in kwargs.items():
                    setattr(entity, k, v)

        if not hasattr(entity, "cell"):
            raise ValueError("Сущность не имеет атрибута 'cell'")

        entity.point = point
        self.map_manager[point] = entity.cell

        logger.info(
            f"Размещена {entity.__class__.__name__} '{getattr(entity, 'name', '')}' в точке {point}"
        )
        return entity

    def place_multiple(
        self, placements: list[tuple[type[Character], Point, dict[str, Any] | None]]
    ) -> list[Character]:
        """
        Размещает несколько сущностей за раз.

        Args:
            placements: Список кортежей (класс, точка, дополнительные_параметры)

        Returns:
            Список созданных сущностей
        """
        entities = []
        for entity_class, point, kwargs in placements:
            kwargs = kwargs or {}
            entity = self.place(entity_class, point, **kwargs)
            entities.append(entity)
        return entities

    def place_at_empty_nearby(
        self, entity_class: type[T], center: Point, max_radius: int = 5, **kwargs: Any
    ) -> T | None:
        """
        Ищет ближайшую свободную клетку вокруг center и размещает там сущность.

        Args:
            entity_class: Класс сущности
            center: Центр поиска
            max_radius: Максимальный радиус поиска
            **kwargs: Атрибуты сущности

        Returns:
            Размещённая сущность или None, если свободное место не найдено
        """
        for dy in range(-max_radius, max_radius + 1):
            for dx in range(-max_radius, max_radius + 1):
                candidate = Point(center.y + dy, center.x + dx)
                if self.map_manager.is_empty(candidate):
                    return self.place(entity_class, candidate, **kwargs)
        logger.warning(
            f"Не найдено свободной клетки вокруг {center} (радиус {max_radius})"
        )
        return None
