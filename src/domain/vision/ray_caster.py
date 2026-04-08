import logging
import math
from collections.abc import Callable

from domain.base.utils.point import Point
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)


class RaycastingVisibility:
    """
    Обработчик видимости с использованием сортировки по расстоянию и углам.

    Принцип работы:
    1. Получает все точки в квадратной области обзора
    2. Сортирует их по расстоянию от центра и по углу
    3. Последовательно проверяет видимость, учитывая блокирующие объекты
    """

    def __init__(self, map_manager: MapManager):
        """
        Инициализация обработчика видимости.

        Args:
            map_manager: Менеджер карты для проверки блокирующих клеток
        """
        self.map_manager = map_manager
        self._visible_cache: dict[tuple[int, int, int], set[Point]] = {}
        self._blocking_cache: dict[Point, bool] = {}

    def check_visibility(
        self,
        center: Point,
        target: Point,
        radius: int | None = None,
        blocking_callback: Callable[[Point], bool] | None = None,
        use_cache: bool = True,
    ) -> bool:
        """
        Backwards-compatible adapter: returns True if `target` is visible from `center`.
        If radius is not provided, uses integer ceil of euclidean distance.
        """
        if radius is None:
            distance = math.ceil(center.distance_float(target))
            radius = max(0, distance)

        visible = self.get_visible_cells(center, radius, blocking_callback, use_cache)
        return target in visible

    def get_visible_cells(
        self,
        center: Point,
        radius: int,
        blocking_callback: Callable[[Point], bool] | None = None,
        use_cache: bool = True,
    ) -> set[Point]:
        """
        Возвращает множество видимых клеток в радиусе от центра.

        Args:
            center: Центральная точка (позиция игрока)
            radius: Радиус обзора в клетках
            blocking_callback: Функция для проверки блокировки клетки.
                              Если не указана, использует стандартную проверку.
            use_cache: Использовать ли кэширование

        Returns:
            Множество видимых клеток
        """

        all_points = self._get_points_in_square(center, radius)

        if not all_points:
            return set()

        sorted_points = self._sort_points_by_distance_and_angle(center, all_points)

        visible_points = set()

        for point in sorted_points:
            if self._is_point_visible(center, point, visible_points, blocking_callback):
                visible_points.add(point)

        if use_cache:
            cache_key = (center.y, center.x, radius)
            self._visible_cache[cache_key] = visible_points

        logger.debug(
            f"Visible cells: {len(visible_points)}/{len(all_points)} for center={center}, radius={radius}"
        )
        return visible_points

    def _get_points_in_square(self, center: Point, radius: int) -> set[Point]:
        """
        Возвращает все точки в квадрате радиуса radius вокруг центра.

        Args:
            center: Центральная точка
            radius: Радиус (половина стороны квадрата)

        Returns:
            Множество точек в квадрате
        """
        points = set()
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dy == 0 and dx == 0:
                    continue

                y = center.y + dy
                x = center.x + dx
                point = Point(y, x)

                if point in self.map_manager:
                    points.add(point)

        return points

    def _sort_points_by_distance_and_angle(
        self, center: Point, points: set[Point]
    ) -> list[Point]:
        """
        Сортирует точки по расстоянию от центра и по углу.

        Сначала по расстоянию (ближе к центру), затем по углу.
        Это гарантирует, что при проверке видимости сначала обрабатываются
        ближайшие точки, что критично для raycasting.

        Args:
            center: Центральная точка
            points: Множество точек для сортировки

        Returns:
            Отсортированный список точек
        """

        def get_sort_key(point: Point) -> tuple[float, float]:
            dy = point.y - center.y
            dx = point.x - center.x

            distance = math.sqrt(dy * dy + dx * dx)

            angle = math.atan2(dy, dx)

            if angle < 0:
                angle += 2 * math.pi

            return (distance, angle)

        return sorted(points, key=get_sort_key)

    def _is_point_visible(
        self,
        center: Point,
        target: Point,
        visible_points: set[Point],
        blocking_callback: Callable[[Point], bool] | None = None,
    ) -> bool:
        """
        Проверяет видимость точки с учетом уже видимых точек.

        Использует алгоритм, проверяющий блокирующие клетки на линии между
        центром и целевой точкой.

        Args:
            center: Центральная точка
            target: Проверяемая точка
            visible_points: Уже видимые точки
            blocking_callback: Функция для проверки блокировки

        Returns:
            True если точка видима, иначе False
        """

        if blocking_callback:
            return blocking_callback(target)

        points_on_line = self._get_points_on_line(center, target)

        return all(not self._is_blocking(point) for point in points_on_line[1:-1])

    def _get_points_on_line(self, start: Point, end: Point) -> list[Point]:
        """
        Возвращает все точки на линии между start и end.

        Использует алгоритм Брезенхема для получения всех клеток на линии.

        Args:
            start: Начальная точка
            end: Конечная точка

        Returns:
            Список точек на линии (включая start и end)
        """
        points = []

        y0, x0 = start.y, start.x
        y1, x1 = end.y, end.x

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        sy = 1 if y0 < y1 else -1
        sx = 1 if x0 < x1 else -1

        err = dx - dy

        y, x = y0, x0

        while True:
            points.append(Point(y, x))

            if y == y1 and x == x1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points

    def _is_blocking(self, point: Point) -> bool:
        """Проверяет, блокирует ли клетка обзор."""

        if point in self._blocking_cache:
            return self._blocking_cache[point]

        try:
            cell = self.map_manager[point]
        except (KeyError, IndexError):
            self._blocking_cache[point] = False
            return False

        if cell is None:
            self._blocking_cache[point] = False
            return False

        is_blocking = False

        if (
            hasattr(cell, "blocking_vision")
            and cell.blocking_vision
            or hasattr(cell, "owner")
            and cell.owner is not None
            or hasattr(cell, "is_wall")
            and cell.is_wall
            or type(cell).__name__ == "WallCell"
        ):
            is_blocking = True

        else:
            is_blocking = False

        self._blocking_cache[point] = is_blocking
        return is_blocking

    def clear_cache(self):
        """
        Очищает кэши видимых клеток и блокировки.
        """
        self._visible_cache.clear()
        self._blocking_cache.clear()
        logger.debug("Raycasting cache cleared")

    def invalidate_point(self, point: Point):
        """
        Инвалидирует кэш для конкретной точки.

        Args:
            point: Точка, кэш которой нужно инвалидировать
        """
        if point in self._blocking_cache:
            del self._blocking_cache[point]

        self._visible_cache.clear()
        logger.debug(f"Cache invalidated for point {point}")

    def get_visible_cells_with_octants(
        self, center: Point, radius: int
    ) -> dict[int, set[Point]]:
        """
        Возвращает видимые клетки, сгруппированные по октантам (направлениям).

        Полезно для отладки и оптимизации.

        Args:
            center: Центральная точка
            radius: Радиус обзора

        Returns:
            Словарь {октант: множество видимых точек}
        """
        all_visible = self.get_visible_cells(center, radius, use_cache=True)
        visible_by_octant = {i: set() for i in range(8)}

        for point in all_visible:
            dy = point.y - center.y
            dx = point.x - center.x

            octant = self._get_octant(dy, dx)
            visible_by_octant[octant].add(point)

        return visible_by_octant

    def _get_octant(self, dy: int, dx: int) -> int:
        """
        Определяет октант для вектора (dy, dx).

        Октанты нумеруются от 0 до 7 по часовой стрелке.

        Args:
            dy: Разница по Y
            dx: Разница по X

        Returns:
            Номер октанта (0-7)
        """
        if dy == 0 and dx == 0:
            return 0

        angle = math.atan2(dy, dx)

        if angle < 0:
            angle += 2 * math.pi

        octant = int((angle + math.pi / 8) / (math.pi / 4)) % 8

        return octant
