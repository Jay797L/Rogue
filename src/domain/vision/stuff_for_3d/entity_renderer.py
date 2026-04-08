"""Module for rendering entities in pseudo-3D view."""

from typing import Any

from domain.base.core.pixel import Pixel
from domain.base.data.colors import COLORS
from domain.vision.stuff_for_3d.ascii_art_renderer import ASCIIArtRenderer


class EntityRenderer:
    """Handles rendering of entities in 3D view."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

    @staticmethod
    def collect_entity_columns(
        col: int,
        distance: float,
        entity: Any,
        entity_columns: dict,
        entity_distances: dict,
        entity_objects: dict,
    ) -> None:
        """Collect entity columns for later rendering."""
        if entity is None:
            return
        uid = entity.uid
        if uid not in entity_columns:
            entity_columns[uid] = []
            entity_distances[uid] = distance
            entity_objects[uid] = entity
        entity_columns[uid].append(col)

    def render_entities(
        self,
        pixels: list[Pixel],
        entity_columns: dict,
        entity_distances: dict,
        entity_objects: dict,
    ) -> None:
        """Render all collected entities onto the pixel buffer."""
        entities_to_render = []

        for uid, columns in entity_columns.items():
            entity = entity_objects[uid]
            distance = entity_distances[uid]

            center_col = sum(columns) // len(columns)

            # Базовый размер арта в зависимости от расстояния
            if distance < 2:
                base_art_height = 5
            elif distance < 4:
                base_art_height = 4
            elif distance < 6:
                base_art_height = 3
            else:
                base_art_height = 2

            # Применяем масштабирование
            scale = self._calculate_scale_by_distance(distance)
            art_height = max(1, int(base_art_height * scale))
            art_width = max(2, art_height * 2)

            entity_art = ASCIIArtRenderer.get_art(
                entity, max_height=art_height, max_width=art_width
            )

            if entity_art:
                # Обрезаем крайние пробелы и получаем информацию о смещении
                trimmed_art, left_trims = self._trim_art_spaces(entity_art)
                
                actual_height = len(trimmed_art)
                actual_width = (
                    max(len(line) for line in trimmed_art) if trimmed_art else 1
                )

                # Вычисляем y_offset с учетом расстояния
                y_offset = self._calculate_floor_y_offset(distance, actual_height)
                # Базовое смещение по X
                x_offset = center_col - (actual_width // 2)

                entities_to_render.append(
                    {
                        "x_offset": x_offset,
                        "distance": distance,
                        "art": trimmed_art,
                        "left_trims": left_trims,
                        "entity": entity,
                        "art_width": actual_width,
                        "art_height": actual_height,
                        "y_offset": y_offset,
                    }
                )

                continue
            
            # Для fallback-символов
            entity_height = max(1, int(3 * scale))
            y_offset = self._calculate_floor_y_offset(distance, entity_height)
            
            entities_to_render.append(
                {
                    "distance": distance,
                    "symbol": self._get_entity_symbol(entity),
                    "entity": entity,
                    "height": entity_height,
                    "y_offset": y_offset,
                    "is_art": False,
                    "col": center_col,
                }
            )

        entities_to_render.sort(key=lambda e: e["distance"], reverse=True)

        for entity_data in entities_to_render:
            self._render_single_entity(pixels, entity_data)

    def _calculate_scale_by_distance(self, distance: float) -> float:
        """
        Вычисляет коэффициент масштабирования в зависимости от расстояния.
        
        Args:
            distance: Расстояние до объекта
            
        Returns:
            float: Коэффициент масштабирования (MIN_SCALE - MAX_SCALE)
        """
        return 1.0
        MAX_SCALE = 3.0  # Максимальный масштаб для объектов вплотную
        MIN_SCALE = 1.0  # Минимальный масштаб (100%)
        SCALE_DISTANCE = 4.0  # Расстояние, на котором масштаб становится минимальным
        
        if distance <= 0:
            return MAX_SCALE
        
        # Линейная интерполяция между MAX_SCALE и MIN_SCALE
        scale = MAX_SCALE - (min(distance, SCALE_DISTANCE) / SCALE_DISTANCE) * (MAX_SCALE - MIN_SCALE)
        
        return max(MIN_SCALE, scale)

    def _calculate_floor_y_offset(self, distance: float, object_height: int) -> int:
        """
        Вычисляет вертикальную позицию объекта так, чтобы он стоял на полу.
        
        Близкие объекты (distance ~ 0) находятся внизу экрана.
        Далекие объекты (distance ~ MAX_RENDER_DIST) находятся около горизонта.
        Горизонт находится примерно на 60% высоты экрана (уровень глаз).
        
        Args:
            distance: Расстояние до объекта
            object_height: Высота объекта в символах
            
        Returns:
            int: Y-координата верхнего левого угла объекта
        """
        # Константы для настройки перспективы
        HORIZON_RATIO = 0.6  # Горизонт на 60% высоты экрана
        MAX_VISIBLE_DISTANCE = 5.0  # Максимальная дистанция отрисовки сущностей
        
        # Нормализуем дистанцию (0 = близко, 1 = далеко)
        normalized_dist = min(distance, MAX_VISIBLE_DISTANCE) / MAX_VISIBLE_DISTANCE
        
        # Вычисляем позицию пола для данной дистанции
        horizon_y = int(self.screen_height * HORIZON_RATIO)
        
        # Для distance=0 объект в самом низу, для distance=max - на горизонте
        floor_y = int(horizon_y + (self.screen_height - horizon_y) * (1 - normalized_dist))
        
        # Корректируем с учетом высоты объекта
        y_offset = floor_y - object_height
        
        # Убеждаемся, что объект не выходит за пределы экрана
        return max(0, min(y_offset, self.screen_height - object_height))

    def _trim_art_spaces(self, art: list[str]) -> tuple[list[str], list[int]]:
        """
        Обрезает крайние пробелы и возвращает информацию о смещении.
        
        "  # #  " -> (["# #"], left_trim=2)
        "   W   " -> (["W"], left_trim=3)
        "  @ @  " -> (["@ @"], left_trim=2)
        
        Args:
            art: Список строк арта
            
        Returns:
            tuple: (обрезанные строки, список смещений для каждой строки)
        """
        trimmed_lines = []
        left_trims = []
        
        for line in art:
            # Находим количество пробелов слева
            left_trim = len(line) - len(line.lstrip())
            # Обрезаем пробелы справа
            stripped = line.rstrip()
            
            if stripped:
                trimmed_lines.append(stripped)
                left_trims.append(left_trim)
            else:
                # Пустые строки пропускаем
                continue
                
        return trimmed_lines, left_trims

    def _render_single_entity(self, pixels: list[Pixel], entity_data: dict) -> None:
        """Render a single entity."""
        entity = entity_data["entity"]
        color = self._get_entity_color(entity)

        if "art" in entity_data:
            self._render_art_entity(pixels, entity_data, color)
        else:
            self._render_symbol_entity(pixels, entity_data, color)

    def _render_art_entity(
        self, pixels: list[Pixel], entity_data: dict, color: int
    ) -> None:
        """Render entity as ASCII art with smart space handling."""
        art = entity_data["art"]
        left_trims = entity_data.get("left_trims", [])
        y_offset = entity_data["y_offset"]
        x_offset = entity_data["x_offset"]

        for row_idx, line in enumerate(art):
            y = y_offset + row_idx
            if not 0 <= y < self.screen_height:
                continue
                
            # Получаем оригинальное смещение слева для этой строки
            original_left_trim = left_trims[row_idx] if row_idx < len(left_trims) else 0
            
            for col_idx, char in enumerate(line):
                # Вычисляем реальную X координату с учетом оригинальных левых пробелов
                # Пробелы влияют на позицию, но не рисуются и не затирают
                x = x_offset + col_idx + original_left_trim
                
                if not 0 <= x < self.screen_width:
                    continue
                    
                if char == " ":
                    # Внутренние пробелы (не крайние) - затирают пол
                    # Крайние пробелы уже удалены, так что это именно внутренние пробелы
                    for i, pixel in enumerate(pixels):
                        if pixel.y == y and pixel.x == x:
                            pixels.pop(i)
                            break
                    continue
                    
                # Не пробел - рисуем символ сущности
                replaced = False
                for i, pixel in enumerate(pixels):
                    if pixel.y == y and pixel.x == x:
                        pixels[i] = Pixel(y, x, char, color)
                        replaced = True
                        break
                if not replaced:
                    pixels.append(Pixel(y, x, char, color))

    def _render_symbol_entity(
        self, pixels: list[Pixel], entity_data: dict, color: int
    ) -> None:
        """Render entity as single symbol (fallback)."""
        symbol = entity_data.get("symbol", "?")
        y_offset = entity_data["y_offset"]
        col = entity_data["col"]
        height = entity_data["height"]

        for row in range(height):
            y = y_offset + row
            if 0 <= y < self.screen_height:
                replaced = False
                for i, pixel in enumerate(pixels):
                    if pixel.y == y and pixel.x == col:
                        pixels[i] = Pixel(y, col, symbol, color)
                        replaced = True
                        break
                if not replaced:
                    pixels.append(Pixel(y, col, symbol, color))

    @staticmethod
    def _get_entity_symbol(entity) -> str:
        """Return symbol for entity in 3D."""
        if hasattr(entity, "cell") and hasattr(entity.cell, "content"):
            return entity.cell.content
        return "?"

    @staticmethod
    def _get_entity_color(entity) -> int:
        """Return color for entity in 3D."""
        if hasattr(entity, "cell") and hasattr(entity.cell, "color"):
            if isinstance(entity.cell.color, int):
                return entity.cell.color
            if hasattr(entity.cell.color, "value"):
                return entity.cell.color.value
        if hasattr(entity, "name"):
            name = entity.name.lower()
            if "elite" in name:
                return COLORS.RED
            if "boss" in name:
                return COLORS.MAGNETA

        return COLORS.WHITE

    def update_screen_dimensions(self, width: int, height: int) -> None:
        """Update screen dimensions."""
        self.screen_width = width
        self.screen_height = height