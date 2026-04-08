import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from domain.base.core.cell import Cell
from domain.base.utils.point import Point

logger = logging.getLogger(__name__)


class MapManager:
    """Менеджер для управления клетками с X/Y индексацией."""

    def __init__(self) -> None:
        """Инициализирует пустую карту."""
        self._content: dict[Point, Cell] = {}
        self._x_index: dict[int, set[Point]] = defaultdict(set)
        self._y_index: dict[int, set[Point]] = defaultdict(set)
        self.ray_caster = None

    def is_empty(self, position: Point) -> bool:
        """Проверяет, пуста ли позиция."""
        empty = position not in self._content
        logger.debug("is_empty({}) -> {}", position, empty)
        return empty

    def __contains__(self, position: Point) -> bool:
        return position in self._content

    def __getitem__(self, position: Point) -> Cell | None:
        if self.is_empty(position=position):
            logger.debug("__getitem__({}) -> None", position)
            return None
        return self._content[position]

    def __setitem__(self, position: Point, cell: Cell) -> None:
        """Устанавливает клетку в позицию с обновлением индексов."""
        existed = position in self._content
        if existed:
            old_cell = self._content[position]
            logger.warning(
                "Overwriting cell at {}: {} -> {}",
                position,
                old_cell.__class__.__name__,
                cell.__class__.__name__,
            )
            self._remove_from_indices(position)
        else:
            logger.debug("Setting new cell {} at {}", cell.__class__.__name__, position)

        self._content[position] = cell
        self._add_to_indices(position)

    def __delitem__(self, position: Point) -> None:
        """Удаляет клетку из указанной позиции."""
        if position in self._content:
            cell = self._content[position]
            logger.debug("Deleting cell {} at {}", cell.__class__.__name__, position)
            self._remove_from_indices(position)
            del self._content[position]
        else:
            logger.debug("Attempted to delete non-existent cell at {}", position)

    def _add_to_indices(self, position: Point) -> None:
        """Добавляет точку в индексы."""
        self._x_index[position.x].add(position)
        self._y_index[position.y].add(position)

    def _remove_from_indices(self, position: Point) -> None:
        """Удаляет точку из индексов."""
        self._x_index[position.x].discard(position)
        self._y_index[position.y].discard(position)

    def move_cell(self, from_position: Point | None, to_position: Point | None) -> bool:
        """Перемещает клетку из одной позиции в другую."""
        if from_position is None or to_position is None:
            logger.warning(
                "move_cell called with None arguments: from={}, to={}",
                from_position,
                to_position,
            )
            return False

        if from_position not in self._content:
            logger.debug("move_cell failed: from_position {} is empty", from_position)
            return False

        if to_position in self._content:
            logger.debug(
                "move_cell failed: target position {} is occupied by {}",
                to_position,
                self._content[to_position].__class__.__name__,
            )
            return False

        cell = self._content.pop(from_position)
        self._remove_from_indices(from_position)
        self._add_to_indices(to_position)
        self._content[to_position] = cell

        logger.debug(
            "Moved {} from {} to {}",
            cell.__class__.__name__,
            from_position,
            to_position,
        )
        return True

    def get_non_empty_points_in_rect(
        self, min_y: int, min_x: int, max_y: int, max_x: int
    ) -> list[Point]:
        """Возвращает список непустых точек в прямоугольнике."""
        rect_size = (max_x - min_x + 1) * (max_y - min_y + 1)
        logger.debug(
            "Searching non-empty points in rect: y[{}..{}], x[{}..{}] (area={})",
            min_y,
            max_y,
            min_x,
            max_x,
            rect_size,
        )

        if (max_x - min_x) < (max_y - min_y):
            result = self._search_by_x(min_x, max_x, min_y, max_y)
        else:
            result = self._search_by_y(min_x, max_x, min_y, max_y)

        logger.debug("Found {} non-empty points in rect", len(result))
        return result

    def _search_by_x(
        self, min_x: int, max_x: int, min_y: int, max_y: int
    ) -> list[Point]:
        """Поиск с использованием X индекса."""
        candidates: set[Point] = set()
        for x in range(min_x, max_x + 1):
            if x in self._x_index:
                candidates.update(self._x_index[x])
        return [p for p in candidates if min_y <= p.y <= max_y]

    def _search_by_y(
        self, min_x: int, max_x: int, min_y: int, max_y: int
    ) -> list[Point]:
        """Поиск с использованием Y индекса."""
        candidates: set[Point] = set()
        for y in range(min_y, max_y + 1):
            if y in self._y_index:
                candidates.update(self._y_index[y])
        return [p for p in candidates if min_x <= p.x <= max_x]

    @property
    def all_points(self) -> set[Point]:
        """Возвращает все точки на карте."""
        return set(self._content)

    def get_bounds(self) -> tuple[int, int, int, int]:
        """Возвращает границы карты (min_y, min_x, max_y, max_x)."""
        if not self._content:
            return (0, 0, 0, 0)

        points = self._content.keys()
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)

        return (min_y, min_x, max_y, max_x)

    def split_cells_by_owner(self) -> tuple[set[Point], set[Point]]:
        """
        Разделяет клетки на имеющих owner и не имеющих.

        Returns:
            tuple: (точки_с_owner, точки_без_owner)
            Каждый элемент - множество точек Point
        """
        cells_with_owner = set()
        cells_without_owner = set()

        for point, cell in self._content.items():
            if hasattr(cell, "owner") and cell.owner is not None:
                cells_with_owner.add(point)
            else:
                cells_without_owner.add(point)

        return cells_with_owner, cells_without_owner

    def get_visible_cells(self, character_position: Point, scope: int) -> set[Point]:
        visible = set()
        for y in range(character_position.y - scope, character_position.y + scope + 1):
            for x in range(
                character_position.x - scope, character_position.x + scope + 1
            ):
                point = Point(y, x)
                if point in self._content:
                    visible.add(point)
        return visible

    def save_snapshot(self, filename: str, description: str = "") -> None:
        """Сохраняет снимок карты в файл для отладки."""

        debug_dir = Path("debug_snapshots")
        debug_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_filename = f"{filename}"
        filepath = debug_dir / safe_filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Map Snapshot: {filename}\n")
            f.write(f"# Time: {timestamp}\n")
            f.write(f"# Description: {description}\n")
            f.write(f"# Total cells: {len(self._content)}\n")
            f.write("\n")

            if not self._content:
                f.write("# Empty map\n")
                return

            bounds = self.get_bounds()
            min_y, min_x, max_y, max_x = bounds
            f.write(f"# Bounds: y={min_y}..{max_y}, x={min_x}..{max_x}\n\n")

            for y in range(min_y, max_y + 1):
                line = ""
                for x in range(min_x, max_x + 1):
                    point = Point(y, x)
                    if point in self._content:
                        cell = self._content[point]
                        content = cell.content if hasattr(cell, "content") else "?"
                        if hasattr(cell, "owner") and cell.owner is not None:
                            owner_name = getattr(cell.owner, "name", "unknown")
                            if len(owner_name) > 1:
                                line += owner_name[0].upper()
                            else:
                                line += content
                        else:
                            line += content
                    else:
                        line += " "
                f.write(line + "\n")

        logger = logging.getLogger(__name__)
        logger.info("Map snapshot saved to {}", filepath)
