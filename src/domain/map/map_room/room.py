import random

from domain.base.utils.directions import DOWN, RIGHT, UP
from domain.base.utils.lines import generate_line_points
from domain.base.utils.point import Point
from domain.map.map_sector.sector import Sector


class Room:
    """Комната на карте."""

    def __init__(self, start_position: Point, height: int, width: int, sector: Sector):
        """Инициализирует комнату.

        Args:
            start_position: Начальная позиция (верхний левый угол)
            height: Высота комнаты
            width: Ширина комнаты

        """
        self.points = (
            start_position,
            start_position + Point(height, 0),
            start_position + Point(height, width),
            start_position + Point(0, width),
        )
        self.locked_walls: list[Point] = []
        self.sector = sector

    def get_bound(self) -> tuple[Point, Point]:
        return (self.points[0], self.points[2])

    def select_wall(self, direction: Point) -> list[Point]:
        """Выбирает стену комнаты по направлению.

        Args:
            direction: Направление стены

        Returns:
            Множество точек стены

        """
        self.add_locked_wall(direction)
        if direction == UP:
            ret = generate_line_points(
                self.points[0],
                self.points[3],
            )
        elif direction == RIGHT:
            ret = generate_line_points(
                self.points[3],
                self.points[2],
            )
        elif direction == DOWN:
            ret = generate_line_points(
                self.points[2],
                self.points[1],
            )
        else:
            ret = generate_line_points(
                self.points[1],
                self.points[0],
            )
        return list(ret)

    @property
    def random_point_inside(self) -> Point:
        """Выбирает случайную точку внутри комнаты."""

        y1 = self.points[0].y
        y2 = self.points[2].y
        x1 = self.points[0].x
        x2 = self.points[2].x
        y_min, y_max = min(y1, y2), max(y1, y2)
        x_min, x_max = min(x1, x2), max(x1, x2)

        y = random.randint(y_min + 1, y_max - 1) if y_max - y_min > 1 else y_min
        x = random.randint(x_min + 1, x_max - 1) if x_max - x_min > 1 else x_min

        return Point(y, x)

    @property
    def random_point_inside_padded(self) -> Point:
        """Выбирает случайную точку внутри комнаты."""

        y1 = self.points[0].y
        y2 = self.points[2].y
        x1 = self.points[0].x
        x2 = self.points[2].x
        y_min, y_max = min(y1, y2), max(y1, y2)
        x_min, x_max = min(x1, x2), max(x1, x2)

        y = random.randint(y_min + 2, y_max - 2) if y_max - y_min > 2 else y_min
        x = random.randint(x_min + 2, x_max - 2) if x_max - x_min > 2 else x_min

        return Point(y, x)

    @property
    def get_room_center(self) -> Point:
        """Возвращает центр комнаты."""
        points = self.points
        center_y = (points[0].y + points[2].y) // 2
        center_x = (points[0].x + points[2].x) // 2
        return Point(center_y, center_x)

    def sorted_wall_points(self, direction: Point) -> list[Point]:
        """Возвращает отсортированные точки стены."""
        wall_points = self.select_wall(direction)
        wall_points = sorted(wall_points, key=lambda p: p.x)
        wall_points = sorted(wall_points, key=lambda p: p.y)
        return wall_points

    def add_locked_wall(self, direction: Point) -> None:
        self.locked_walls.append(direction)

    def is_wall_free(self, direction: Point) -> bool:
        return direction not in self.locked_walls

    def get_all_corners(self) -> tuple[Point, Point, Point, Point]:
        return self.points

    def in_room(self, point: Point) -> bool:
        """Проверяет, находится ли точка внутри комнаты.

        Args:
            point: Проверяемая точка

        Returns:
            True, если точка внутри комнаты, иначе False
        """

        top_left = self.points[0]
        bottom_right = self.points[2]

        y_min = min(top_left.y, bottom_right.y)
        y_max = max(top_left.y, bottom_right.y)
        x_min = min(top_left.x, bottom_right.x)
        x_max = max(top_left.x, bottom_right.x)

        return (y_min < point.y < y_max) and (x_min < point.x < x_max)
