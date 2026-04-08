import random
import time


class MapGenProp:
    """Свойства генерации карты."""

    def __init__(
        self,
        seed: int = time.time(),
        min_room_height: int = 7,
        min_room_width: int = 7,
        max_sector_height: int = 27,
        max_sector_width: int = 35,
        sector_pedding: int = 5,
        door_pedding: int = 3,
        hallway_depth: int = 1,
        chance_for_expansion: float = 0.5,
        min_dead_ends: int = 0,
        max_dead_ends: int = 3,
        dead_end_chance: float = 0.3,
        dead_end_min_length: int = 2,
        dead_end_max_length: int = 5,
        dead_end_chamber_size: int = 2,
        dead_end_branch_chance: float = 0.3,
        scaler: float = 1,
        map_scale: float | None = None,
        enemies_at_level: int = 4,
        items_at_level: int = 1,
    ):
        """Инициализирует свойства генерации.

        Args:
            seed: Сид для генерации
            min_room_height: Минимальная высота комнаты
            min_room_width: Минимальная ширина комнаты
            max_sector_height: Максимальная высота сектора
            max_sector_width: Максимальная ширина сектора
            sector_pedding: Отступ сектора
            door_pedding: Отступ для дверей
            corridor_turn_pedding: Отступ для поворота коридора
            chance_for_expansion: Вероятность расширения коридора
            min_dead_ends: Минимальное количество тупиков на карту
            max_dead_ends: Максимальное количество тупиков на карту
            dead_end_chance: Вероятность создания тупика от точки коридора
            dead_end_min_length: Минимальная длина тупикового коридора
            dead_end_max_length: Максимальная длина тупикового коридора
            dead_end_chamber_size: Размер камеры в тупике
            dead_end_branch_chance: Вероятность ветвления тупика
            scaler: Масштаб (для обратной совместимости)
            map_scale: Новый безопасный масштаб (приоритет выше scaler)
            enemies_at_level: Количество врагов на уровне
            items_at_level: Количество предметов на уровне

        """
        self.seed = seed

        scale = map_scale if map_scale is not None else scaler
        safe_scale = min(scale, 2.0)

        self._min_room_height = max(3, int(min_room_height * safe_scale))
        self._min_room_width = max(3, int(min_room_width * safe_scale))
        self._max_sector_height = int(
            max(
                max_sector_height * safe_scale,
                (min_room_height + 2 * sector_pedding) * safe_scale,
            )
        )
        self._max_sector_width = int(
            max(
                max_sector_width * safe_scale,
                (min_room_width + 2 * sector_pedding) * safe_scale,
            )
        )
        self.sector_pedding = int(sector_pedding * safe_scale)
        self.door_pedding = int(door_pedding * safe_scale)
        self.chance_for_expansion = chance_for_expansion
        self.hallway_depth = int(hallway_depth * safe_scale)

        self.min_dead_ends = int(min_dead_ends * safe_scale)
        self.max_dead_ends = int(max_dead_ends * safe_scale)
        self.dead_end_chance = dead_end_chance
        self.dead_end_min_length = int(dead_end_min_length * safe_scale)
        self.dead_end_max_length = int(dead_end_max_length * safe_scale)
        self.dead_end_chamber_size = int(dead_end_chamber_size * safe_scale)
        self.dead_end_branch_chance = dead_end_branch_chance

        self.enemies_at_level = enemies_at_level
        self.items_at_level = items_at_level

    @property
    def min_room_height(self) -> int:
        """Возвращает минимальную высоту комнаты."""
        return self._min_room_height

    @property
    def min_room_width(self) -> int:
        """Возвращает минимальную ширину комнаты."""
        return self._min_room_width

    @property
    def sector_height(self) -> int:
        """Генерирует случайную высоту сектора."""
        min_val = self._min_room_height + 2 * self.sector_pedding
        return random.randint(min_val, self._max_sector_height)

    @property
    def sector_width(self) -> int:
        """Генерирует случайную ширину сектора."""
        min_val = self._min_room_width + 2 * self.sector_pedding
        return random.randint(min_val, self._max_sector_width)
